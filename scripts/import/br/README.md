## Purpose

This script copies and imports the information about the Brazilian
federal government organizational structure from the open data API at

https://dados.gov.br/dataset/siorg

It saves the data as a csv file in the
[schema](http://data.okfn.org/data/okfn/public-bodies) used by the
[public bodies project](https://github.com/okfn/publicbodies).

## Dependencies

* `python-slugify` to generate user-friendly ids
* `requests`, to fetch data through http(s)
* `pandas`, for some data transformations

## Installation

Simply create and activate a virtual environment

```bash
$ python3 -m venv env
$ source env/bin/activate
```

and install the dependencies.

```bash
(env)$ pip install -r requirements.txt
```
## Usage

With the Python environment active, just run the `import_br.py` script.

```
(env)$ python import_br.py
```

As an optional parameter, you can specify the path and file name of the
csv file output.
