#/usr/bin/python3
"""Prepares the website for building with Jekyll. For each public body:

- creates a markdown file to be transformed by Jekyll into html
- creates a json file for downloading machine processable data of
  individual public body
"""
import os, shutil
import csv
import logging
import json

from slugify import slugify

# directories
DATA_DIR = "../../data"
WEBSITE_DIR = "../../website"
MAX_NAME_SIZE = 250 # limit from Linux ext4 file system, minus extension
BODY_TEMPLATE = \
"""---
layout: body
permalink: {}
---

"""

logging.getLogger().setLevel(logging.INFO)

# copy data files to website
data_files = [file for file in os.listdir(DATA_DIR) if file.endswith('.csv')]

for file in data_files:
    logging.info('Copying data file "%s"...', file)
    shutil.copy2(
        os.path.join(DATA_DIR,file),
        os.path.join(WEBSITE_DIR, "_data"))

# generate files for individual public bodies
for data_file in data_files:
    csv_filename = os.path.join(WEBSITE_DIR, "_data", data_file)
    with open(csv_filename, "r") as csv_file:
        row_reader = csv.DictReader(csv_file)
        for row in row_reader:
            if not row["id"]:
                continue # skip rows with empty ids
            jurisdiction, body_id = row["id"].split("/", maxsplit=1)
            body_id = slugify(body_id)[:MAX_NAME_SIZE]
            jurisdiction_path = os.path.join(WEBSITE_DIR, jurisdiction)
            try:
                os.mkdir(jurisdiction_path)
                logging.info('Created directory "%s"...', jurisdiction)
            except FileExistsError:
                pass
            md_filename = f"{body_id}.md"
            with open(os.path.join(jurisdiction_path, md_filename),
                "w") as md_file:
                md_file.write(
                    BODY_TEMPLATE.format(f"{jurisdiction}/{body_id}/"))
            json_filename = f"{body_id}.json"
            with open(os.path.join(jurisdiction_path, json_filename),
                "w") as json_file:
                json.dump(row, json_file)
