from mybot import router
from rocketgram import commonfilters, ChatType, SendDice
from rocketgram import context


@router.handler
@commonfilters.chat_type(ChatType.private)
@commonfilters.command('/dice')
class Dice:
    def __call__(self):
        """\
        Send dice for user. This also demonstrates how to use class-based handlers."""

        emoji = "🎲" if context.update.update_id % 2 else "🎯"

        SendDice(context.user.user_id, emoji).webhook()
