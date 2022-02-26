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
    2. `montecarlo/Scripts/active.bat` (if on Windows)


4. Clone this repository and move into the newly-created project directory.
    1. `git clone <TODO URL> montecarlo_app`
    2. `cd montecarlo_app`


5. Install dependencies via `pip`.
    1. `pip install -r requirements.txt`


6. Set environment variables.
    1. `export FLASK_APP=montecarlo_app`
    2. `export FLASK_ENV=development`


7. *(Optional)* Sign up for a Cryptowatch account and get an API key. Set the public key in an environment variable.
    1. Visit https://cryptowat.ch/ and follow instructions to create an account and generate an API key.
    2. `export CRYPTO_API_KEY=<your public key>`


#### Running the application

TODO


### Using the API

TODO


### Design considerations and future improvements

TODO