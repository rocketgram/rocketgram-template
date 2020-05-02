import logging
import os

import callbacks
import commands
import dice
import echo
import inline
import keyboards
import mybot
import myenigma
import poll
import rocketgram
import send
import unknown


# avoid to remove "unused" imports by optimizers
def fix_imports():
    _ = callbacks
    _ = commands
    _ = echo
    _ = keyboards
    _ = myenigma
    _ = inline
    _ = send
    _ = dice
    _ = unknown
    _ = poll


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
        rocketgram.UpdatesExecutor.run(bot, drop_updates=bool(int(os.environ.get('DROP_UPDATES', 0))))
    else:
        port = int(os.environ['PORT']) if mode == 'heroku' else int(os.environ.get('WEBHOOK_PORT', 8080))
        rocketgram.AioHttpExecutor.run(bot,
                                       os.environ['WEBHOOK_URL'].strip(),
                                       os.environ.get('WEBHOOK_PATH', '/').strip(),
                                       host='0.0.0.0', port=port,
                                       drop_updates=bool(int(os.environ.get('DROP_UPDATES', 0))),
                                       webhook_remove=not mode == 'heroku')

    logger.info('Bye!')


if __name__ == '__main__':
    main()
