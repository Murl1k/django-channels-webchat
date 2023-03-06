from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.dispatch import receiver
from django.db.models.signals import post_save

User = get_user_model()


def user_avatar_path(instance, filename):
    return f"avatars/{instance.user.username}/{filename}"


class Profile(models.Model):
    """ Модель профиля для каждого пользователя """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to=user_avatar_path, default='avatars/default-avatar.png')
    status = models.CharField(max_length=50, blank=True, default='')

    def __str__(self):
        return f"{self.user} profile"


class ThreadManager(models.Manager):
    """ Менеджер объектов для Thread"""
    def by_user(self, **kwargs):
        user = kwargs.get('user')
        lookup = Q(first_person=user) | Q(second_person=user)
        qs = self.get_queryset().filter(lookup).distinct()
        return qs


class Thread(models.Model):
    """ Модель чата """
    first_person = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True,
                                     related_name='thread_first_person')
    second_person = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True,
                                      related_name='thread_second_person')
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = ThreadManager()

    class Meta:
        unique_together = ['first_person', 'second_person']


class ChatMessage(models.Model):
    """ Модель сообщения """
    thread = models.ForeignKey(Thread, null=True, blank=True, on_delete=models.CASCADE,
                               related_name='chatmessage_thread')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    # Создает профиль пользователя, когда пользователь регистрируется на сайте
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=ChatMessage)
def update_created_at(sender, instance, created, **kwargs):
    # Обновляет поле Thread updated на значение, когда было создано последнее сообщение
    if created:
        instance.thread.updated = instance.timestamp
        instance.thread.save()
