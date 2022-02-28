""" Tests for the API routes. """

# Shim the Flask app database creation to use an in-memory SQLite database instead of the
# filesystem production one.
import os
os.environ['MONTECARLO_TEST_ENV'] = 'true'

from datetime import datetime, timedelta
from statistics import stdev
from unittest import TestCase

from montecarlo import DB, app
from montecarlo.persistence.models import CryptoPairMetric, MetricInstanceValue


class APIRoutesTests(TestCase):

    def setUp(self):
        """ Make sure that the in-memory database has the expected test data before each test. """
        DB.drop_all()
        DB.create_all()

        # Create a handful of metrics to use
        btcusd_price = CryptoPairMetric(ticker='KRAKEN:BTCUSD', metric_type='price')
        btcusd_volume = CryptoPairMetric(ticker='KRAKEN:BTCUSD', metric_type='volume')
        ethusd_price = CryptoPairMetric(ticker='KRAKEN:ETHUSD', metric_type='price')
        ethusd_volume = CryptoPairMetric(ticker='KRAKEN:ETHUSD', metric_type='volume')

        self.known_metrics = [btcusd_price, btcusd_volume, ethusd_price, ethusd_volume]
        for metric in self.known_metrics:
            DB.session.add(metric)
        DB.session.commit()

        self.btcusd_price_id = btcusd_price.id
        self.ethusd_price_id = ethusd_price.id

        # Create some metric instance values for the price metrics for KRAKEN:BTCUSD and ETCUSD,
        # for testing the metric info route.

        now = datetime.utcnow()

        self.btcusd_price_values = [1, 2, 3, 4]
        # something like 1.3, this will be ranked first above ETHUSD standard deviation
        # which is more like 123.87
        self.btcusd_std_dev = stdev(self.btcusd_price_values)
        for i, price in enumerate(self.btcusd_price_values):
            DB.session.add(MetricInstanceValue(
                custom_metric_id=self.btcusd_price_id,
                metric_value=price,
                timestamp=now - timedelta(minutes=1)
            ))

        for i, price in enumerate([99, 106, 300, 5]):
            DB.session.add(MetricInstanceValue(
                custom_metric_id=self.ethusd_price_id,
                metric_value=price,
                timestamp=now - timedelta(minutes=1)
            ))
        DB.session.commit()


    def test_metrics_list(self):
        """ Tests a call to the metrics list route. """

        with app.test_client() as c:
            response = c.get('/metrics')
            assert response.status_code == 200
            assert response.json == {
                'metrics': [m.to_json() for m in self.known_metrics]
            }

    def test_metrics_info_invalid_metric_id(self):
        """ Tests a call to the metrics info route with an invalid metric ID. """

        with app.test_client() as c:
            response = c.get('/metrics/twenty')

            # 400 Bad Request
            assert response.status_code == 400
            assert response.json == {
                'error': 'Invalid metric ID: "twenty". Must be an integer.'
            }

    def test_metrics_info_unknown_metric(self):
        """ Tests a call to the metrics info route with a metric ID, but to a metric which does not
        exist. """

        with app.test_client() as c:
            response = c.get('/metrics/30')

            # 404 Not Found
            assert response.status_code == 404
            assert response.json == {
                'error': 'No such metric with ID 30.'
            }

    def test_metrics_info_success(self):
        """ Tests a call to the metrics info route for a valid metric."""

        with app.test_client() as c:
            response = c.get('/metrics/{}'.format(self.btcusd_price_id))

            assert response.status_code == 200

            data = response.json
            assert data['id'] == self.btcusd_price_id
            assert data['metric_rank'] == '1/2'
            assert data['metric_type'] == 'price'
            assert data['ticker'] == 'KRAKEN:BTCUSD'
            assert data['standard_deviation'] == self.btcusd_std_dev
            assert len(data['metric_24h_history']) == len(self.btcusd_price_values)

            # Rather than sorting and asserting contents, it makes more sense to assert specific
            # values and timestamps for each known instance value in the database, and making sure
            # it shows up in the history returned by the API, but I'm passing on that in the
            # interest of time.
            history_raw = [m['value'] for m in data['metric_24h_history']]
            assert sorted(self.btcusd_price_values) == sorted(history_raw)
