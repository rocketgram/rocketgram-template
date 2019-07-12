import json

from mybot import router
from rocketgram import ChatType, SendMessage, UpdateType, InlineKeyboard, EditMessageReplyMarkup, AnswerCallbackQuery
from rocketgram import commonfilters, commonwaiters, context2
from rocketgram import make_waiter
from rocketgram.tools import escape


@make_waiter
@commonfilters.update_type(UpdateType.message)
@commonfilters.chat_type(ChatType.private)
def next_all():
    return True


@router.handler
@commonfilters.chat_type(ChatType.private)
@commonfilters.callback('stop')
async def stop():
    """Shows how break existing waiter."""

    yield commonwaiters.drop_waiter()

    await EditMessageReplyMarkup(chat_id=context2.chat.chat_id, message_id=context2.message.message_id).send()
    await AnswerCallbackQuery(context2.update.callback_query.query_id).send()
    SendMessage(context2.chat.chat_id, "🔹 Ok! See you later!").webhook()


@router.handler
@commonfilters.chat_type(ChatType.private)
@commonfilters.command('/echo')
async def echo():
    """Shows how to use waiter."""

    msg = "🔹 Now i will send you back all messages in raw format like @ShowJsonBot.\n\n" \
          "Hit /cancel to exit."

    kb = InlineKeyboard()
    kb.callback('Stop!', 'stop')

    SendMessage(context2.message.chat.chat_id, msg, reply_markup=kb.render()).webhook()

    while True:

        # here waiting next request
        # this is python's async generator
        yield next_all()

        if context2.message.text == '/cancel':
            SendMessage(context2.message.chat.chat_id, "🔹 Ok! See you later!").webhook()
            return

        # print reminder every five updates
        if not context2.update.update_id % 5:
            await SendMessage(context2.message.chat.chat_id,
                              "🔹 I am in <code>echo</code> mode. Hit /cancel to exit.").send()

        prepared = escape.html(json.dumps(context2.update.raw, ensure_ascii=False, indent=1))
        SendMessage(context2.message.chat.chat_id,
                    f"<code>{prepared}</code>",
                    reply_to_message_id=context2.message.message_id).webhook()
