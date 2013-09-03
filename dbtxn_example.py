from __future__ import print_function

from db_txn import db_execute, db_insert, db_query, db_result, for_recurse, \
                   in_txn

import MySQLdb


'''
  There should be a MySQL server listening on the localhost. There should be a
  user named 'test' without password, being able to access a db also named
  'test'.

  There should be table named, suprisingly, 'test' in the db, which looks like:
    CREATE TABLE test (id INT PRIMARY KEY AUTO_INCREMENT, a INT, b VARCHAR(15));
'''

@for_recurse
def insert_db():
    row_count, row_id = yield db_insert('INSERT INTO test(a, b) VALUES(%s, %s)',
                                        1, '2')
    assert row_count > 0
    yield db_result(row_id)

@in_txn
def update_db():
    row = yield insert_db()
    row_count, _ = yield db_execute('UPDATE test SET a = 3 WHERE id = %s', row)
    assert row_count > 0
    yield db_result(row)

@in_txn
def query_db(row):
    row_count, rows = yield db_query('SELECT a, b FROM test WHERE id = %s', row)
    assert row_count > 0
    row = rows[0]
    yield db_result(row.a, row.b)

class test_pool(object):
    def connection(self):
        return MySQLdb.connect(user='test', db='test')

row = update_db(test_pool())
a, b = query_db(test_pool(), row)

print('row selected: a =', a, ', b =', b)
