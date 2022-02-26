""" SQLAlchemy models for the database tables. """

from montecarlo import DB


class CryptoPairCustomMetric(DB.Model):
    """ A point-in-time instance of a crypto/fiat pair metric (price or volume), its standard
    deviation over the trailing 24-hour time period, as well as its rank (judged by standard
    deviation) as compared to other metrics of the same type. """

    __tablename__ = 'metrics'
    id = DB.Column(DB.Integer, primary_key=True)
    ticker = DB.Column(DB.String)
    metric_type = DB.Column(DB.Enum('price', 'volume', name='metric_type'))
    metric_value = DB.Column(DB.Float)
    metric_ranking = DB.Column(DB.Integer)
    standard_deviation = DB.Column(DB.Float)
    timestamp = DB.Column(DB.DateTime(timezone=True))


# This ensures the local SQLite DB is created and the metrics table is created.
# In a production system, this wouldn't be the responsibility of the web app itself, but rather
# part of the infrastructure creation/deployment process, but for the sake of simplicity in a
# take-home assignment this is fine.
DB.create_all()
