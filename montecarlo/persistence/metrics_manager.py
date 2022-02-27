""" Easy access queries and operations against this app's database. """

from montecarlo import DB
from montecarlo.persistence.models import CryptoPairMetric, MetricInstanceValue

METRIC_PRICE = 'price'
METRIC_VOLUME = 'volume'


def bulk_save_metrics(ticker_metric_map, timestamp):
    """ Accepts a map of tickers (market + crypto/fiat pair combos) to their latest values for each
     metric type, as well the current timestamp, and bulk inserts records to the database for each
     of these metrics. """

    # Hold a map of ticker + metric types to the CryptoPairMetrics DB entries which represent them.
    crypto_pair_metric_map = dict()

    # First make sure we have created instances of the CryptoPairMetrics themselves. Query them and
    # create them if they are new, so we can reference them when adding the latest metric values to
    # the database.
    for ticker, metric_map in ticker_metric_map.items():
        for metric_type, _ in metric_map.items():
            crypto_pair_metric = _get_or_create_crypto_pair_metric(ticker, metric_type)
            crypto_pair_metric_map[(ticker, metric_type)] = crypto_pair_metric

    # Now that we know the corresponding CryptoPairMetrics (and have ensured they exist), create
    # the MetricInstanceValues and bulk insert them into the database at once.
    for ticker, metric_map in ticker_metric_map.items():
        for metric_type, metric_value in metric_map.items():
            DB.session.add(MetricInstanceValue(
                crypto_pair_metric=crypto_pair_metric_map[(ticker, metric_type)],
                metric_value=metric_value,
                timestamp=timestamp
            ))

    DB.session.commit()


def _get_or_create_crypto_pair_metric(ticker, metric_type):
    """ Retrieves a CryptoPairMetric if it exists, otherwise creates and returns it. """

    crypto_pair_metric = CryptoPairMetric.query.\
        filter(CryptoPairMetric.ticker == ticker).\
        filter(CryptoPairMetric.metric_type == metric_type).\
        first()

    # If it doesn't yet exist, create it.
    if crypto_pair_metric is None:
        crypto_pair_metric = CryptoPairMetric(ticker=ticker, metric_type=metric_type)
        DB.session.add(crypto_pair_metric)
        DB.session.commit()

    return crypto_pair_metric
