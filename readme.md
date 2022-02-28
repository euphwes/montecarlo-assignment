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

1. Open up a new terminal window
2. Activate your new montecarlo Python virtual environment:
    1. `cd` to the directory containing your virtual environment
    2. `. montecarlo/Scripts/activate`
3. `cd` to your root `montecarlo_app` project directory
4. Run the Flask development server:
    1. `flask run`


### Using the API

This web app offers two API endpoints:

The `metrics_list` endpoint is `/metrics`, which returns a representation of all `CryptoPairMetrics`, which indicate the
specific metrics being tracked (price or volume) for a particular crypto/fiat pair at a particular market. The combination
of market and crypto/fiat pair is known as a `ticker`.

This API endpoint can be used to build a UI to present a user with available metrics.

Example response:

```json
{
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
}
```

The `metrics_info` endpoint is `/metrics/<metric_id>`, where `<metric_id>` is the internal ID for a `CryptoPairMetric`
as returned by the `metrics_list` endpoint. This `metrics_info` endpoint returns a 24-hour history of values of the requested
data point, as well as its standard deviation over that time period, and a ranking against other metrics of the same type
(price or volume) within the same time period.

This API endpoint can be used to build a UI to present the user with a chart of the desired crypto metric's behavior over
time, as well as indicate how this metric is performing compared to similar metrics.

Example response:

```json
{
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
}
```


### Design considerations and future improvements

#### TODOs

To stay reasonably within the suggested 5-hour time limit, I skipped some unit tests in places like config, app
setup in init), as I felt it was a more valuable use of time to focus on tests for the core business logic. In a real-world
environment I'd complete unit tests to give my code base as much coverage as possible. Additionally, the tests could stand
to be more thoroughly documented (docstrings, internal comments).

Another TODO is to clean up "prod" vs "test" app configuration; as it stands, "test" app configuration is applied by
setting a particular environment variable value in the test case setup so that an in-memory database is used, etc. In a
production-worthy environment, configuration for prod and pre-prod stages would be decoupled from the code itself, and
would be loaded dynamically depending on the specific environment.

Currently, the DB model is tied to the web application itself. In a real-world scenario, the DB model, persistence-wrapper
code, etc, would be decoupled from the web application and provided in a common utility package which could be used by
the web app, the background crypto metrics poller, and any other potential components not yet written.

Obviously in a production environment, we wouldn't be using an in-memory or file-based SQLite database, so we'd move
that infrastructure over to a more suitable database (PostgreSQL, Oracle, MySQL, etc).

#### Scability

*What would you change if you needed to track many metrics?*

There's room for improvement in the crypto-polling configuration to specify which types of metrics you'd like to poll
for each market and crypto/fiat pair. Rather than assuming just price and volume, desired metrics could be introduced
by configuration and persistence of these metrics could be implemented by designing an "adapter" mechanism which defines
in-code how to extract that metrics from the Cryptowatch API and persist it to the database.

*What if you needed to sample them more frequently?*

The current scheme of using a single process to periodically poll Cryptowatch's API for metrics is not particularly
scalable. In order to be able to scale this process in a production environment, I'd design a series of serverless
functions which can be horizontally scaled if/when necessary.

I imagine an "orchestrator" Lambda which is invoked on a periodic basis (once per minute, or more frequently), parses
configuration to determine which metrics are being polled on a per-market/crypto pair basis. This orchestrator Lambda
invokes a series of poller Lambdas in parallel, each one responsible for polling the Cryptowatch API for a particular
ticker's market summary and persisting its tracked metrics to the database.

Additionally, this application currently calculates standard deviation and performs the similar-metric-ranking on the
fly -- this might become infeasible with a large number of metrics, each being polled on a cadence more frequently than
once per minute. This is a candidate for an additional background periodic task, which pre-calculates standard deviation
and rankings on a per metric basis and persists them to the database, so the API itself was responsible for less business
logic and merely returned pre-existing data.

This leads to...

*What if you had many users accessing your dashboard to view metrics?*

Being able to support multiple concurrent requests is important for a high-traffic API. I'd address this from potentially
two fronts; horizontally scaling the web application itself, multiple instances running behind a load balancer, as well
as designing the API in a such a way that the web server can asynchronously respond to multiple requests and handle IO-bound
operations (database queries) in an async/await fashion.

Moving business logic (such as standard deviation calculation and rankings) out of the API and into a background task
to be pre-calculated also improves API performance as it's merely a data-query and transport mechanism.

#### Testing

Beyond the unit testing I've implemented, this application like many others could also benefit from integration testing
and load testing.

Integration testing would validate that the crypto metrics mechanism is able to talk to the Cryptowatch API as expected,
and is able to scale the poller processes to handle any number of metrics to be polled. It would also ensure our service
is fault-tolerant against Cryptowatch API being down, unavailable, etc. We could possibly fall back to a different crypto
metrics provider, and/or alarm internally to notify the team of ops issues. Integration testing would ensure all these
mechanisms behave as expected.

Load testing is valuable in making sure that we, and our downstream dependencies (Cryptowatch API, etc) can handle
expected load. In a pre-production environment, we can continuously hit our APIs with a high level of traffic to ensure
that latencies remain within allowable bounds, our system continues to operate as expected (database can handle the
IO rates, etc), and our boxes hosting the service are maintaining resource utilization (memory, CPU usage) within
acceptable bounds.

#### Thoughts on a real-time alert feature

As described above, we'd need to pre-calculate metric standard deviation on a per-data point basis, instead of on demand
within the web API.

We'd offer an alert-subscription mechanism -- users can subscribe to alerts for certain metrics of interest (BTC/USD price,
for example), and provide whatever information necessary for us to send them an alert (email address for email notifications,
phone number for text message notifications, etc). We'd maintain these subscriptions internally.

We'd have a background periodic process, potentially serverless and scaled horizontally to handle analysis of point-in-time
standard deviation of all metrics of interest against the average standard deviation within the past hour. If this process
identifies a metric of interest (current deviation is 3x average deviation over the last hour), a message indicating this
event is inserted into a queue.

A process ingests messages from this queue to determine all users who are interested in this event, and then queues up
notification jobs which are picked up by another process to notify all interested users of the event in question.