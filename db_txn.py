from collections import namedtuple
from functools import partial

DONE = 0
QUERY = 1
EXECUTE = 2  # can insert, but won't report insert id
INSERT = 3


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

def db_txn(pool, gen):
    g = gen()
    conn = pool.connection()
    try:
        cur = conn.cursor()
        what, val = g.next()
        while True:
            if what == DONE:
                cur.close()
                conn.commit()
                conn.close()
                return val
            else:
                sql, args = val
                cur.execute(sql, args)
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
    except StopIteration:  # no val to return
        cur.close()
        conn.commit()
        conn.close()
    except:
        conn.rollback()
        conn.close()
        raise
