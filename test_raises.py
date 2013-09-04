from db_txn import db_execute, in_txn, for_recurse

from test_dbtxn import pool

from pytest import raises
from sqlite3 import OperationalError


@in_txn
def buggy_gen():
    raise ValueError()
    yield 0

def test_gen_raises(pool):
    with raises(ValueError):
        buggy_gen(pool)
        assert pool.conns == 0

@for_recurse
def buggy_recur():
    raise ValueError()
    yield 0

@in_txn
def call_buggy():
    with raises(ValueError):
        yield buggy_recur()

def test_recur_raises(pool):
    call_buggy(pool)
    assert pool.conns == 0

@in_txn
def bad_sql():
    with raises(OperationalError):
        yield db_execute('bad sql')

def test_bad_sql(pool):
    bad_sql(pool)
    assert pool.conns == 0
