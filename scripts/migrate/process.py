import csv
import sys
import os
import json
import datetime

# migrate data as per https://github.com/okfn/publicbodies/issues/29
def migrate29(path):
    fo = open(path) 
    reader = csv.DictReader(fo)
    fields = reader.fieldnames
    schema = json.load(open('datapackage.json'))['resources'][0]['schema']
    newfields = [ f['id'] for f in schema['fields'] ]
    mapfields = {
        'title': 'name',
        'abbr': 'abbreviation',
        'key': 'id',
        'category': 'classification',
        'parent_key': 'parent_id',
        }
    def migraterow(row):
        for key in mapfields:
            outkey = mapfields[key]
            row[outkey] = row[key]
        for key in row.keys():
            if key not in newfields:
                del row[key]
        return row
    
    newrows = [ migraterow(row) for row in reader ]
    fo.close()
    writer = csv.DictWriter(open(path, 'w'), newfields, lineterminator='\n')
    writer.writeheader()
    writer.writerows(newrows)

## Older

def normalize(path):
    fo = open(path) 
    reader = csv.DictReader(fo)
    fields = reader.fieldnames
    newrows = [ normalize_dates(r) for r in reader ]
    newrows = [ normalize_keys_2(r) for r in newrows ]
    fo.close()
    writer = csv.DictWriter(open(path, 'w'), fields, lineterminator='\n')
    writer.writeheader()
    writer.writerows(newrows)
   
def normalize_dates(row):
    format_ = '%a %b %d %X %Z %Y'
    for f in ['created_at', 'updated_at']:
        if row[f]:
            d = datetime.datetime.strptime(row[f], format_)
            row[f] = datetime.date(d.year, d.month, d.day).isoformat()
    return row

def normalize_keys_2(row):
    if not row['key']:
        key = row['abbr'] if row['abbr'] else row['title']
        row['key'] = row['jurisdiction_code'].lower() + '/' + generate_slug(key)
    parts = row['key'].split('/')
    row['key'] = parts[0] + '/' + parts[1].replace('_', '-')
    return row

def normalize_keys(path):
    out = [];
    fo = open(path) 
    reader = csv.DictReader(fo)
    fields = reader.fieldnames
    for row in reader:
        newrow = dict(row)
        slug = row['slug']
        if not slug:
            slug = generate_slug(row['title'])
        newrow['key'] = row['key'].split('/')[0] + '/' + slug
        del newrow['slug']
        out.append(newrow) 
    fo.close()
    fields = [ f for f in fields if f != 'slug' ]
    writer = csv.DictWriter(open(path, 'w'), fields, lineterminator='\n')
    writer.writeheader()
    writer.writerows(out)

def generate_slug(title):
    slug = strip_accents(title)
    slug = slug.lower()
    slug = slug.strip().replace('.', '')
    slug = slug.replace('/', ' ')
    slug = slug.replace(' ', '-')
    slug = slug.replace('- ', '-')
    slug = slug.replace('--', '-')
    slug = slug.replace('(', '').replace(')', '')
    return slug

import unicodedata
def strip_accents(s):
    s = s.decode('utf8')
    out = ''.join(c for c in unicodedata.normalize('NFD', s)
        if unicodedata.category(c) != 'Mn')
    return out.encode('utf8')

if __name__ == '__main__':
    usage = 'process.py {action} ...'
    if not len(sys.argv) > 1:
        print(usage)
        sys.exit(0)

    jurisdictions = ['br', 'ch', 'de', 'eu', 'gb', 'gr', 'nz', 'us']

    action = sys.argv[1]
    if action == 'migrate29':
        if len(sys.argv) > 2:
            migrate29(sys.argv[2])
        else:
            for j in jurisdictions:
                print('Processing %s' % j)
                migrate29(os.path.join('data', '%s.csv' % j))
    elif action == 'normalize':
        if len(sys.argv) > 2:
            path = sys.argv[2]
            normalize(path)
        else:
            for c in ['de', 'eu', 'gb']:
                normalize(os.path.join('data', c + '.csv'))
    else:
        print(usage)

