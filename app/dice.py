from mybot import router
from rocketgram import commonfilters, ChatType, SendDice, DiceType
from rocketgram import context

ALL_DICES = list(DiceType)[:-1]
ALL_DICES_LEN = len(ALL_DICES)


@router.handler
@commonfilters.chat_type(ChatType.private)
@commonfilters.command('/dice')
class Dice:
    def __call__(self):
        """\
        Send dice for user. This also demonstrates how to use class-based handlers."""

        emoji = ALL_DICES[context.update.update_id % ALL_DICES_LEN]

        SendDice(context.user.user_id, emoji).webhook()
