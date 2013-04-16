import csv
import sys
import os

def normalize(path):
    out = [];
    fo = open(path) 
    reader = csv.DictReader(fo)
    fields = reader.fieldnames
    for row in reader:
        newrow = dict(row)
        slug = row['slug']
        if not slug:
            slug = row['title']
            slug = strip_accents(slug)
            slug = slug.lower()
            slug = slug.strip().replace('.', '')
            slug = slug.replace('/', ' ')
            slug = slug.replace(' ', '-')
            slug = slug.replace('- ', '-')
            slug = slug.replace('--', '-')
        newrow['key'] = row['key'].split('/')[0] + '/' + slug
        del newrow['slug']
        out.append(newrow) 
    fo.close()
    fields = [ f for f in fields if f != 'slug' ]
    writer = csv.DictWriter(open(path, 'w'), fields, lineterminator='\n')
    writer.writeheader()
    writer.writerows(out)

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

