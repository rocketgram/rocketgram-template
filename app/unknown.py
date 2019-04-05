from mybot import router
from rocketgram import Context, commonfilters, ChatType, SendMessage, priority


@router.handler
@commonfilters.chat_type(ChatType.private)
@priority(2048)
def unknown(ctx: Context):
    """\
    This is about how to use priority.

    This handler caches all messages to bot, but since we set priority
    to 2048 handler will be called if no other handlers was do.

    Default priority in Dispatcher is 1024, so for
    set the order of handlers you can use @priority decorator."""

    whr = SendMessage(ctx.update.message.user.user_id,
                      "🔹 I don't known what to do. May be /help?")

    ctx.webhook_request(whr)
