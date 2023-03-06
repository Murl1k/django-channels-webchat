from chat.models import User, Thread, ChatMessage
from channels.db import database_sync_to_async
from django.db.models import Q


@database_sync_to_async
def get_user_threads(user: User):
    """ Получает чаты, которые есть у пользователя """
    qs = Thread.objects.by_user(user=user).prefetch_related('chatmessage_thread').order_by('-updated')
    threads = []

    for thread in qs:
        if thread.first_person == user:
            interlocutor = thread.second_person
        else:
            interlocutor = thread.first_person

        # Создание одинакового списка, как в поиске, чтобы не делать новую функцию для показа собеседников.
        threads.append({
            'username': interlocutor.username,
            'user_avatar': interlocutor.profile.avatar.url,
            'user_status': interlocutor.profile.status,
            'id': interlocutor.id,
            'thread_id': thread.id
        })
    
    return threads


@database_sync_to_async
def save_message(thread_id: int, author_id: int, content: str):
    """ Сохраняет полученное сообщение от пользователя """
    thread = Thread.objects.filter(id=thread_id)
    author = User.objects.filter(id=author_id)

    if not thread.exists():
        print("Указанный Thread не найден!")
        return
    
    if not author.exists():
        print("Указанный пользователь не найден!")
        return
    
    ChatMessage.objects.create(thread=thread.first(), user=author.first(), message=content)
    

@database_sync_to_async
def get_thread_messages(thread_id: int):
    """ Получает сообщения в указанном чате """
    thread = Thread.objects.filter(id=thread_id)
    
    if thread.exists():
        thread = thread.first()
    else:
        return False

    messages = []

    for message_object in thread.chatmessage_thread.all().order_by('-pk'):

        messages.append({
            'user': {'id': message_object.user.pk,
                     'user_avatar': message_object.user.profile.avatar.url,
                     'username': message_object.user.username
                     },
            'message': message_object.message,
            'timestamp': str(message_object.timestamp)
        })
    
    return messages


@database_sync_to_async
def get_users_by_username(current_user: User, value: str):
    """ Получает пользователей по указанному запросу (регистр не важен)"""
    raw_data = User.objects.filter(username__istartswith=value).exclude(username=current_user)
    user_threads = Thread.objects.by_user(user=current_user)
    users = []

    for user in raw_data:
        user_thread = user_threads.filter(Q(first_person=user) | Q(second_person=user))
        if user_thread.exists():
            user_thread = user_thread.first().id
        else:
            user_thread = 'undefined'

        users.append(
            {'id': user.id,
             'user_avatar': user.profile.avatar.url,
             'user_status': user.profile.status,
             'username': user.username,
             'thread_id': user_thread
             }
        )

    return users


@database_sync_to_async
def get_or_create_thread(current_user: User, interlocutor_id: int):
    """ Создает или получает чат """
    second_person = User.objects.filter(id=interlocutor_id).first()
    qs = Thread.objects.by_user(user=current_user)

    for thread in qs:
        if second_person == thread.first_person or second_person == thread.second_person:
            thread_id = thread.id
            break
    else:
        thread_id = Thread.objects.create(first_person=current_user, second_person=second_person).id

    return thread_id


@database_sync_to_async
def get_user_profile_info(user_id: int):
    user = User.objects.get(pk=user_id)

    return {'username': user.username, 'avatar': user.profile.avatar.url, 'status': user.profile.status}


@database_sync_to_async
def get_user_avatar(user: User):
    return user.profile.avatar.url
