import json

from .db_operations import get_user_avatar, get_user_threads, get_users_by_username, get_thread_messages,\
    save_message, get_or_create_thread, get_user_profile_info

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from chat.models import User


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):

        # Первая группа - группа чата. Вторая - личная для каждого пользователя.
        self.room_group_name = f"room_default"
        self.user_group = f"user_{self.scope['user']}"

        await self.channel_layer.group_add(self.user_group,self.channel_name)
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, exit_data):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        await self.channel_layer.group_discard(self.user_group, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        # Получение команды от вебсокета, которую нужно выполнить.
        command = text_data_json.get('command')

        if command == 'join':
            interlocutor = text_data_json.get('interlocutor')
            thread_id = await get_or_create_thread(self.scope['user'], interlocutor)
            profile_info = await get_user_profile_info(interlocutor)

            await self.change_chat_room(thread_id)
            messages = await get_thread_messages(thread_id)

            await self.channel_layer.group_send(
                self.user_group, {'type': 'get_messages', "messages": messages, "thread_id": thread_id, 'user_info': profile_info}
            )

        elif command == 'send_message':
            # Отправка сообщения
            message = text_data_json.get('message')
            author = self.scope["user"]
            other_user = await database_sync_to_async(User.objects.get)(id=text_data_json.get('interlocutor'))
            thread_id = await get_or_create_thread(author, other_user.id)

            # Сохранение написанного сообщения в базу данных
            await save_message(thread_id, author.id, message)
            author_avatar = await get_user_avatar(author)

            await self.channel_layer.group_send(
                self.room_group_name, {'type': 'send_message',
                                       'thread': thread_id,
                                       'message': message,
                                       'author': author.id, 
                                       'author_avatar': author_avatar}
            )
            
            # Обновление Threads пользователя. (Для переноса текущего Thread наверх)
            await self.channel_layer.group_send(self.user_group, {'type': 'get_threads'})
            await self.channel_layer.group_send(f"user_{other_user}", {'type': 'get_threads'})

        elif command == 'get_threads':
            # Получение всех чатов (Threads) пользователя
            await self.channel_layer.group_send(self.user_group, {'type': 'get_threads'})

        elif command == 'search':
            value = text_data_json.get('value')

            # Получение пользователей по запросу
            result = await get_users_by_username(self.scope['user'], value)

            await self.channel_layer.group_send(
                self.user_group, {'type': 'search_users', "result": result}
            )

        else:
            await self.send(json.dumps({
                'error': 'COMMAND_NOT_FOUND'
            }))

    async def change_chat_room(self, thread_id: int):
        """ Сменяет комнату чата """
        room = "chat_%s" % thread_id

        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        await self.channel_layer.group_add(room, self.channel_name)

        self.room_group_name = room

    """ 
    ------------------------------------ 
    Команды для обработки group send
    ------------------------------------ 
    """

    async def get_threads(self, event):
        threads = await get_user_threads(self.scope["user"])

        await self.send(text_data=json.dumps(
            {"command": "get_threads",
             "threads": threads}
        ))

    async def get_messages(self, event):
        await self.send(text_data=json.dumps(
            {"command": "join",
             "messages": event.get('messages'),
             'thread_id': event.get('thread_id'),
             'user_info': event.get('user_info')
             }))

    async def send_message(self, event):
        await self.send(text_data=json.dumps(
            {"command": "message",
             "message": event.get('message'),
             "author": event.get('author'),
             "author_avatar": event.get('author_avatar')}
        ))

    async def search_users(self, event):
        await self.send(text_data=json.dumps({
            "command": "search",
            "result": event.get('result')
        }))
