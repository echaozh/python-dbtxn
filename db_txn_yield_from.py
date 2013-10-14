from collections import namedtuple
from contextlib import closing
from functools import partial


QUERY = 1
EXECUTE = 2                   # can insert, but won't report insert id
INSERT = 3

def db_input(t, sql, *args):
    return (t, sql, args)

db_query = partial(db_input, QUERY)
db_execute = partial(db_input, EXECUTE)
db_insert = partial(db_input, INSERT)

class _NextIteration(BaseException):
    def __init__(value):
        super(_NextIteration, self).__init__()
        self.value = value

def _exec(cur, g):
    def _run_for_gen(f, *args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            raise _NextIteration(g.throw(type(e), e))

    what, sql, args = next(g)
    while True:
        try:
            _run_for_gen(cur.execute, sql, args)
            rowc = cur.rowcount
            rs = None
            if what == QUERY:
                rows = _run_for_gen(cur.fetchall)
                cols = [c[0] for c in cur.description]
                nt = namedtuple('_', cols)
                rs = [nt(*list(r)) for r in rows]
                rowc = len(rs)
            elif what == INSERT:
                rs = cur.lastrowid
            what, sql, args = g.send((rowc, rs))
        except _NextIteration as e:
            what, sql, args = e.value

def db_txn(pool, gen, *args, **kwargs):
    g = gen(*args, **kwargs)
    with closing(pool.connection()) as conn:
        try:
            conn.begin()
        except AttributeError:
            pass

        try:
            with closing(conn.cursor()) as cur:
                res = _exec(cur, g)
                conn.commit()
                return res
        except StopIteration as e:
            conn.commit()
            return e.value

def in_txn(f):
    def wrapper(pool, *args, **kwargs):
        return db_txn(pool, f, *args, **kwargs)
    return wrapper
