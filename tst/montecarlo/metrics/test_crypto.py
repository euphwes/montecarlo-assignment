""" Tests for the cryptocurrency metrics module. """

from datetime import datetime
from unittest import TestCase
from unittest.mock import Mock, patch

from cryptowatch.errors import CryptowatchError

from montecarlo.metrics.crypto import poll_crypto_metrics, pull_market_summary


class CryptoMetricsTests(TestCase):

    @patch('montecarlo.metrics.crypto.bulk_save_metrics')
    @patch('montecarlo.metrics.crypto.pull_market_summary')
    @patch('montecarlo.metrics.crypto.CRYPTO_CONFIG')
    @patch('montecarlo.metrics.crypto.datetime')
    def test_poll_crypto_metrics_success(self,
                                         patched_datetime,
                                         patched_config,
                                         patched_pull_market_summary,
                                         patched_bulk_save_metrics):
        expected_date = datetime.utcnow()
        patched_datetime.utcnow.return_value = expected_date

        mock_market = Mock()
        mock_market.name = 'KRAKEN'
        mock_market.pairs = ['BTCUSD', 'ETHUSD']

        patched_config.markets = [mock_market]

        # KRAKEN:BTCUSD price, volume, and KRAKEN:ETHUSD price, volume
        patched_pull_market_summary.side_effect = [(1.1, 2.2), (3.3, 4.4)]

        poll_crypto_metrics()

        assert patched_pull_market_summary.call_count == 2

        expected_ticker_metric_map = {
            'KRAKEN:BTCUSD': {
                'price': 1.1,
                'volume': 2.2
            },
            'KRAKEN:ETHUSD': {
                'price': 3.3,
                'volume': 4.4
            }
        }

        patched_bulk_save_metrics.assert_called_once_with(expected_ticker_metric_map, expected_date)

    @patch('montecarlo.metrics.crypto._log')
    @patch('montecarlo.metrics.crypto.bulk_save_metrics')
    @patch('montecarlo.metrics.crypto.pull_market_summary')
    @patch('montecarlo.metrics.crypto.CRYPTO_CONFIG')
    @patch('montecarlo.metrics.crypto.datetime')
    def test_poll_crypto_metrics_complete_api_failure(self,
                                                      patched_datetime,
                                                      patched_config,
                                                      patched_pull_market_summary,
                                                      patched_bulk_save_metrics,
                                                      patched_logger):
        expected_date = datetime.utcnow()
        patched_datetime.utcnow.return_value = expected_date

        mock_market = Mock()
        mock_market.name = 'KRAKEN'
        mock_market.pairs = ['BTCUSD', 'ETHUSD']

        patched_config.markets = [mock_market]

        patched_pull_market_summary.side_effect = [CryptowatchError, CryptowatchError]

        poll_crypto_metrics()

        assert patched_pull_market_summary.call_count == 2
        assert patched_logger.error.call_count == 2

        patched_bulk_save_metrics.assert_called_once_with(dict(), expected_date)

    @patch('montecarlo.metrics.crypto._log')
    @patch('montecarlo.metrics.crypto.bulk_save_metrics')
    @patch('montecarlo.metrics.crypto.pull_market_summary')
    @patch('montecarlo.metrics.crypto.CRYPTO_CONFIG')
    @patch('montecarlo.metrics.crypto.datetime')
    def test_poll_crypto_metrics_partial_api_failure(self,
                                                     patched_datetime,
                                                     patched_config,
                                                     patched_pull_market_summary,
                                                     patched_bulk_save_metrics,
                                                     patched_logger):
        expected_date = datetime.utcnow()
        patched_datetime.utcnow.return_value = expected_date

        mock_market = Mock()
        mock_market.name = 'KRAKEN'
        mock_market.pairs = ['BTCUSD', 'ETHUSD']

        patched_config.markets = [mock_market]

        # KRAKEN:BTCUSD price, volume, and KRAKEN:ETHUSD market summary fails
        patched_pull_market_summary.side_effect = [(1.1, 2.2), CryptowatchError]

        poll_crypto_metrics()

        assert patched_pull_market_summary.call_count == 2
        assert patched_logger.error.call_count == 1

        expected_ticker_metric_map = {
            'KRAKEN:BTCUSD': {
                'price': 1.1,
                'volume': 2.2
            }
        }

        patched_bulk_save_metrics.assert_called_once_with(expected_ticker_metric_map, expected_date)

    @patch('montecarlo.metrics.crypto.cw_client')
    def test_pull_market_summary_success(self, patched_cw_client):
        expected_ticker = 'KRAKEN:DOGEUSD'
        expected_price = 123.45
        expected_volume = 67.89

        mock_market_summary = Mock()
        mock_market_summary.volume = expected_volume
        mock_market_summary.price.last = expected_price

        mock_api_response = Mock()
        mock_api_response.market = mock_market_summary

        patched_cw_client.markets.get.return_value = mock_api_response

        received_price, received_volume = pull_market_summary(expected_ticker)

        patched_cw_client.markets.get.assert_called_once_with(expected_ticker)

        assert expected_price == expected_price
        assert received_volume == expected_volume

    @patch('montecarlo.metrics.crypto.cw_client')
    def test_pull_market_summary_failure(self, patched_cw_client):

        expected_ticker = 'KRAKEN:DOGEUSD'

        patched_cw_client.markets.get.side_effect = CryptowatchError

        with self.assertRaises(CryptowatchError):
            pull_market_summary(expected_ticker)

        patched_cw_client.markets.get.assert_called_once_with(expected_ticker)
