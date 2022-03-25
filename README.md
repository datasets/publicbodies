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

## Contribute Data

Please just add a CSV file and submit a pull request or open an issue.

The set of fields required in the CSV file can be seen in the field list on:
[public-body-schema.json](public-body-schema.json). You can also check out 
the existing data in `data/` for hints. To learn more about Data
Packages, visit https://specs.frictionlessdata.io/.

## For Developers of the Website

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

----

## Original Preparation

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
