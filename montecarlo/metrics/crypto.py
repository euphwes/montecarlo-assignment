from datetime import datetime
from logging import getLogger, INFO
from os import environ

import cryptowatch as cw_client
from cryptowatch.errors import CryptowatchError

from montecarlo.metrics.config import CRYPTO_CONFIG
from montecarlo.persistence.metrics_manager import (
    bulk_save_metrics,
    METRIC_PRICE,
    METRIC_VOLUME
)


_log = getLogger(__name__)
_log.setLevel(INFO)

_API_KEY = 'CRYPTO_API_KEY'
_TICKER_TEMPLATE = '{market_name}:{pair_name}'

# If a Cryptowatch API key is specified, use that instead of relying on free daily API credits.
cw_client.api_key = environ.get(_API_KEY)


def poll_crypto_metrics():
    """ Entry point for the periodic task which polls Cryptowatch for crypto metrics, and persists
    these metrics for retrieval by the web API. """

    # Grab the current timestamp to assign to these metrics when we persist them.
    now = datetime.utcnow()

    # Maintain a map of tickers to metric types and their latest values, to facilitate bulk metric
    # insertion into the database.
    ticker_metric_map = dict()

    # For each crypto/fiat pair in each market, construct the ticker identifier and pull the
    # latest market summary from the cryptowatch API. This crypto summary will include latest price
    # quotes as well as trade volume information.
    for market in CRYPTO_CONFIG.markets:
        for pair in market.pairs:
            ticker = _TICKER_TEMPLATE.format(market_name=market.name, pair_name=pair).upper()
            try:
                price, volume = pull_market_summary(ticker)
                ticker_metric_map[ticker] = {METRIC_PRICE: price, METRIC_VOLUME: volume}

            except CryptowatchError as e:
                err = 'Failed to pull market summary for {ticker}: {e}'.format(ticker=ticker, e=e)
                _log.error(err)

    # Persist these metrics to the database.
    bulk_save_metrics(ticker_metric_map, now)


def pull_market_summary(ticker):
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
        volume=volume
    ))

    return price, volume
