[![Data](https://github.com/okfn/publicbodies/actions/workflows/frictionless.yaml/badge.svg)](https://repository.frictionlessdata.io/report?user=okfn&repo=publicbodies&flow=publicbodies)

A database of public bodies (or organizations):

> Government-run or controlled organizations or entities which may or may not
> have distinct corporate existence

Examples are:

* Government Ministries or Departments
* State-run Health organizations
* Police and fire departments

Visit the site: https://publicbodies.org/

## Data

Data is stored in CSVs partitioned by country or region (e.g. EU) in the
[data](data) folder. Files are named by two-letter ISO code.  

## Contribute data

Please just add a CSV file and submit a pull request or
[open an issue](https://github.com/okfn/publicbodies/issues).

The set of fields required in the CSV file can be seen in the field list on:
[public-body-schema.json](public-body-schema.json). You can also check out 
the existing data in `data/` for hints. To learn more about Data
Packages, visit https://specs.frictionlessdata.io/.

If you can, [developing a bot](#for-developers-of-data-collector-bots)
to automatically and periodically collect the data is even better.

## For developers of the website

The website is a node webapp. To get it running:

1. Install node and npm (>= 12). Alternatively, install Docker.

2. Get the code

    ```bash
    git clone https://github.com/okfn/publicbodies
    ```

3. Install the dependencies (make sure you are in the publicbodies
    directory)

    ```bash
    npm install .
    ```

    If you're using Docker, build the container instead:

    ```bash
    docker build --rm -t publicbodies .
    ```

    If you are building a development environment, please use:

    ```bash
    docker build --rm -t publicbodies . --build-arg NODE_ENV=development
    ```

    so that you can get debugging information.

4. Run the webapp:

    ```bash
    node index.js
    ```
  
    If you're using Docker, start the container instead:

    ```bash
    docker run --rm --name publicbodies -p 3000:3000 -it publicbodies node index.js
    ```

The list of outstanding issues is at: <https://github.com/okfn/publicbodies/issues>

## For developers of data collector bots

Data is kept automatically up-to-date by bots that collect and update
data once a week. The scripts are kept on the
[scripts/import](scripts/import) directory, followed by the international
place code (e.g. `br` for Brazil, `it` for Italy).

The script MUST be runnable from a command line interface. It should
display the available options if run with the `--help` parameter, and
output data to the file chosen by the `--output` parameter. For example:

```bash
python3 scripts/import/br/import_br.py --help
```
```
usage: import_br.py [-h] [--output file_name]

Imports Brazilian public body data from the official source and complements it
with data from several auxiliary sources. Official source: [SIORG's open data
API](https://dados.gov.br/dataset/siorg)

optional arguments:
  -h, --help          show this help message and exit
  --output file_name  filename for the data output as CSV
```

When making requests, bots MUST use the Public Bodies Bot user agent string
to identify themselves to servers:

```
PublicBodiesBot (https://github.com/okfn/publicbodies)
```

If using Python, use the same libraries already defined in
[scrips/requirements.txt](scripts/requirements.txt), in order to keep
the project dependencies tidy, and only add new ones if strictly
necessary.

After creating a new bot, make sure to add it to the
[update data workflow](.github/workflows/update_data.yml) so that it runs
regularly and keeps the data up-to-date.

----

## Original preparation

Details of the automated data extraction to build the original database.

Data sources:

* Brazil
  * Brazilian Government's SIORG – https://dados.gov.br/dataset/siorg
* European Union
  * [AskTheEU.org](https://www.asktheeu.org/)
* Italy
  * Opendata IPA
    ([amministrazioni](https://indicepa.gov.it/ipa-dati/dataset/amministrazioni)
    / [enti](https://indicepa.gov.it/ipa-dati/dataset/enti))
* Germany
  * FragDenStaat.de – (private GoogleDoc)
  * Bund.de – https://www.bund.de/Content/DE/Behoerden/Suche/Formular.html
* United Kingdom
  * WhatDoTheyKnow.com – https://www.whatdotheyknow.com/body/all-authorities.csv
* United States of America
  * A-Z Index of U.S. Government Departments and Agencies – https://www.usa.gov/federal-agencies/a
