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

     Ex: {
      "id": 3,
      "metric_24h_history": [
        {
          "timestamp": "2022-02-27 05:06:37.850087",
          "value": 2619.8
        },
        ...
        {
          "timestamp": "2022-02-27 17:14:25.342538",
          "value": 2799.67
        }
      ],
      "metric_rank": "8/10",
      "metric_type": "price",
      "standard_deviation": 65.7042239543861,
      "ticker": "KRAKEN:ETHUSD"
    } """

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

    # Get metric instance value history over the last day, so we can return values and timestamps
    # in this API response for charting purposes.
    metric_value_history = get_24h_metric_history(metric.id, datetime.utcnow())

    # Get this metric's standard deviation over the last day, and also its rank position against
    # the standard deviations of similar metrics in the same time period.
    rank, standard_deviation = _rank_metric_against_similar(metric)

    return {
        'id': metric_id,
        'ticker': metric.ticker,
        'metric_type': metric.metric_type,
        'metric_24h_history': [m.to_json() for m in metric_value_history],
        'standard_deviation': standard_deviation,
        'metric_rank': rank
    }


# Note: this probably belongs in a separate module with similar business logic, but since I don't
# have anything else specific to put in there I'll keep it here.
def _rank_metric_against_similar(metric):
    """ Given a target metric, pull the 24h history all metrics with the same metric type
    (we'll call these "similar metrics"), and ranking them by their standard deviation across this
    time range. Return a tuple of (rank_position, standard_deviation) for our target metric. """

    # Store a list of tuples of metrics IDs and daily standard deviation, so we can rank metrics of
    # the same type as the target metric.
    metric_std_devs = list()

    # Get all metrics and only keep the ones with the same metric type, so we can perform a
    # meaningful ranking of similar metrics by their daily standard deviation.
    all_metrics = get_all_crypto_pair_metrics()
    similar_metrics = [m for m in all_metrics if m.metric_type == metric.metric_type]

    # Pull 24h metric value history for all similar metrics, calculate their standard deviation in
    # this time period, store the result for that metric.
    now = datetime.utcnow()
    for similar_metric in similar_metrics:
        metric_value_history = get_24h_metric_history(similar_metric.id, now)
        raw_history = [m.metric_value for m in metric_value_history]
        metric_std_devs.append((similar_metric.id, stdev(raw_history)))

    # Sort the metrics by their standard deviation values, in ascending order.
    metric_std_devs.sort(key=lambda x: x[1])

    rank = None
    standard_deviation = None

    # Iterate the sorted metrics until we find our target metric.
    # The 1-based index of our metric in this list will be its ranking, and while we have the value,
    # remember its specific standard deviation so we can return it.
    for i, (m_id, std_dev) in enumerate(metric_std_devs):
        if metric.id == m_id:
            rank = i + 1
            standard_deviation = std_dev
            break

    # Report the rank as this metric's position within the total number of similar metrics
    rank_string = '{}/{}'.format(rank, len(metric_std_devs))

    return rank_string, standard_deviation
