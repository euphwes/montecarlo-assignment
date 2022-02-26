from datetime import datetime
from logging import getLogger, INFO
from os import environ

import cryptowatch as cw_client
from cryptowatch.errors import CryptowatchError

from montecarlo.metrics.config import CRYPTO_CONFIG


_log = getLogger(__name__)
_log.setLevel(INFO)

_API_KEY = 'CRYPTO_API_KEY'
_TICKER_TEMPLATE = '{market_name}:{pair_name}'

# If a Cryptowatch API key is specified, use that instead of relying on free daily API credits.
cw_client.api_key = environ.get(_API_KEY)


def poll_crypto_metrics():
    """ Entry point for the periodic task which polls cryptowatch for crypto metrics, and persists
    these metrics and calculated statistics to the database for retrieval by the web API. """

    # Grab the current datetime to persist later
    now = datetime.utcnow()

    # Map tickers to the new metrics pulled to facilitate custom calculations and data persistence
    ticker_metrics_map = dict()

    for market in CRYPTO_CONFIG.markets:
        for pair in market.pairs:
            ticker = _TICKER_TEMPLATE.format(market_name=market.name, pair_name=pair.name).upper()
            try:
                price, volume = _pull_market_summary(ticker)
                ticker_metrics_map[ticker] = (price, volume)
            except CryptowatchError as e:
                err = 'Failed to pull market summary for {ticker}: {e}'.format(ticker=ticker, e=e)
                _log.error(err)

    # TODO pull 24-hour previous data
    # TODO calc standard deviation and rank metrics
    # TODO persist data


def _pull_market_summary(ticker):
    """ Calls the cryptowatch market summary API for the market and crypto/fiat pair ticker, and
    returns the subset of relevant information we care about from this call, a tuple of
    (price, volume) for this instant in time. """

    _log.info('Pulling market summary for {ticker}.'.format(ticker=ticker))

    market_summary = cw_client.markets.get(ticker).market
    price = market_summary.price.last
    volume = market_summary.volume

    _log.debug('{ticker}: price={price}, volume={volume}'.format(
        ticker=ticker,
        price=price,
        volume=volume)
    )

    return price, volume
