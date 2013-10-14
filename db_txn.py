from collections import namedtuple
from contextlib import closing
from functools import partial


DONE = 0
QUERY = 1
EXECUTE = 2                   # can insert, but won't report insert id
INSERT = 3
RECURSE = 4                     # recursive generator

def db_result(*val, **named):
    assert len(val) == 0 or len(named) == 0
    if len(val) == 1:
        return (DONE, val[0])
    elif len(val) > 1:
        return (DONE, val)
    elif len(named) != 0:
        t = namedtuple('_', named.keys())
        return (DONE, t(**named))
    else:
        return (DONE, None)

def db_input(t, sql, *args):
    return (t, (sql, args))

db_query = partial(db_input, QUERY)
db_execute = partial(db_input, EXECUTE)
db_insert = partial(db_input, INSERT)

def db_recurse(g):
    return (RECURSE, g)

def for_recurse(f):
    def wrapper(*args, **kwargs):
        return db_recurse(f(*args, **kwargs))
    return wrapper

class _NextIteration(BaseException):
    def __init__(value):
        super(_NextIteration, self).__init__()
        self.value = value

def _exec(cur, g):
    def _run_for_gen(f, *args, **kwargs):
        try:
            return f(*args, **kwargs)
        except StopIteration:
            raise
        except Exception as e:
            raise _NextIteration(g.throw(type(e), e))

    what, val = next(g)
    while True:
        try:
            if what == DONE:
                g.close()
                return val
            elif what == RECURSE:
                try:
                    r = _run_for_gen(_exec, cur, val)
                except StopIteration:
                    r = None
                what, val = g.send(r)
            else:
                sql, args = val
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
                what, val = g.send((rowc, rs))
        except _NextIteration as e:
            what, val = e.value

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
        except StopIteration:  # no val to return
            conn.commit()
            return None

def in_txn(f):
    def wrapper(pool, *args, **kwargs):
        return db_txn(pool, f, *args, **kwargs)
    return wrapper
