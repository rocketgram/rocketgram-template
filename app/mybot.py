import logging

from rocketgram import Bot, commonfilters, ChatType, DefaultValuesMiddleware, ParseModeType
from rocketgram import MessageType
from rocketgram import UpdateType, Dispatcher
from rocketgram import context

logger = logging.getLogger('mybot')

router = Dispatcher()


def get_bot(token: str):
    # create bot with given token
    bot = Bot(token, router=router)

    # Pass middleware that sets parse_mode to 'html' if it is none.
    bot.middleware(DefaultValuesMiddleware(parse_mode=ParseModeType.html))

    return bot


@router.on_init
def on_init():
    """This function called when bot starts. Place here any startup code."""

    logger.info('I am starting!')


@router.on_shutdown
def on_shutdown():
    """This function called when bot stops. Place here any cleanup code."""

    logger.info('I am going to sleep!')


@router.before
@commonfilters.chat_type(ChatType.private)
@commonfilters.update_type(UpdateType.callback_query)
async def before_callback_request():
    """This is the preprocessor. All preprocessors will be called for every update with callback_query."""

    logger.info('Got new callback from %s: `%s`', context.user.id, context.callback.data)


@router.before
@commonfilters.chat_type(ChatType.private)
@commonfilters.update_type(UpdateType.message)
def before_message_request():
    """This is the preprocessor. All preprocessors will be called for every update with message."""

    if context.message.type == MessageType.text:
        logger.info('Got new message from %s: `%s`', context.user.id, context.message.text)
    else:
        logger.info('Got new message from %s', context.user.id)
