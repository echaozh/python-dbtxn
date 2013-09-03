python-dbtxn
============

Generator based, hassle free db accessing layer over python dbi.

Python dbi is not abstract enough. The business logic does not need to know about
the database connection or even the cursor object. It should only know the SQLs
and the data. And python-dbtxn only lets it know just that.

Usage:

```python
row_count, _ = yield db_execute(SQL, arg1, arg2, ...)
```

Executes a SQL statement and reports back the number of affected rows.

```python
row_count, row_id = yield db_insert(SQL, arg1, arg2, ...)
```

Executes an INSERT statement and reports back the number of affected rows, and
the ID of the row inserted last.

```python
row_count, result_set = yield db_query(SQL, arg1, arg2, ...)
```

Executes a SELECT statement and reports back the number of affected rows, as well
as the result set as a list of collections.namedtuple. Note the column names will
be used as tuple field names, so they have to be a valid identifier, or be
aliased to be one.

```python
@in_txn
def sql_generator(args):
    yield db_execute(SQL, args)
    yield db_result(results)

results = sql_generator(pool, args)
```

Decorates a SQL generator to be directly callable with a connection pool and
arguments required by the original generator.

```python
@for_recurse
def inner_generator(args):
    yield db_execute(SQL, args)
    yield db_result(results)

@in_txn
def outer_generator(args):
    yield inner_generator(args)
    yield db_execute(SQL, args)
    yield db_result(results)
```

Decorates a SQL generator to be directly callable within another generator.

dbtxn_example.py demonstrates the use of all functions and decorators defined in
the library.
