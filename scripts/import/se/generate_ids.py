# -*- coding: utf-8 -*-

def generate_ids(infile, outfile):
    from csv import DictReader, DictWriter
    from simpleslugger import make_slug

    with open(infile, "r") as f:
        reader = DictReader(f)
        fieldnames = [fieldname.decode("utf-8") for fieldname in reader.fieldnames]

        with open(outfile, "w") as g:
            writer = DictWriter(g, fieldnames=fieldnames)

            # write the first line (field names)
            writer.writerow(dict((fn, fn) for fn in fieldnames))

            for row in reader:
                row[u"id"] = u"se/%s" % make_slug(row[u"name"].decode("utf-8"))
                writer.writerow(dict((fieldname, row[fieldname]) for fieldname in fieldnames))

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print "Generates slug-like ids on the first column of a csv file,"
        print " based on the contents of the 'name' column."
        print "Usage: %s [filename] [outfile] [domainfilename]" % sys.argv[0]
        print "       infile: input filename"
        print "       outfile: input filename"
    else:
        infile, outfile = sys.argv[1], sys.argv[2]
        generate_ids(infile, outfile)
