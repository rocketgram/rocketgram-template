import json

from mybot import router
from rocketgram import Context, commonfilters, ChatType, SendMessage, UpdateType
from rocketgram import make_waiter
from rocketgram.tools import escape


@make_waiter
@commonfilters.update_type(UpdateType.message)
@commonfilters.chat_type(ChatType.private)
def next_all(ctx: Context):
    return True


# =========================================================================================
@router.handler
@commonfilters.chat_type(ChatType.private)
@commonfilters.command('/echo')
async def echo(ctx: Context):
    """Shows how to use waiter."""

    msg = "🔹 Now i will send you back all messages in raw foramat like @ShowJsonBot.\n\n" \
          "Hit /cancel to exit."

    whr = SendMessage(ctx.update.message.chat.chat_id, msg)
    ctx.webhook_request(whr)

    while True:

        # here waiting next request
        # this is python's async generator
        ctx: Context = (yield next_all())

        if ctx.update.message.text == '/cancel':
            whr = SendMessage(ctx.update.message.chat.chat_id, "🔹 Ok! See you later!")
            ctx.webhook_request(whr)
            return

        # print reminder every five updates
        if not ctx.update.update_id % 5:
            await ctx.bot.send_message(ctx.update.message.chat.chat_id,
                                       "🔹 I am in <code>echo</code> mode. Hit /cancel to exit.")

        prepared = escape.html(json.dumps(ctx.update.raw, ensure_ascii=False, indent=1))
        whr = SendMessage(ctx.update.message.chat.chat_id,
                          f"<code>{prepared}</code>",
                          reply_to_message_id=ctx.update.message.message_id)
        ctx.webhook_request(whr)
