""" SQLAlchemy models for the database tables. """

from sqlalchemy import Index
from sqlalchemy.orm import relationship

from montecarlo import DB


class CryptoPairMetric(DB.Model):
    """ Represents a specific type of metric data being tracked for a given market and crypto/fiat
    pair (ticker). For example, volume of BTC/USD trades at Kraken, or price quotes for ETH/USD at
    Binance. """

    __tablename__ = 'cryptoMetrics'
    id = DB.Column(DB.Integer, primary_key=True)
    ticker = DB.Column(DB.String)
    metric_type = DB.Column(DB.Enum('price', 'volume', name='metric_type'))

    # Add a composite index on CryptoPairMetric ticker and type, this should be a unique combo
    __tableargs__ = (Index('ticker_type_index', 'ticker', 'metric_type'), )

    def to_json(self):
        return {
            'id': self.id,
            'ticker': self.ticker,
            'metric_type': self.metric_type
        }


class MetricInstanceValue(DB.Model):
    """ A point-in-time value for a CryptoPairMetric. """

    __tablename__ = 'metricValues'
    id = DB.Column(DB.Integer, primary_key=True)
    metric_value = DB.Column(DB.Float)
    custom_metric_id = DB.Column(DB.Integer, DB.ForeignKey('cryptoMetrics.id'))
    timestamp = DB.Column(DB.DateTime(timezone=True))
    crypto_pair_metric = relationship('CryptoPairMetric', backref='values')


# This ensures the local SQLite database and underlying tables are created.
# In a production system, this wouldn't be the responsibility of the web app itself, but rather
# part of the infrastructure creation/deployment process, but for the sake of simplicity in a
# take-home assignment I think this is fine.
DB.create_all()
