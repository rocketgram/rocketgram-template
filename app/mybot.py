import logging

import munch

from rocketgram import Bot, Context, commonfilters, ChatType
from rocketgram import MessageType, ParseModeType
from rocketgram import UpdateType, Dispatcher, DefaultValuesMiddleware

logger = logging.getLogger('mybot')

router = Dispatcher()


def get_bot(token: str):
    # create bot with given token
    bot = Bot(token, router=router, globals_class=munch.Munch, context_data_class=munch.Munch)

    # Pass middleware that sets parse_mode to 'html' if it is none.
    bot.middleware(DefaultValuesMiddleware(parse_mode=ParseModeType.html))

    return bot

@router.on_init
def on_init(bot: Bot):
    """This function called when bot starts. Place here any startup code."""

    logger.info('I am starting!')

@router.on_shutdown
def on_shutdown(bot: Bot):
    """This function called when bot stops. Place here any cleanup code."""

    logger.info('I am going to sleep!')


@router.before
@commonfilters.chat_type(ChatType.private)
@commonfilters.update_type(UpdateType.callback_query)
def before_callback_request(ctx: Context):
    """This is preprocessor. All preprocessor will be called for every update with callback_query."""

    logger.info('Got new callback from %s: `%s`',
                ctx.update.callback_query.user.user_id,
                ctx.update.callback_query.data)


@router.before
@commonfilters.chat_type(ChatType.private)
@commonfilters.update_type(UpdateType.message)
def before_message_request(ctx: Context):
    """This is preprocessor. All preprocessor will be called for every update with message."""

    if ctx.update.message.message_type == MessageType.text:
        logger.info('Got new message from %s: `%s`', ctx.update.message.user.user_id, ctx.update.message.text)
    else:
        logger.info('Got new message from %s', ctx.update.message.user.user_id)
