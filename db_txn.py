from collections import namedtuple
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

def _exec(cur, g):
    what, val = g.next()
    while True:
        if what == DONE:
            g.close()
            return val
        elif what == RECURSE:
            try:
                r = _exec(cur, val)
            except StopIteration:
                r = None
            except Exception as e:
                what, val = g.throw(type(e), e)
                continue
            what, val = g.send(r)
        else:
            sql, args = val
            try:
                cur.execute(sql, args)
            except Exception as e:
                what, val = g.throw(type(e), e)
                continue

            rowc = cur.rowcount
            rs = None
            if what == QUERY:
                rows = cur.fetchall()
                cols = [c[0] for c in cur.description]
                nt = namedtuple('_', cols)
                rs = [nt(*list(r)) for r in rows]
            elif what == INSERT:
                rs = cur.lastrowid
            what, val = g.send((rowc, rs))

def db_txn(pool, gen, *args, **kwargs):
    g = gen(*args, **kwargs)
    conn = pool.connection()
    cur = conn.cursor()
    commit = True
    try:
        return _exec(cur, g)
    except StopIteration:  # no val to return
        pass
    except:
        commit = False
        raise
    finally:
        cur.close()
        if commit:
            conn.commit()
        else:
            conn.rollback()
        conn.close()

def in_txn(f):
    def wrapper(pool, *args, **kwargs):
        return db_txn(pool, f, *args, **kwargs)
    return wrapper
