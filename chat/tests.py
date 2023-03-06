from django.test import TestCase, Client
from django.urls import reverse_lazy
from .models import Profile, Thread, ChatMessage, User


class ViewsTestCase(TestCase):
    """ Тесткейс на представления """
    def setUp(self):
        self.client = Client()
        self.register_url = reverse_lazy('chat:register')
        self.login_url = reverse_lazy('chat:login')
        self.logout_url = reverse_lazy('chat:logout')
        self.main_url = reverse_lazy('chat:main_page')
        self.chat_url = reverse_lazy('chat:chat')
        self.change_status_url = reverse_lazy('chat:change_status')
        self.change_avatar_url = reverse_lazy('chat:change_avatar')
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_main_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.get(self.main_url)
        self.assertRedirects(response, self.chat_url)

    def test_main_not_authenticated(self):
        response = self.client.get(self.main_url)
        self.assertRedirects(response, self.login_url)

    def test_register_view(self):
        form_data = {
            'username': 'testuser2',
            'email': 'testuser2@test.com',
            'password1': 'testpassword123',
            'password2': 'testpassword123'
        }
        response = self.client.post(self.register_url, form_data)
        self.assertRedirects(response, self.chat_url)
        self.assertEqual(User.objects.filter(username='testuser2').count(), 1)

    def test_login_view(self):
        form_data = {
            'username': 'testuser',
            'password': 'testpassword'
        }
        response = self.client.post(self.login_url, form_data)
        self.assertRedirects(response, self.chat_url)

    def test_logout_view(self):
        self.client.force_login(self.user)
        response = self.client.get(self.logout_url)
        self.assertRedirects(response, self.login_url)

    def test_change_avatar_view(self):
        self.client.force_login(self.user)
        avatar_file = open('./media/avatars/default-avatar.png', 'rb')
        response = self.client.post(self.change_avatar_url, {'file': avatar_file}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertIn('url', response.json())
        self.assertTrue(Profile.objects.get(user=self.user).avatar)
        avatar_file.close()

    def test_change_status_view(self):
        self.client.force_login(self.user)
        response = self.client.post(self.change_status_url, {'new-status': 'test status'}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Profile.objects.get(user=self.user).status, 'test status')

    def test_chat_view(self):
        self.client.force_login(self.user)
        response = self.client.get(self.chat_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'chat/chat.html')


class ProfileModelTestCase(TestCase):
    """ Тесткейс на модель Profile """
    def setUp(self):
        self.user = User.objects.create_user(username='testuser1233453', password='testpass')
        
        # Получаем профиль пользоватлея, т.к он уже был создан с помощью django signals
        self.profile = Profile.objects.get(user=self.user)
        self.profile.status = 'Test Status'
        self.profile.save()

    def test_profile_creation(self):
        self.assertEqual(self.profile.user, self.user)
        self.assertEqual(self.profile.avatar.url, '/media/avatars/default-avatar.png')
        self.assertEqual(self.profile.status, 'Test Status')


class ThreadModelTestCase(TestCase):
    """ Тесткейс на Thread """
    def setUp(self):
        self.user1 = User.objects.create_user(username='testuser1', password='testpass')
        self.user2 = User.objects.create_user(username='testuser2', password='testpass')
        self.thread = Thread.objects.create(first_person=self.user1, second_person=self.user2)

    def test_thread_creation(self):
        self.assertEqual(self.thread.first_person, self.user1)
        self.assertEqual(self.thread.second_person, self.user2)


class ChatMessageModelTestCase(TestCase):
    """ Тесткейс на ChatMessage """
    def setUp(self):
        self.user1 = User.objects.create_user(username='testuser1', password='testpass')
        self.user2 = User.objects.create_user(username='testuser2', password='testpass')
        self.thread = Thread.objects.create(first_person=self.user1, second_person=self.user2)
        self.chat_message = ChatMessage.objects.create(thread=self.thread, user=self.user1, message='Test message')

    def test_chat_message_creation(self):
        self.assertEqual(self.chat_message.thread, self.thread)
        self.assertEqual(self.chat_message.user, self.user1)
        self.assertEqual(self.chat_message.message, 'Test message')
