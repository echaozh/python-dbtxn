import sys
sys.path.append('../')

from db_txn_yield_from import db_execute, db_insert, db_query, in_txn

from test_dbtxn import pool


def insert_row():
    row_count, row_id = yield db_insert('INSERT INTO test(a, b) VALUES(?, ?)',
                                        1, '2')
    assert row_count == 1
    return row_id

@in_txn
def update_row():
    row = yield from insert_row()
    row_count, _ = yield db_execute('UPDATE test SET a = 3 WHERE id = ?', row)
    assert row_count == 1
    return row

def delete_row(row):
    row_count, _ = yield db_execute('DELETE FROM test WHERE id = ?', row)
    assert row_count == 1

@in_txn
def query_row(row):
    row_count, rows = yield db_query('SELECT a, b FROM test WHERE id = ?', row)
    assert row_count == 1
    r = rows[0]
    yield from delete_row(row)
    return (r.a, r.b)

def test_success(pool):
    row = update_row(pool)
    assert row == 1
    a, b = query_row(pool, row)
    assert a == 3 and b == '2'
    assert pool.conns == 0
