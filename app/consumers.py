import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from db.models import Message, Meeting
from db.constants import MeetingStatusEnum
from django.utils import timezone


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.meeting_id = self.scope["url_route"]["kwargs"]["meeting_id"]
        self.room_group_name = f"chat_{self.meeting_id}"
        self.user = self.scope["user"]

        if not await self.is_allowed():
            await self.close()
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data["message"]
        sender = self.user.username

        message_save_res = await self.save_message(message)

        if message_save_res == 1:
            message = "Pasiekėte savo 200 žinučių limitą. Ši žinutė nebuvo išsiųsta."
            sender = "antivienas.lt"
        elif message_save_res == 2:
            message = "Jūsų žinutė nebuvo išsiųsta, nes viršijo 2000 simbolių limitą."
            sender = "antivienas.lt"
        elif message_save_res == 3:
            message = "Klaida: Nepavyko išsaugoti jūsų žinutės. Bandykite dar kartą."
            sender = "antivienas.lt"

        await self.channel_layer.group_send(
            self.room_group_name,
                {
                    "type": "chat_message",
                    "message": message,
                    "sender": sender,
                    "timestamp": timezone.now().isoformat(),
                }
            )


    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "sender": event["sender"],
            "timestamp": event["timestamp"],
        }))

    # ---------- DB METHODS ----------

    @database_sync_to_async
    def is_allowed(self):
        try:
            meeting = Meeting.objects.get(id=self.meeting_id)
            return (meeting.status == MeetingStatusEnum.CONFIRMED and self.user in (meeting.user, meeting.friend))
        except Meeting.DoesNotExist:
            return False

    @database_sync_to_async
    def save_message(self, content):
        
        meeting = Meeting.objects.get(id=self.meeting_id)
        messages = Message.objects.filter(meeting=meeting, sender=self.user).count()

        if messages > 200:
            return 1
        
        if len(content) > 2000:
            return 2
        
        try:
            Message.objects.create(
                meeting=meeting,
                sender=self.user,
                content=content
            )
            return 0
        except:
            return 3
