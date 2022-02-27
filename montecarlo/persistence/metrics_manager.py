""" Easy access queries and operations against this app's database. """

from montecarlo import DB
from montecarlo.persistence.models import CryptoPairCustomMetric

METRIC_PRICE = 'price'
METRIC_VOLUME = 'volume'


def bulk_save_metrics(ticker_metric_map, timestamp):
    """ Accepts a map of tickers (market + crypto/fiat pair combos) to their latest values for each
     metric type, as well the current timestamp, and bulk inserts records to the database for each
     of these metrics. """

    for ticker, metric_map in ticker_metric_map.items():
        for metric_type, metric_value in metric_map.items():
            DB.session.add(CryptoPairCustomMetric(
                ticker=ticker,
                metric_type=metric_type,
                metric_value=metric_value,
                timestamp=timestamp
            ))

    DB.session.commit()
