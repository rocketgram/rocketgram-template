from mybot import router
from rocketgram import commonfilters, ChatType, SendMessage, priority, GetCustomEmojiStickers
from rocketgram import context


@router.handler
@commonfilters.chat_type(ChatType.private)
@priority(2048)
async def unknown():
    """\
    This code shows how to use the priority decorator.

    This handler will catch all messages to the bot, but since we set the priority
    to 2048 the handler will be called only if no other handlers was called.

    The default priority in the Dispatcher is 1024.

    You can use the @priority decorator to change it.
    """

    # SendMessage(context.user.id, "🔹 I don't known what to do. May be /help?").webhook()

    r = await GetCustomEmojiStickers(["5427175573497583755"]).send()
    print(r)

    await SendMessage(context.user.id, "😀😀😀").send()
