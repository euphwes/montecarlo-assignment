""" SQLAlchemy models for the database tables. """

from montecarlo import DB


class CryptoPairCustomMetric(DB.Model):
    """ A point-in-time instance of a crypto/fiat pair metric (price or volume) and its value. """

    __tablename__ = 'metrics'
    id = DB.Column(DB.Integer, primary_key=True)
    ticker = DB.Column(DB.String, index=True)
    metric_type = DB.Column(DB.Enum('price', 'volume', name='metric_type'), index=True)
    metric_value = DB.Column(DB.Float)
    timestamp = DB.Column(DB.DateTime(timezone=True))


# This ensures the local SQLite DB is created and the metrics table is created.
# In a production system, this wouldn't be the responsibility of the web app itself, but rather
# part of the infrastructure creation/deployment process, but for the sake of simplicity in a
# take-home assignment this is fine.
DB.create_all()
