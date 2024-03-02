import rocketgram
from mybot import router
from rocketgram import commonfilters, ChatType, SendMessage
from rocketgram import context, LinkPreviewOptions


@router.handler
@commonfilters.chat_type(ChatType.private)
@commonfilters.command('/start')
async def start_command():
    """This is the asynchronous handler. You can use here any async code."""
    await SendMessage(
        context.user.id,
        '🔹 Hello there. This is the demo bot for Rocketgram framework.\n\n'
        f'Rocketgram version: {rocketgram.version()}\n\n'
        'See source code here:\n'
        'github.com/rocketgram/rocketgram-template\n\n'
        'And Rocketgram framework source here:\n'
        'github.com/rocketgram/rocketgram\n\n'
        'You can list all commands by type /help.\n\n'
        'Support group: @RocketBots.',
        link_preview_options=LinkPreviewOptions(
            url='https://github.com/rocketgram/rocketgram',
            prefer_small_media=True,
        ),
    ).send()


@router.handler
@commonfilters.chat_type(ChatType.private)
@commonfilters.command('/help')
def help_command():
    """Handler can also be a simple function.

    But remember, in the async environment, you shouldn't use here hard synchronous code.

    This handler also demonstrates how to make webhook-request.

    If you use the webhook executor, this will be sent as reply of received a webhook.
    Otherwise, bot's router will fall back to send by regular call."""

    SendMessage(context.user.id,
                "🔹 Bot's help.\n"
                "\n"
                "/start - Print welcome message.\n"
                "/help - Show this message."
                "\n"
                "\n"
                "/keyboard - Shows keyboard.\n"
                "/keyboard_location - Shows keyboard with location button.\n"
                "/keyboard_contact - Shows keyboard with contact button.\n"
                "/cancel - Removes current keyboard.\n"
                "\n"
                "/simple_inline_keyboard - Shows simple inline keyboard.\n"
                "/arranged_inline_keyboard - Shows how to arrange inline keyboard.\n"
                "/arranged_scheme_inline_keyboard - Shows how to arrange inline keyboard by scheme.\n"
                "\n"
                "/send - Shows how send files.\n"
                "\n"
                "/echo - Waiting next request in same handler.\n"
                "\n"
                "/inline - Shows how to use inline mode.\n"
                "\n"
                "/dice - Sends dice.\n"
                "\n"
                "/poll - Sends poll.\n"
                "\n"
                "/enigma - Enigma cypher machine.").webhook()
