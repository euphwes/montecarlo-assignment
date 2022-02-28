""" API routes. """

from datetime import datetime
from statistics import stdev

from montecarlo import app
from montecarlo.persistence.metrics_manager import (
    get_all_crypto_pair_metrics,
    get_crypto_pair_metric_by_id,
    get_24h_metric_history
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

    # Ensure metric ID is an integer and return a 400 Bad Request if it's not
    try:
        metric_id = int(metric_id)
    except ValueError:
        msg = 'Invalid metric ID: "{}". Must be an integer.'.format(metric_id)
        return {'error': msg}, 400

    metric = get_crypto_pair_metric_by_id(int(metric_id))

    # Ensure the metric exists. If not, return a 404 Not Found.
    if metric is None:
        return {'error': 'No such metric with ID {}.'.format(metric_id)}, 404

    # TODO test and clean up below

    # Get metric instance value history over the last day so we can return values and timestamps
    # in this API response for charting purposes.
    metric_value_history = get_24h_metric_history(metric.id, datetime.utcnow())

    # Extract a raw list of metric values over the past day so we can calculate standard deviation.
    raw_history = [m.metric_value for m in metric_value_history]
    std_deviation = stdev(raw_history)

    # Get similar metrics and their standard deviations, and sort by standard deviation
    std_devs = _get_metric_std_devs(metric.metric_type)
    std_devs.sort(key=lambda x: x[1])

    rank = None
    for i, (m_id, std_dev) in enumerate(std_devs):
        if metric.id == m_id:
            rank = i + 1
            break

    return {
        'id': metric_id,
        'ticker': metric.ticker,
        'metric_type': metric.metric_type,
        'metric_24h_history': [m.to_json() for m in metric_value_history],
        'standard_deviation': std_deviation,
        'metric_rank': '{}/{}'.format(rank, len(std_devs))
    }


def _get_metric_std_devs(metric_type):
    """ TODO doc and test """

    # Store a list of tuples of metrics IDs to daily standard deviation so we can rank metrics of
    # the specified type.
    metric_std_devs = list()

    # Get all metrics and only keep the ones with the same metric type, so we can perform a
    # meaningful ranking of similar metrics by their daily standard deviation.
    all_metrics = get_all_crypto_pair_metrics()
    similar_metrics = [m for m in all_metrics if m.metric_type == metric_type]

    now = datetime.utcnow()
    for metric in similar_metrics:
        metric_value_history = get_24h_metric_history(metric.id, now)
        raw_history = [m.metric_value for m in metric_value_history]

        metric_std_devs.append((metric.id,stdev(raw_history)))

    return metric_std_devs
