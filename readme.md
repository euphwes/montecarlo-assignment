## Crypto/Fiat Metrics API
This project is a simple web application which periodically polls real-time cryptocurrency quotes from a publicly
available API, persists this data over time, and exposes a handful of REST APIs to allow access to this data as well
as custom rankings of specific cryptocurrency metrics based on standard deviation over time.

Crypto quotes are retrieved from https://docs.cryptowat.ch/rest-api/.

### Getting started

#### Environment setup

1. Ensure you have a recent Python 3.x installation as well as `virtualenv` installed.
    1. https://www.python.org/downloads/
    2. https://pypi.org/project/virtualenv/


2. Create a new virtual environment for this web app to create an isolated Python environment.
    1. `virtualenv --python=python3 montecarlo`


3. Activate the virtual environment so that you're running the expected Python version and installing dependencies
   specifically to this environment.
    1. `. montecarlo/Scripts/activate` (if on Linux/Unix)
    2. `montecarlo/Scripts/active.bat`


4. Clone this repository and move into the newly-created project directory.
    1. `git clone <TODO URL> montecarlo_app`
    2. `cd montecarlo_app`


5. Install dependencies via `pip`.
    1. `pip install -r requirements.txt`


6. Set environment variables.
    1. `export FLASK_APP=montecarlo`
    2. `export FLASK_ENV=development`


7. *(Optional)* Sign up for a Cryptowatch account and get an API key. Set the public key in an environment variable.
    1. Visit https://cryptowat.ch/ and follow instructions to create an account and generate an API key.
    2. `export CRYPTO_API_KEY=<your public key>`


#### Running unit tests

`pytest` is my preferred test runner and testing framework, and is included in `requirements.txt`.

From the root project directory, run the test suite with `python -m pytest`.


#### Running the metrics poller

This web application requires a process running which periodically polls the Cryptowatch API to get the latest cryptocurrency
metrics and persist them to the database. Fire up this process by following these instructions:

1. Open up a new terminal window
2. Activate your new montecarlo Python virtual environment:
    1. `cd` to the directory containing your virtual environment
    2. `. montecarlo/Scripts/activate`
3. `cd` to your root `montecarlo_app` project directory
4. Run the poller process:
    1. `python poller_entry.py`
   
This will create a scheduler which will run the crypto metrics poller on a 1-minute interval. You'll see informative
logging in the terminal window which will indicate the poller is running.

Press `Ctrl-C` at any time to quit (note: it may take up to 1 minute to exit as the scheduler is blocking).

#### Running the web application

TODO


### Using the API

TODO


### Design considerations and future improvements

TODO

timestamp for metrics not established until all metrics are collected, for simplicity
possibly timestamp each metric as the latest data is pulled

right now doing multiple DB queries, 1 each for ticker and metric type combo
For larger numbers of metrics, and/or larger number of tickers, it might be more effective
from a DB IO POV to query one *all* data from previous 24 hours, and then filter in memory.
Need to do some DB query profiling, estimate resource usage, etc

calculating std dev and ranking on the fly in the polling process.