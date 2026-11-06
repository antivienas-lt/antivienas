import asyncio
import app.notifications as notifications
import os

NEW_USER_DC_ID = "1568228026301284442"
VERIFY_ID_DC_ID = "1568228066184921170"
MEETING_CONFIRMED_DC_ID = "1568228105368244286"
SEND_PAYMENT_DC_ID = "1568228143993720943"

async def _send_message(channel_id, message):
    intents = notifications.Intents.default()

    async with notifications.Client(intents=intents) as client:
        await client.login(os.environ["DISCORD_BOT_TOKEN"])
        channel = await client.fetch_channel(channel_id)
        await channel.send(message)
        await client.close()


def send_message(channel_id, message="Hello World! 👋"):
    asyncio.run(_send_message(channel_id, message))


def new_user_notification(message):
    send_message(NEW_USER_DC_ID, message)

def verify_id_request_notification(message):
    send_message(VERIFY_ID_DC_ID, message)

def meeting_confirmed_notification(message):
    send_message(MEETING_CONFIRMED_DC_ID, message)

def send_invoice_notification(message):
    send_message(SEND_PAYMENT_DC_ID, message)