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
    _get_or_create_crypto_pair_metric
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
