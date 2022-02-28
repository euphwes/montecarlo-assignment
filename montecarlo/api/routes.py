""" API routes. """

from montecarlo import app
from montecarlo.persistence.metrics_manager import get_all_crypto_pair_metrics


@app.route('/metrics', methods=['GET'])
def metrics_list():
    """ Returns a JSON response containing all CryptoPairMetrics in the database.

    Ex: {
        "metrics": [
            {
                "id": 1,
                "metric_type": "price",
                "ticker": "KRAKEN:BTCUSD"
            },
            {
                "id": 2,
                "metric_type": "volume",
                "ticker": "KRAKEN:BTCUSD"
            },
            ...
            {
                "id": 20,
                "metric_type": "volume",
                "ticker": "ZONDA:USDTUSD"
            }
        ]
    } """

    return {
        'metrics': [m.to_json() for m in get_all_crypto_pair_metrics()]
    }
