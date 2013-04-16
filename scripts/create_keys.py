import sqlite3
import uuid

def make_random_key():
    return str(uuid.uuid4()).split('-')[-1]


if __name__ == '__main__':
    db = sqlite3.connect('bodies.db')
    db.row_factory = sqlite3.Row
    cur = db.execute("SELECT DISTINCT * FROM entity;")
    for row in list(cur.fetchall()):
        #if row['key'] is not None:
        #    continue
        key = "%s/%s" % (row['jurisdiction_code'].lower(),
                         make_random_key())
        print key, row['title'].encode('utf-8')
        cur = db.execute("UPDATE entity SET key = ? WHERE title = ? "
            "AND source_url = ?", (key, row['title'], row['source_url']))
        #import ipdb; ipdb.set_trace()
        db.commit()


