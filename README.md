python-dbtxn
============

Generator based, hassle free db accessing layer over python dbi.

Python dbi is not abstract enough. The business logic does not need to know about
the database connection or even the cursor object. It should only know the SQLs
and the data. And python-dbtxn only lets it know just that.

Generators are definitely better than callbacks with cursor object as argument,
as the callback has no chance to accidentally close the cursor.

Generators are also better than callbacks given a closure hiding the cursor
inside. It's much simpler to write a mock of db_txn() yielding back predefined
result sets one after than another, than make the closure decide which result set
to return each time.

With the in_txn decorators, the generators can be invoked and return like
ordinary functions.

With the for_recurse decorator, the generators can be called recursively within
another generator without looking too different.

The example demonstrates the use of all SQL execution methods (query, insertion,
and other forms of execution). Leaving the db_ prefixed functions there makes
the expected result type more obvious, especially when SQLs are given as variable
names.

```python
r = yield db_query(AUTH_USER, username, passwd)
```

is easy to recognize as a query. Therefore, the library is not going to parse
the SQL and automatically decide what to return.
