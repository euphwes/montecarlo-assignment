import json
from os.path import dirname, abspath, join

_MARKETS = 'markets'
_NAME = 'name'
_PAIRS = 'pairs'


class MarketConfig:
    """ Market-level config which specifies the crypto/fiat pairs tracked for this market. """

    def __init__(self, market_data):
        self.name = market_data[_NAME]
        self.pairs = market_data[_PAIRS]


class CryptoMetricsConfig:
    """ Top-level config class that specifies which crypto markets are to be polled and which
    crypto/fiat pairs in each market are tracked. """

    def __init__(self, config_path):
        try:
            with open(config_path) as f:
                data = json.loads(f.read())
                self.markets = [MarketConfig(market) for market in data[_MARKETS]]

        except Exception as e:
            raise RuntimeError('Could not load crypto metrics config: {}'.format(e))


# Build absolute path to config file based on this module's location
_PARENT_DIR = dirname(abspath(__file__))
_CRYPTO_CONFIG_PATH = join(_PARENT_DIR, 'market_pair_config.json')

# Use this for easy access to per-market crypto/fiat pair metrics config
CRYPTO_CONFIG = CryptoMetricsConfig(_CRYPTO_CONFIG_PATH)
