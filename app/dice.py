from mybot import router
from rocketgram import commonfilters, ChatType, SendDice
from rocketgram import context2


@router.handler
@commonfilters.chat_type(ChatType.private)
@commonfilters.command('/dice')
def dice():
    """\
    Send dice for user. Just for fun."""

    SendDice(context2.user.user_id).webhook()
