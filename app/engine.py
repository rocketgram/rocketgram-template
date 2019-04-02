import logging
import os

import mybot
import rocketgram

logger = logging.getLogger('minibots.engine')


def main():
    mode = os.environ.get('MODE', 'updates')

    logging.basicConfig(format='%(asctime)s - %(levelname)-5s - %(name)-25s: %(message)s')
    logging.basicConfig(level=logging.ERROR)
    logging.getLogger('engine').setLevel(logging.INFO)
    logging.getLogger('mybot').setLevel(logging.DEBUG)
    logging.getLogger('rocketgram').setLevel(logging.DEBUG)
    logging.getLogger('rocketgram.raw.in').setLevel(logging.INFO)
    logging.getLogger('rocketgram.raw.out').setLevel(logging.INFO)

    logger.info('Starting bot''s template %s...', )

    bot = mybot.get_bot(os.environ['TOKEN'])

    if mode == 'updates':
        rocketgram.run_updates(bot, drop_updates=bool(int(os.environ.get('DROP_UPDATES', 0))))
    elif mode == 'webhook':
        rocketgram.run_webhook(bot,
                               os.environ['WEBHOOK_URL'],
                               os.environ['WEBHOOK_PATH'],
                               port=int(os.environ.get('WEBHOOK_PORT', 8080)),
                               drop_updates=bool(int(os.environ.get('DROP_UPDATES', 0))))
    else:
        raise TypeError('MODE must be `updates` or `webhook`!')

    logger.info('Bye!')


if __name__ == '__main__':
    main()
