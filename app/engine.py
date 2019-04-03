import logging
import os

import mybot
import rocketgram

logger = logging.getLogger('minibots.engine')


def main():
    mode = os.environ.get('MODE', 'updates').lower().strip()

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
        rocketgram.run_updates(bot, drop_updates=bool(int(os.environ.get('DROP_UPDATES', 0).strip())))
    elif mode in ('webhook', 'heroku'):
        if mode == 'heroku':
            port = os.environ['PORT']
        else:
            port = os.environ.get('WEBHOOK_PORT', 8080).strip()
        rocketgram.run_webhook(bot,
                               os.environ['WEBHOOK_URL'].strip(),
                               os.environ.get('WEBHOOK_PATH', '/').strip(),
                               port=int(port),
                               drop_updates=bool(int(os.environ.get('DROP_UPDATES', 0).strip())))
    else:
        raise TypeError('MODE must be `updates` or `webhook` or `heroku`!')

    logger.info('Bye!')


if __name__ == '__main__':
    main()
