import json

from mybot import router
from rocketgram import ChatType, SendMessage, UpdateType, InlineKeyboard, EditMessageReplyMarkup, AnswerCallbackQuery, ReplyParameters
from rocketgram import commonfilters, commonwaiters, context
from rocketgram import make_waiter
from rocketgram.tools import parser


@make_waiter
@commonfilters.update_type(UpdateType.message)
@commonfilters.chat_type(ChatType.private)
def next_all():
    return True


@router.handler
@commonfilters.chat_type(ChatType.private)
@commonfilters.callback('stop')
async def stop():
    """Shows how to break an existing waiter."""

    yield commonwaiters.drop_waiter()

    await EditMessageReplyMarkup(chat_id=context.chat.id, message_id=context.message.message_id).send()
    await AnswerCallbackQuery(context.callback.id).send()
    SendMessage(context.chat.id, "🔹 Ok! See you later!").webhook()


@router.handler
@commonfilters.chat_type(ChatType.private)
@commonfilters.command('/echo')
async def echo():
    """Shows how to use waiter."""

    msg = "🔹 Now i will send you back all messages in raw format like @ShowJsonBot.\n\n" \
          "Hit /cancel to exit."

    kb = InlineKeyboard()
    kb.callback('Stop!', 'stop')

    SendMessage(context.chat.id, msg, reply_markup=kb.render()).webhook()

    while True:

        # here waiting next request
        # this is python's async generator
        yield next_all()

        if context.message.text == '/cancel':
            SendMessage(context.chat.id, "🔹 Ok! See you later!").webhook()
            return

        # print reminder every five updates
        if not context.update.update_id % 5:
            await SendMessage(context.chat.id, "🔹 I am in <code>echo</code> mode. Hit /cancel to exit.").send()

        prepared = parser.escape_html(json.dumps(context.update.raw, ensure_ascii=False, indent=1))
        SendMessage(
            context.chat.id,
            f"<code>{prepared}</code>",
            reply_parameters=ReplyParameters(message_id=context.message.message_id)
        ).webhook()
