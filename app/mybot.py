import logging
import pickle
from datetime import datetime

import munch

from rocketgram import Bot, Dispatcher, DefaultValuesMiddleware, ParseModeType

logger = logging.getLogger('mybot')

router = Dispatcher()


def get_bot(token: str):
    bot = Bot(token, router=router, globals_class=munch.Munch, context_data_class=munch.Munch)
    bot.middleware(DefaultValuesMiddleware(parse_mode=ParseModeType.html))
    return bot

