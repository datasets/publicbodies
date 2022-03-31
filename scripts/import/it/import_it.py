"""Imports Italian public body data from the official sources.

* https://indicepa.gov.it/ipa-dati/dataset/amministrazioni
* https://indicepa.gov.it/ipa-dati/dataset/enti

Both contain the same data, but use different schemas. Only the first one
is enabled at the moment. The second is kept as a backup data source, in
case it is needed in the future.
"""

# dependencies
# standard library
import os
import argparse
import logging
from urllib.parse import urlparse

# packages
import requests
import pandas as pd
import requests
from slugify import slugify
from frictionless import Schema

# Script parameters
# Acronyms used: ipa -> indicePa , pbo -> publicbodies.org
# URLs of the data in indicepa dataset
DATASETS = {
    'amministrazioni': {
        'url': 'https://indicepa.gov.it/ipa-dati/dataset/502ff370-1b2c-4310-94c7-f39ceb7500e3/resource/3ed63523-ff9c-41f6-a6fe-980f3d9e501f/download/amministrazioni.txt',
        'delimiter': '\t',
    },
    # The dataset below is now disabled for now (see docstring).
    # 'enti':  {
    #     'url': 'https://indicepa.gov.it/ipa-dati/datastore/dump/d09adf99-dc10-4349-8c53-27b1e5aa97b6?bom=True',
    #     'delimiter': ',',
    # }
}

# config for making requests
USER_AGENT = 'PublicBodiesBot (https://github.com/okfn/publicbodies)'
SCHEMA_PATH = os.path.join(
    os.path.dirname(os.path.abspath((__file__))),
    '..', '..', '..',
    'public-body-schema.json')

# sets up the level of logging to print to the terminal
logging.basicConfig(level=logging.INFO)

def cleanup_url(url: str) -> str:
    'Fixes a URL value.'
    if isinstance(url, str) and url:
        parsed = urlparse(url)
        if not parsed.scheme: # some don't have the scheme part
            url = f'https://{url}'
        else:
            url = parsed.geturl()
    return url

def get_table(url: str, delimiter: str) -> pd.DataFrame:
    'Downloads and processes a table.'
    logging.info(f'Downloading and parsing table from "{url}"...')
    table = pd.read_csv(
        url,
        storage_options={'User-Agent': USER_AGENT},
        sep=delimiter,
        na_values='null',
    )

    # Categories of public bodies to skip during import (for now Schools)
    not_wanted_categories = ['Istituti di Istruzione Statale di Ogni Ordine e Grado']
    table = table[~table.tipologia_istat.isin(not_wanted_categories)].copy()

    # cleaning ulrs
    table['sito_istituzionale'] = (
        table['sito_istituzionale']
        .str.replace(',', '.')
        .apply(cleanup_url)
    )

    # derived columns
    table['id'] = table['des_amm'].apply(lambda s: f'it/{slugify(s)}')
    table['jurisdiction_code'] = 'IT'
    table['source_url'] = table['cod_amm'].apply(
        lambda s: f'http://www.indicepa.gov.it/ricerca/n-dettaglioamministrazione.php?cod_amm={s}')
    table['address'] = table.apply(
        lambda v:
        (v.Indirizzo.replace(',', " ") +
            f' - {v.Cap} {v.Comune} ({v.Provincia}) Italy'),
        axis=1)

    # renamed columns
    table.rename(
        columns={
            'des_amm': 'name',
            'acronimo': 'abbreviation',
            'tipologia_istat': 'classification',
            'sito_istituzionale': 'url',
            'mail1': 'email',
        },
        inplace=True)

    # get table schema
    schema = Schema(SCHEMA_PATH)

    # create columns missing from schema as empty columns
    for column in schema.field_names:
        if column not in table.columns:
            table[column] = None

    # return the dataframe with expected columns
    return table.loc[:,schema.field_names].copy()

def import_it_data(datasets: dict, output_path: str):
    'Imports data for Italy.'
    schema = Schema(SCHEMA_PATH)
    table = pd.DataFrame(columns=schema.field_names)
    for dataset, properties in datasets.items():
        logging.info(f'Downloading and processing dataset "{dataset}"...')
        table = pd.concat((
            table,
            get_table(properties['url'], properties['delimiter'])))
    table.to_csv(output_path, index=False)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__
    )
    parser.add_argument(
        '--output',
        help='filename for the data output as CSV',
        metavar='file_name',
        default='it.csv'
    )
    args = parser.parse_args()

    import_it_data(DATASETS, args.output)
