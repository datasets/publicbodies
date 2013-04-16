import csv
import sys
import os
import datetime

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

import unicodedata
def strip_accents(s):
    s = s.decode('utf8')
    out = ''.join(c for c in unicodedata.normalize('NFD', s)
        if unicodedata.category(c) != 'Mn')
    return out.encode('utf8')

if __name__ == '__main__':
    if len(sys.argv) >= 2:
        path = sys.argv[1]
        normalize(path)
    else:
        for c in ['de', 'eu', 'gb']:
            normalize(os.path.join('data', c + '.csv'))

