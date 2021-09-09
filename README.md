[![goodtables.io](https://goodtables.io/badge/github/okfn/publicbodies.svg)](https://goodtables.io/github/okfn/publicbodies)

A database of public bodies (or organizations):

> Government-run or controlled organizations or entities which may or may not
> have distinct corporate existence

Examples are:

* Government Ministries or Departments
* State-run Health organizations
* Police and fire departments

Visit the site: http://publicbodies.org/

## Data

Data is stored in CSVs partitioned by country or region (e.g. EU). Directories
are named by ISO code.  

## Contribute Data

Please just add a CSV file and submit a pull request or open an issue.

The set of fields required in the CSV file can be seen in the field list on:
<http://data.okfn.org/community/okfn/publicbodies>.  You can also check out 
the existing data in `data/` for hints, or if you like JSON, you can look
directly at the `datapackage.json` file in this repo.  To learn more about Data
Packages, visit http://specs.frictionlessdata.io/.

## For Developers of the Website

The website is a node webapp. To get it running:

1. Install node and npm (>= 12). Alternatively, install Docker.

2. Get the code

        ```
        git clone https://github.com/okfn/publicbodies
        ```

3. Install the dependencies (make sure you are in the publicbodies directory)

        ```
        npm install .
        ```

  If you're using Docker, build the container instead:

        ```
        docker build --rm -t publicbodies .
        ```

4. Run the webapp:

        ```
        node index.js
        ```
  
  If you're using Docker, start the container instead:

        ```
        docker run --rm --volume="$PWD:/home/node/portal" -p 3000:3000 -it publicbodies node index.js
        ```

The list of outstanding issues is at: <https://github.com/okfn/publicbodies/issues>

----

## Original Preparation

Details of the automated data extraction to build the original database.

Data sources:

* A-Z Index of U.S. Government Departments and Agencies - http://www.usa.gov/directory/federal/index.shtml
* AskTheEU.org
* FragDenStaat.de - (private GoogleDoc) - http://www.bund.de/DE/Behoerden
* WhatDoTheyKnow.com - http://www.whatdotheyknow.com/body/all-authorities.csv
* Brazilian Government SIORG - http://www.siorg.redegoverno.gov.br/ - xml export at http://repositorio.dados.gov.br/governo-politica/administracao-publica/estrutura-organizacional/

### Building the SQLite DB

Schema:

    title
    abbr
    key
    slug
    category
    parent
    parent_key
    description
    url
    jurisdiction
    jurisdiction_code
    source
    source_url
    source_description
    address
    contact
    email
    tags
    created_at
    updated_at

SQL 

    ALTER TABLE froide_de ADD COLUMN source; 
    ALTER TABLE froide_de ADD COLUMN source_description;
    ALTER TABLE froide_de ADD COLUMN source_url;
    UPDATE froide_de SET source = 'FragDenStaat / Bund Online';
    UPDATE froide_de SET source_url = 'https://fragdenstaat.de/hilfe/';
    UPDATE froide_de SET source_description = 'Federal-level agencies of the German government';

    ALTER TABLE froide_de ADD COLUMN jurisdiction;
    ALTER TABLE froide_de ADD COLUMN jurisdiction_code;
    UPDATE froide_de SET jurisdiction = 'Germany';
    UPDATE froide_de SET jurisdiction_code = 'DE';

    ALTER TABLE ateu_en ADD COLUMN source; 
    ALTER TABLE ateu_en ADD COLUMN source_description;
    ALTER TABLE ateu_en ADD COLUMN source_url;
    UPDATE ateu_en SET source = 'Ask the EU (AccessInfo)';
    UPDATE ateu_en SET source_url = 'http://www.asktheeu.org/de/help/api';
    UPDATE ateu_en SET source_description = 'European-level FoI request tracker';

    ALTER TABLE ateu_en ADD COLUMN jurisdiction;
    ALTER TABLE ateu_en ADD COLUMN jurisdiction_code;
    UPDATE ateu_en SET jurisdiction = 'European Union';
    UPDATE ateu_en SET jurisdiction_code = 'EU';

    ALTER TABLE wdtk_gb ADD COLUMN source; 
    ALTER TABLE wdtk_gb ADD COLUMN source_description;
    ALTER TABLE wdtk_gb ADD COLUMN source_url;
    UPDATE wdtk_gb SET source = 'What do they know? (MySociety)';
    UPDATE wdtk_gb SET source_url = 'http://www.whatdotheyknow.com/help/api';
    UPDATE wdtk_gb SET source_description = 'UK FoI site';

    ALTER TABLE wdtk_gb ADD COLUMN jurisdiction;
    ALTER TABLE wdtk_gb ADD COLUMN jurisdiction_code;
    UPDATE wdtk_gb SET jurisdiction = 'United Kingdom';
    UPDATE wdtk_gb SET jurisdiction_code = 'GB';


    CREATE TABLE entity (
      title TEXT,
      abbr TEXT,
      key TEXT,
      slug TEXT,
      category TEXT,
      parent TEXT,
      parent_key TEXT,
      description TEXT,
      url TEXT,
      jurisdiction TEXT,
      jurisdiction_code TEXT,
      source TEXT,
      source_url TEXT,
      source_description TEXT,
      address TEXT,
      contact TEXT,
      email TEXT,
      tags TEXT,
      created_at TEXT,
      updated_at TEXT);

    DELETE FROM entity;
    INSERT INTO entity 
      (title, category, parent, description, url, jurisdiction, 
       jurisdiction_code, source, source_url, source_description, 
       address, contact, email, tags) 
      SELECT title, class, parent, description, url, jurisdiction, 
        jurisdiction_code, source, source_url, source_description, 
        address, contacts AS contact, email, tags FROM froide_de; 

    INSERT INTO entity
      (title, abbr, slug, url, jurisdiction, jurisdiction_code, source, 
       source_url, source_description, tags, created_at, updated_at) 
      SELECT Name AS title, `Short name` AS abbr, `URL Name` AS slug, 
         `Home page` AS url, jurisdiction, jurisdiction_code, source, 
         source_url, source_description, Tags as tags, `Created at` 
         AS created_at, `Updated at` AS updated_at FROM wdtk_gb; 

    INSERT INTO entity
      (title, abbr, slug, url, jurisdiction, jurisdiction_code, source, 
       source_url, source_description, tags, created_at, updated_at) 
      SELECT Name AS title, `Short name` AS abbr, `URL Name` AS slug, 
         `Home page` AS url, jurisdiction, jurisdiction_code, source, 
         source_url, source_description, Tags as tags, `Created at` 
         AS created_at, `Updated at` AS updated_at FROM ateu_en; 


    CREATE TABLE alias (alias TEXT, key TEXT);
    DELETE FROM alias;
    INSERT INTO alias (alias, key) SELECT abbr AS alias, key AS key 
      FROM entity WHERE abbr IS NOT NULL AND LENGTH(abbr);
    INSERT INTO alias (alias, key) SELECT (SELECT ateu.Name AS alias FROM 
    ateu_de ateu WHERE ateu.`Home page` = ent.url) AS alias, ent.key AS key
    FROM entity ent; 
    INSERT INTO alias (alias, key) SELECT (SELECT ateu.Name AS alias FROM 
    ateu_de ateu WHERE ateu.`Short name` = ent.abbr) AS alias, ent.key AS key
    FROM entity ent; 
    INSERT INTO alias (alias, key) SELECT (SELECT ateu.Name AS alias FROM 
    ateu_fr ateu WHERE ateu.`Home page` = ent.url) AS alias, ent.key AS key
    FROM entity ent; 
    INSERT INTO alias (alias, key) SELECT (SELECT ateu.Name AS alias FROM 
    ateu_fr ateu WHERE ateu.`Short name` = ent.abbr) AS alias, ent.key AS key
    FROM entity ent; 
    INSERT INTO alias (alias, key) SELECT (SELECT ateu.Name AS alias FROM 
    ateu_es ateu WHERE ateu.`Home page` = ent.url) AS alias, ent.key AS key
    FROM entity ent; 
    INSERT INTO alias (alias, key) SELECT (SELECT ateu.Name AS alias FROM 
    ateu_es ateu WHERE ateu.`Short name` = ent.abbr) AS alias, ent.key AS key
    FROM entity ent; 
    DELETE FROM alias WHERE alias IS NULL;


    CREATE TABLE types (
      name TEXT,
      db_url TEXT,
      entity_table TEXT,
      entity_key TEXT,
      alias_table TEXT,
      alias_text TEXT,
      alias_key TEXT
      );

    INSERT INTO types (name, db_url, entity_table,
      entity_key, alias_table, alias_text, alias_key) VALUES
      ('bodies', 'http://localhost:5000/pudo/publicbody', 
      'entity', 'key', 'alias', 'alias', 'key');

### SQL to extract data from sqlite to CSV

    .output entities.csv
    .mode csv
    .headers ON

    SELECT * FROM entity;

