from db_txn import db_execute, db_insert, db_query, db_result, db_txn

import MySQLdb


'''
  There should be a MySQL server listening on the localhost. There should be a
  user named 'test' without password, being able to access a db also named
  'test'.

  There should be table named, suprisingly, 'test' in the db, which looks like:
    CREATE TABLE test (id INT PRIMARY KEY AUTO_INCREMENT, a INT, b VARCHAR(15));
'''

def insert_db():
    row_count, row_id = yield db_insert('INSERT INTO test(a, b) VALUES(%s, %s)',
                                        1, '2')
    assert row_count > 0
    yield db_result(row_id)

def update_db(row):
    row_count, _ = yield db_execute('UPDATE test SET a = 3 WHERE id = %s', row)
    assert row_count > 0

def query_db(row):
    row_count, rows = yield db_query('SELECT a, b FROM test WHERE id = %s', row)
    assert row_count > 0
    row = rows[0]
    yield db_result(row.a, row.b)

class test_pool(object):
    def connection(self):
        return MySQLdb.connect(user='test', db='test')

row = db_txn(test_pool(), insert_db)
db_txn(test_pool(), update_db, row)
a, b = db_txn(test_pool(), query_db, row)

print 'row selected: a =', a, ', b =', b

