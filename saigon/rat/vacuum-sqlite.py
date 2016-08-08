"""
from: http://www.djangosnippets.org/snippets/234/
description: This script can be run periodically (e.g. as a nightly cronjob) to keep a SQLite database with high churn from growing unnecessarily large.

Modified for RAT environment.
Run this script in the rat directory.

Example:

    vacuum-sqlite.py

"""
from ratenv import *

def vacuum_db():
    from django.db import connection
    cursor = connection.cursor()
    cursor.execute("VACUUM")
    connection.close()

if __name__ == "__main__":
    print "Vacuuming database..."
    before = os.stat(settings.DATABASE_NAME).st_size
    print "Size before: %s bytes" % before
    vacuum_db()
    after = os.stat(settings.DATABASE_NAME).st_size
    print "Size after: %s bytes" % after
    print "Reclaimed: %s bytes" % (before - after)
