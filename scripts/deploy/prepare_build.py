#/usr/bin/python3
"""Prepares the website for building with Jekyll. For each public body:

- creates a markdown file to be transformed by Jekyll into html
- creates a json file for downloading machine processable data of
  individual public body
"""
from typing import List
import os
import shutil
import csv
import logging
import json
import argparse

from slugify import slugify

DATA_DIR = "../../data"
WEBSITE_DIR = "../../website"
BODY_TEMPLATE = \
"""---
layout: body
permalink: {}
---

"""

def list_data_files(data_dir: str) -> List[str]:
    """Returns a list of data files to process.

    Args:
        data_dir (str): Path to the original data files.

    Returns:
        List[str]: List of data files.
    """
    return (file
        for file in os.listdir(data_dir) if file.endswith('.csv'))

def copy_data_files(data_dir: str, website_dir: str):
    """Copies the data files to the website _data subfolder for processing
    by Jekyll.

    Args:
        data_dir (str): Path to the original data files.
        website_dir (str): Path to the Jekyll source files.
    """
    for file in list_data_files(data_dir):
        logging.info('Copying data file "%s"...', file)
        shutil.copy2(
            os.path.join(data_dir,file),
            os.path.join(website_dir, "_data"))

def generate_files_public_bodies(
    data_dir: str,
    website_dir: str,
    max_name_size: int,
    max_bodies_per_jurisdiction: int,
    body_template: str):
    """Generates the markdown and json files for each individual
    public body.

    Args:
        data_dir (str): Path to the original data files.
        website_dir (str): Path to the Jekyll source files.
        max_name_size (int): Maximum size for file names.
        max_bodies_per_jurisdiction (int): Maximum number of bodies to
            generate files to per jurisdiction. May be necessary for
            performance reasons.
        body_template (str): Template for the markdown files.
    """
    for data_file in list_data_files(data_dir):
        csv_filename = os.path.join(website_dir, "_data", data_file)
        with open(csv_filename, "r") as csv_file:
            row_reader = csv.DictReader(csv_file)
            generated_count = 0
            for row in row_reader:
                if not row["id"]:
                    continue # skip rows with empty ids
                jurisdiction, body_id = row["id"].split("/", maxsplit=1)
                generated_count += 1
                if generated_count > max_bodies_per_jurisdiction:
                    logging.info('Jurisdiction "%s" exceeded the public body'
                        ' limit of %d. Skipping further file generation.',
                        jurisdiction, max_bodies_per_jurisdiction)
                    break # do not generate files past the count limit
                body_id = slugify(body_id)[:max_name_size]
                jurisdiction_path = os.path.join(website_dir, jurisdiction)
                try:
                    os.mkdir(jurisdiction_path)
                    logging.info('Created directory "%s"...', jurisdiction)
                except FileExistsError:
                    pass
                md_filename = f"{body_id}.md"
                with open(os.path.join(jurisdiction_path, md_filename),
                    "w") as md_file:
                    md_file.write(
                        body_template.format(f"{jurisdiction}/{body_id}/"))
                json_filename = f"{body_id}.json"
                with open(os.path.join(jurisdiction_path, json_filename),
                    "w") as json_file:
                    json.dump(row, json_file)

def parse_cli() -> int:
    """Parses the command line interface.

    Returns:
        int: The maximum number of bodies per jurisdiction.
    """
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('--max_bodies_per_jurisdiction',
        help='The maximum number of bodies per jurisdiction.',
        default='100',
        nargs='?',
    )

    args = parser.parse_args()

    return int(args.max_bodies_per_jurisdiction)

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    max_bodies_per_jurisdiction = parse_cli()
    copy_data_files(DATA_DIR, WEBSITE_DIR)
    generate_files_public_bodies(
        data_dir=DATA_DIR,
        website_dir=WEBSITE_DIR,
        max_name_size=250,
        max_bodies_per_jurisdiction=max_bodies_per_jurisdiction,
        body_template=BODY_TEMPLATE)
