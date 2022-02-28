""" A basic period process which calls montecarlo.metrics.crypto.poll_crypto_metrics on a 1-minute
interval to get the latest and greatest cryptocurrency metrics. """

import logging
from sys import stdout

from apscheduler.schedulers.blocking import BlockingScheduler
from montecarlo.metrics.crypto import poll_crypto_metrics

log_format = '%(levelname)s %(asctime)s [%(filename)s %(funcName)s] - %(message)s'
logging.basicConfig(stream=stdout, format=log_format)

if __name__ == '__main__':
    scheduler = BlockingScheduler()
    scheduler.add_job(poll_crypto_metrics, 'interval', seconds=60)

    print('Press Ctrl-C to exit.')

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass
