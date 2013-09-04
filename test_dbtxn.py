from pytest import fixture
from sqlite3 import connect, Connection


class counted_connection(Connection):
    def __init__(self, pool):
        super(counted_connection, self).__init__(pool.dbfile)
        self.pool = pool
        self.pool.conns += 1

    def close(self):
        self.pool.conns -= 1
        super(counted_connection, self).close()

class unlimited_pool(object):
    def __init__(self, dbfile):
        self.dbfile = dbfile
        self.conns = 0

        conn = connect(dbfile)
        cur = conn.cursor()
        cur.execute('''CREATE TABLE test (id INTEGER PRIMARY KEY,
                                          a INTEGER,
                                          b VARCHAR(15))''')
        cur.close()
        conn.commit()
        conn.close()

    def connection(self):
        return counted_connection(self)

@fixture
def pool(tmpdir):
    return unlimited_pool(str(tmpdir.join('test.db')))
