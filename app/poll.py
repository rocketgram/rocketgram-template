from mybot import router
from rocketgram import context, commonfilters, ChatType, SendMessage, SendPoll, UpdateType


@router.handler
@commonfilters.chat_type(ChatType.private)
@commonfilters.command('/poll')
async def send_poll():
    """Shows how to send polls"""

    await SendPoll(context.user.user_id,
                   'Some question', ['Variant 1', 'Variant 2', 'Variant 3'],
                   allows_multiple_answers=True,
                   is_anonymous=False).send2()


@router.handler
@commonfilters.update_type(UpdateType.poll_answer)
async def answer():
    """Receives poll's answers"""

    await SendMessage(context.user.user_id,
                      f"Received answer for #{context.update.poll_answer.poll_id} - "
                      f"{context.update.poll_answer.option_ids}").send2()
