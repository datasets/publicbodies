import csv
import sys
path = sys.argv[1]

def normalize():
    out = [];
    fo = open(path) 
    reader = csv.DictReader(fo)
    fields = reader.fieldnames
    for row in reader:
        newrow = dict(row)
        slug = row['slug']
        if slug:
            pass
        else:
            slug = row['title'].strip().replace('.', '')
        out.append(newrow) 
    fo.close()
    writer = csv.DictWriter(open(path, 'w'), fields, lineterminator='\n')
    writer.writeheader()
    writer.writerows(out)

if __name__ == '__main__':
    normalize()

