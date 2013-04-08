A database of public bodies (or organizations):

> Government-run or controlled organizations or entities which may or may not
> have distinct corporate existence

Examples are:

* Government Ministries or Departments
* State-run Health organizations
* Police and fire departments

## Data

Data is stored in CSVs partitioned by country or region (e.g. EU). Directories
are named by ISO code.  

## Contribute

Please just add to the CSV file and submit a pull request or open an issue.

## Preparation

SQL to extract data from sqlite:

    .output entities.csv
    .mode csv
    .headers ON

    SELECT * FROM entity;

