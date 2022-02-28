""" Tests for the metrics_manager module. """

# Shim the Flask app database creation to use an in-memory SQLite database instead of the
# filesystem production one.
import os
os.environ['MONTECARLO_TEST_ENV'] = 'true'

from datetime import datetime, timedelta
from unittest import TestCase

from montecarlo import DB
from montecarlo.persistence.models import CryptoPairMetric, MetricInstanceValue
from montecarlo.persistence.metrics_manager import (
    bulk_save_metrics,
    _get_or_create_crypto_pair_metric,
    get_all_crypto_pair_metrics,
    get_crypto_pair_metric_by_id,
    get_24h_metric_history
)


class MetricsManagerTest(TestCase):

    def setUp(self):
        """ Make sure that the in-memory database is clean before each test method. """
        DB.drop_all()
        DB.create_all()

    def test_create_crypto_pair_metric_creates_new_entry(self):
        assert CryptoPairMetric.query.count() == 0

        expected_ticker = 'KRAKEN:BTCUSD'
        expected_metric_type = 'price'

        created_metric = _get_or_create_crypto_pair_metric(expected_ticker, expected_metric_type)

        assert created_metric.ticker == expected_ticker
        assert created_metric.metric_type == expected_metric_type

        # Should just be the one new metric in the DB
        assert CryptoPairMetric.query.count() == 1

        # Assert another query returns the created metric
        assert created_metric == CryptoPairMetric.query. \
            filter(CryptoPairMetric.ticker == expected_ticker). \
            filter(CryptoPairMetric.metric_type == expected_metric_type). \
            first()

    def test_get_crypto_pair_metric_returns_correct(self):

        expected_ticker = 'KRAKEN:BTCUSD'
        expected_metric_type = 'price'

        expected_metric = CryptoPairMetric(ticker=expected_ticker, metric_type=expected_metric_type)
        DB.session.add(expected_metric)
        DB.session.commit()

        assert CryptoPairMetric.query.count() == 1

        received_metric = _get_or_create_crypto_pair_metric(expected_ticker, expected_metric_type)

        # The count should still be 1, no new one should've been created
        assert CryptoPairMetric.query.count() == 1

        # Confirm the query returns the pre-existing matching metric
        assert received_metric == expected_metric

    def test_bulk_save_metrics_fresh(self):

        # Completely clean database, nothing in it yet
        assert CryptoPairMetric.query.count() == 0
        assert MetricInstanceValue.query.count() == 0

        ticker_metric_map = {
            'KRAKEN:BTCUSD': {
                'price': 123.45,
                'volume': 88.77
            },
            'KRAKEN:LTCUSD': {
                'price': 998.77,
                'volume': 77.665
            }
        }

        bulk_save_metrics(ticker_metric_map, datetime.utcnow())

        # 4 metric types should exist now
        # (KRAKEN:BTCUSD price and volume, KRAKEN:LTCUSD price and volume)
        assert CryptoPairMetric.query.count() == 4

        # 4 metric instance values should exist now
        # 1 data point each for the above 4 metric types
        assert MetricInstanceValue.query.count() == 4


    def test_bulk_save_metrics_multiple_metric_instance_values(self):

        # Completely clean database, nothing in it yet
        assert CryptoPairMetric.query.count() == 0
        assert MetricInstanceValue.query.count() == 0

        ticker_metric_map = {
            'KRAKEN:BTCUSD': {
                'price': 123.45,
                'volume': 88.77
            },
            'KRAKEN:LTCUSD': {
                'price': 998.77,
                'volume': 77.665
            }
        }

        bulk_save_metrics(ticker_metric_map, datetime.utcnow())
        bulk_save_metrics(ticker_metric_map, datetime.utcnow() + timedelta(minutes=1))
        bulk_save_metrics(ticker_metric_map, datetime.utcnow() + timedelta(minutes=2))
        bulk_save_metrics(ticker_metric_map, datetime.utcnow() + timedelta(minutes=3))

        # 4 metric types should exist now
        # (KRAKEN:BTCUSD price and volume, KRAKEN:LTCUSD price and volume)
        assert CryptoPairMetric.query.count() == 4

        # 16 metric instance values should exist now
        # 4 data points each for the above 4 metric types (across 4 minutes)
        assert MetricInstanceValue.query.count() == 16


    def test_get_all_crypto_pair_metrics(self):

        expected_metrics = list()
        for ticker in ['KRAKEN:BTCUSD', 'KRAKEN:DOGEUSD']:
            for metric_type in ['price', 'volume']:
                _get_or_create_crypto_pair_metric(ticker, metric_type)
                expected_metrics.append({'ticker': ticker, 'metric_type': metric_type})

        assert CryptoPairMetric.query.count() == 4

        received_metrics = get_all_crypto_pair_metrics()
        assert len(received_metrics) == 4

        for i, expected_metric in enumerate(expected_metrics):
            rec_metric = received_metrics[i]
            assert rec_metric.ticker == expected_metric['ticker']
            assert rec_metric.metric_type == expected_metric['metric_type']


    def test_get_crypto_pair_metric_by_id(self):

        expected_ticker = 'KRAKEN:BTCUSD'
        expected_metric_type = 'price'
        expected_metric = _get_or_create_crypto_pair_metric(expected_ticker, expected_metric_type)

        received_metric = get_crypto_pair_metric_by_id(expected_metric.id)

        assert received_metric == expected_metric


    def test_get_24h_metric_history(self):

        ticker = 'KRAKEN:BTCUSD'
        metric_type = 'price'
        metric = _get_or_create_crypto_pair_metric(ticker, metric_type)

        now = datetime.utcnow()
        ticker_metric_map = {
            'KRAKEN:BTCUSD': {
                'price': 123.45,
                'volume': 88.77
            }
        }

        # Push some metric instance values over the last 6 hours
        # Note the price values are 123.45, we'll assert those values later
        for n in range(6):
            timestamp = now - timedelta(hours=n)
            bulk_save_metrics(ticker_metric_map, timestamp)

        # Push some metric instance values more than a day ago
        # Note the price values are now 999.99, we'll make sure we assert that we're not getting
        # these particular values
        ticker_metric_map = {
            'KRAKEN:BTCUSD': {
                'price': 999.99,
                'volume': 88.77
            }
        }
        for n in range(6):
            timestamp = now - timedelta(days=2, hours=n)
            bulk_save_metrics(ticker_metric_map, timestamp)

        # 24 total metric instance data points, 12 each for price and volume of the above ticker
        assert MetricInstanceValue.query.count() == 24

        metric_24h_history = get_24h_metric_history(metric.id, now)

        # Should have only received the 6 data points in the last day specifically for price.
        # Note: we should also assert specific timestamps on the metric values, but I'm glossing
        # over that in the interest of time for this exercise.
        assert len(metric_24h_history) == 6
        assert all(m.metric_value == 123.45 for m in metric_24h_history)
