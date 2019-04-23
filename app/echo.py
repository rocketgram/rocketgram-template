import json

from mybot import router
from rocketgram import commonfilters, ChatType, SendMessage, UpdateType
from rocketgram import context
from rocketgram import make_waiter
from rocketgram.tools import escape


@make_waiter
@commonfilters.update_type(UpdateType.message)
@commonfilters.chat_type(ChatType.private)
def next_all():
    return True


@router.handler
@commonfilters.chat_type(ChatType.private)
@commonfilters.command('/echo')
async def echo():
    """Shows how to use waiter."""

    msg = "🔹 Now i will send you back all messages in raw foramat like @ShowJsonBot.\n\n" \
          "Hit /cancel to exit."

    SendMessage(context.update().message.chat.chat_id, msg).webhook()

    while True:

        # here waiting next request
        # this is python's async generator
        yield next_all()

        if context.update().message.text == '/cancel':
            SendMessage(context.update().message.chat.chat_id, "🔹 Ok! See you later!").webhook()
            return

        # print reminder every five updates
        if not context.update().update_id % 5:
            await SendMessage(context.update().message.chat.chat_id,
                              "🔹 I am in <code>echo</code> mode. Hit /cancel to exit.").send()

        prepared = escape.html(json.dumps(context.update().raw, ensure_ascii=False, indent=1))
        SendMessage(context.update().message.chat.chat_id,
                    f"<code>{prepared}</code>",
                    reply_to_message_id=context.update().message.message_id).webhook()
