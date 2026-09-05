from django.db import transaction
from db.models import Meeting, Payment, MeetingStatusEnum


@transaction.atomic
def complete_meeting(meeting: Meeting) -> Meeting:
    if meeting.status == MeetingStatusEnum.COMPLETED:
        return meeting

    meeting.status = MeetingStatusEnum.COMPLETED
    meeting.save(update_fields=["status"])

    Payment.objects.get_or_create(
        meeting=meeting,
        defaults={
            "payer": meeting.friend,
            "payer_email": meeting.friend.email,
            "platform_fee": meeting.platform_fee,
        },
    )

    return meeting