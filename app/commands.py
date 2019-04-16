from rocketgram import Context, commonfilters, ChatType, SendMessage
from mybot import router


@router.handler
@commonfilters.chat_type(ChatType.private)
@commonfilters.command('/start')
async def start_command(ctx: Context):
    """This is asynchronous handler. You can use here any async code."""

    await ctx.bot.send_message(ctx.update.message.user.user_id,
                               '🔹 Hello there. This is the demo bot for Rockegram framework.\n\n'
                               'See source code here:\n'
                               'github.com/vd2org/rocketgram-template\n\n'
                               'And Rocketgram framework source here:\n'
                               'github.com/vd2org/rocketgram\n\n'
                               'You can list all commands by type /help.\n\n'
                               'Support group: @RocketBots.',
                               disable_web_page_preview=True)


@router.handler
@commonfilters.chat_type(ChatType.private)
@commonfilters.command('/help')
def help_command(ctx: Context):
    """Handler can also be simple function.

    But remember - in async environment you shouldn't use here hard synchronous code.

    This handler also demonstrates how to make webhook-request.

    If you use webhook executor this will be send as reply of received a webhook.
    Otherwise bot's router will fallback to send by regular call."""

    whr = SendMessage(ctx.update.message.user.user_id,
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
                      "/echo - Waiting next request in same handler.\n"
                      "\n"
                      "/inline - Shows how to use inline mode.\n"
                      "\n"
                      "/enigma - Enigma cypher machine")

    ctx.webhook_request(whr)




