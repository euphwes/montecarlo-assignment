""" Tests for the API routes. """

# Shim the Flask app database creation to use an in-memory SQLite database instead of the
# filesystem production one.
import os
os.environ['MONTECARLO_TEST_ENV'] = 'true'

from unittest import TestCase

from montecarlo import DB, app
from montecarlo.api.routes import metrics_list
from montecarlo.persistence.models import CryptoPairMetric


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
