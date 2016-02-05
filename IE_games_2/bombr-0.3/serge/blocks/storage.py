"""

Classes to help with storage of detailed information about a
game in sql tables.

This is good for high scores, achievements etc.

The objects here allow persisting between versions and
handle schema updates to the tables.

"""

import sqlite3
import sys
import os

import serge.common

class ConnectionError(Exception): """Could not connect to database"""


class Storage(serge.common.Loggable):
    """The main storage object"""

    def __init__(self, name, path=None):
        """Initialise the storage"""
        self.addLogger()
        #
        # Find the place to put the database file
        if not path:
            var = 'HOME' if not sys.platform.startswith('win') else 'HOMEPATH'
            path = os.getenv(var)
        #
        # Connect to, or create, the database file
        filename = os.path.join(path, name)
        try:
            self.db = sqlite3.connect(filename)
        except Exception, err:
            raise ConnectionError('Could not connect to storage database "%s": %s' % (filename, err))
        #
        self.cursor = self.db.cursor()

    def addTable(self, name, sql):
        """Add a new table"""
        #
        # Do not do this if the table already exists
        try:
            self.get('select * from %s' % name)
        except sqlite3.OperationalError:
            self.cursor.execute(sql)
        else:
            pass # Table is there - ok

    def addDefaultRows(self, table_name, row_key, rows, override=False):
        """Add some default rows to the database

        The row_key specifies which of the columns is used as the key. If a row
        already exists in the database with that key then the default row will
        not be added.

        The rows is a list of lists of values. The row_key is in the first position.

        """
        for row in rows:
            if override:
                self.cursor.execute(
                    ('delete from %s where %s=?' % (table_name, row_key)),
                    (row[0],))
            existing = self.get(('select * from %s where %s=?' % (table_name, row_key)), (row[0],))
            if not existing:
                self.cursor.execute(
                    ('insert into %s values (%s)' % (table_name, ', '.join(['?']*len(row)))),
                    row)

    def get(self, sql, params=None):
        """Return results"""
        self.cursor.execute(sql, params if params else [])
        results = self.cursor.fetchall()
        return results

    def save(self):
        """Save the current database"""
        self.db.commit()

    def close(self):
        """Close the database"""
        self.cursor.close()
        self.db.close()