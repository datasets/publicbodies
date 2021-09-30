"Fixes url columns by converting domain names to clean urls."

from urllib.parse import urlsplit, urlunsplit
import re
import argparse

import pandas as pd
from frictionless import Package

domain_re = re.compile(
    r'([a-z0-9A-Z]\.)*[a-z0-9-]+'
    r'\.([a-z0-9]{2,24})+(\.co\.([a-z0-9]{2,24})|\.([a-z0-9]{2,24}))')

def domain_to_url(domain: str) -> str:
    "Converts a domain name to a full url."
    return urlunsplit(urlsplit(f'//{domain}', scheme='https'))

class JurisdictionData:
    "Data from a given jurisdiction."

    def _get_jurisdiction_df(self) -> pd.DataFrame:
        "Get a pandas dataframe for a given jurisdiction code."
        package = Package('../../datapackage.json')
        self.resource = package.get_resource(self.jurisdiction_code)
        return pd.read_csv(self.resource.fullpath)

    def _save_jurisdiction_df(self, file_name: str):
        "Save a pandas dataframe for a given jurisdiction code."
        self.df.to_csv(file_name, index=False)

    def __init__(self, jurisdiction_code: str):
        self.jurisdiction_code = jurisdiction_code
        self.df = self._get_jurisdiction_df()

    def save(self, file_name: str = None):
        """Saves the contents of the dataframe to the resource or to a
        provided csv file."""
        self._save_jurisdiction_df(
            file_name if file_name else self.resource.fullpath)

def fix_url(df: pd.DataFrame) -> pd.DataFrame:
    "Fixes the url column in a given datafame."
    # remove extra spaces
    df['url'] = df['url'].str.strip()
    domain_lines = (df.url.notna() & df.url.str.match(domain_re))
    df.loc[domain_lines, 'url'] = df[domain_lines]['url'].apply(domain_to_url)
    return df

def fix_csv(jurisdiction_code: str):
    "Fixes the url column in a csv file with a given jurisdiction code."
    data = JurisdictionData(jurisdiction_code)
    data.df = fix_url(data.df)
    data.save()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__
    )
    parser.add_argument(
        "jurisdiction_code",
        help=fix_csv.__doc__,
        nargs=1,
        metavar="JURISDICTION_CODE"
    )

    args = parser.parse_args()
    if args.jurisdiction_code:
        fix_csv(args.jurisdiction_code[0])
    else:
        parser.print_help()
