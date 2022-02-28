""" API routes. """

from montecarlo import app
from montecarlo.persistence.metrics_manager import (
    get_all_crypto_pair_metrics,
    get_crypto_pair_metric_by_id
)


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


@app.route('/metrics/<metric_id>', methods=['GET'])
def metrics_info(metric_id):
    """ Returns a 24-hour history of data points for the requested metric, as well as its standard
     deviation in that time period and rank against other metrics of the same metric type.

     Ex: TODO """

    try:
        metric_id = int(metric_id)
    except ValueError:
        msg = 'Invalid metric ID: "{}". Must be an integer.'.format(metric_id)
        return {'error': msg}, 400

    metric = get_crypto_pair_metric_by_id(int(metric_id))
    if metric is None:
        return {'error': 'No such metric with ID {}.'.format(metric_id)}, 404

    # placeholder
    return {'id': metric_id, 'ticker': metric.ticker}
