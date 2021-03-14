import logging
import os

import callbacks  # noqa
import commands  # noqa
import dice  # noqa
import echo  # noqa
import inline  # noqa
import keyboards  # noqa
import mybot
import myenigma  # noqa
import poll  # noqa
import rocketgram
import send  # noqa
import unknown  # noqa

logger = logging.getLogger('minibots.engine')


def main():
    mode = os.environ.get('MODE')
    if mode is None and 'DYNO' in os.environ:
        mode = 'heroku'

    if mode not in ('updates', 'webhook', 'heroku'):
        raise TypeError('MODE must be `updates` or `webhook` or `heroku`!')

    logging.basicConfig(format='%(asctime)s - %(levelname)-5s - %(name)-25s: %(message)s')
    logging.basicConfig(level=logging.ERROR)
    logging.getLogger('engine').setLevel(logging.INFO)
    logging.getLogger('mybot').setLevel(logging.DEBUG)
    logging.getLogger('rocketgram').setLevel(logging.DEBUG)
    logging.getLogger('rocketgram.raw.in').setLevel(logging.INFO)
    logging.getLogger('rocketgram.raw.out').setLevel(logging.INFO)

    logger.info('Starting bot''s template in %s...', mode)

    bot = mybot.get_bot(os.environ['TOKEN'].strip())

    if mode == 'updates':
        rocketgram.UpdatesExecutor.run(bot, drop_pending_updates=bool(int(os.environ.get('DROP_UPDATES', 0))))
    else:
        port = int(os.environ['PORT']) if mode == 'heroku' else int(os.environ.get('WEBHOOK_PORT', 8080))
        rocketgram.AioHttpExecutor.run(bot,
                                       os.environ['WEBHOOK_URL'].strip(),
                                       os.environ.get('WEBHOOK_PATH', '/').strip(),
                                       host='0.0.0.0', port=port,
                                       drop_pending_updates=bool(int(os.environ.get('DROP_UPDATES', 0))),
                                       webhook_remove=not mode == 'heroku')

    logger.info('Bye!')


if __name__ == '__main__':
    main()
