# Contributing

## Test Coverage

To contribute to Consulate, please make sure that any new features or changes
to existing functionality **include test coverage**.

*Pull requests that add or change code without coverage have a much lower chance
of being accepted.*

## Prerequisites

Consulate test suite has a couple of requirements:

 * Dependencies from [requirements/testing.txt](requirements/testing.txt) are installed
 * Local Docker and [docker-compose](https://docs.docker.com/compose/)

## Installing Dependencies

You may want to develop in a virtual environment. This is usually done inside the source
repository, and `.gitignore` is configured to ignore a virtual environment in `env`.

```bash
python3 -m venv env
source env/bin/activate
```

To install the dependencies needed to run Consulate tests, use

```bash
pip install -r requirements/testing.txt
```    

## Starting the test dependency

Prior to running tests, ensure that Consul is running via Docker using:

```bash
./bootstrap
```
    
This script uses [docker-compose](https://docs.docker.com/compose/) to launch a Consul server container that is
pre-configured for the tests. In addition, it configures `build/test-environment` that is loaded
by the tests with configuration information for connecting to Consul.

## Running Tests

To run all test suites, run:

    nosetests

## Code Formatting

Please format your code using [yapf](http://pypi.python.org/pypi/yapf)
with ``pep8`` style prior to issuing your pull request. In addition, run
``flake8`` to look for any style errors prior to submitting your PR.

Both are included when the test requirements are installed. If you are fixing
formatting for existing code, please separate code-reformatting commits from 
functionality changes.
