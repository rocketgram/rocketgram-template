import logging

from rocketgram import Bot, commonfilters, ChatType
from rocketgram import MessageType, ParseModeType
from rocketgram import UpdateType, Dispatcher, DefaultValuesMiddleware
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
def before_callback_request():
    """This is preprocessor. All preprocessor will be called for every update with callback_query."""

    logger.info('Got new callback from %s: `%s`',
                context.update().callback_query.user.user_id,
                context.update().callback_query.data)


@router.before
@commonfilters.chat_type(ChatType.private)
@commonfilters.update_type(UpdateType.message)
def before_message_request():
    """This is preprocessor. All preprocessor will be called for every update with message."""

    if context.update().message.message_type == MessageType.text:
        logger.info('Got new message from %s: `%s`', context.update().message.user.user_id,
                    context.update().message.text)
    else:
        logger.info('Got new message from %s', context.update().message.user.user_id)
