from mybot import router
from rocketgram import commonfilters, ChatType, SendMessage, priority
from rocketgram import context


@router.handler
@commonfilters.chat_type(ChatType.private)
@priority(2048)
def unknown():
    """\
    This is about how to use priority.

    This handler caches all messages to bot, but since we set priority
    to 2048 handler will be called if no other handlers was do.

    Default priority in Dispatcher is 1024, so for
    set the order of handlers you can use @priority decorator."""

    SendMessage(context.user.user_id,
                "🔹 I don't known what to do. May be /help?").webhook()
