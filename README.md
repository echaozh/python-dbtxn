python-dbtxn
============

Generator based, hassle free db accessing layer over python dbi.

ORM is not always useful. When you're not writing a thin wrapper over the database tables, it is more often than not you're only accessing some of the fields, or joining multiple tables at the same time. Also, code mapping tables to objects may be too much trouble for your simple use case.

When using python dbi directly, you cannot avoid duplicate code. You have to create a connection, and then a cursor, hold them in your hand as long as you're accessing the database, and then destroy it, and the connection with it, committing or rolling back depending on the occasion. Python dbi may be an interface facade over various ugly vendor-specific low level connectors, but it is still not the easiest tool to wield, especially in lightweight code. 

The database accessing code should mind its SQLs and data processing logic, but not the database accessing details. The details are boilerplate code and can be hidden from business logic. And db_txn is my answer to this problem.

SQLs and business logic go into generators, which generates SQLs and SQL parameters to the db_txn() function, which then feeds back the execution result. To make things simpler and more transparent, the generator tells db_txn() what it's doing, querying and expecting a result set, inserting and expecting a row id, or executing without expecting only the affected row count. Also, the return value is yielded with a specific tag.

To me yielding is better than callbacks with cursor as argument. There is no abstraction leak, say the generator can never accidentally closes the cursor. Passing in a closure holding the cursor is another option, but it's still uglier to me.

The generator interface has one weakness, and that is recursive generators. SQLs yielded back from callee generators have to be yielded to db_txn() in each layer. The calling generator code will be hard to get right, and people will never try it given the amount of code that does nothing meaningful. Directly yielding back generators and let db_txn() to resolve may be a much better idea. I will try it out later.
