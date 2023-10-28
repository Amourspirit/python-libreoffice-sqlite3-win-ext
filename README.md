<p align="center">
<img src="https://user-images.githubusercontent.com/4193389/278824380-7ac5360b-4d46-4563-bafe-85865c147d05.png" alt="Sqlite3 Extension Logo" width="174" height="174">
</p>

# Sqlite3 for LibreOffice

The sqlite3 module is a powerful part of the Python standard library; it lets us work with a fully featured on-disk SQL database without installing any additional software.

This extension add sqlite3 support to LibreOffice.

The extension can be found in the [dist](./dist) folder.

## Example:

Ths extension includes `SqlCtx` which is a context manager that handles the opening and closing of the database connection. It also includes a `cursor` attribute that references a cursor object that we can use to execute SQL queries.

The following example can be run in the [APSO](https://extensions.libreoffice.org/en/extensions/show/apso-alternative-script-organizer-for-python) python console.

The demo create a database in the user's home directory called `test.db` and creates a table called `fish` with three columns: `name`, `species`, and `tank_number`. It then adds two rows of data to the table, and then reads the data back out. It then modifies the data in the table, and then deletes one of the rows.

```python
>>> from sql_util import SqlCtx
>>> from pathlib import Path
>>> cs = Path.home() / "Documents/test.db"

# Creating a Connection to a SQLite Database
>>> with SqlCtx(cs) as db:
...     print(db.connection.total_changes)
... 
0

# Creating a table in the database
>>> with SqlCtx(cs) as db:
...     _ = db.cursor.execute("CREATE TABLE fish (name TEXT, species TEXT, tank_number INTEGER)")
... 


# Adding Data to the SQLite Database
>>> with SqlCtx(cs) as db:
...     with db.connection:
...         _ = db.cursor.execute("INSERT INTO fish VALUES ('Sammy', 'shark', 1)")
...         _ = db.cursor.execute("INSERT INTO fish VALUES ('Jamie', 'cuttlefish', 7)")
...     print(db.connection.total_changes)
... 
2

# Reading Data from the SQLite Database
>>> with SqlCtx(cs) as db:
...     rows = db.cursor.execute("SELECT name, species, tank_number FROM fish").fetchall()
...     for row in rows:
...         for key in row.keys():
...             print(f"{key} = {row[key]}")
... 
name = Sammy
species = shark
tank_number = 1
name = Jamie
species = cuttlefish
tank_number = 7

>>> with SqlCtx(cs) as db:
...     target_fish_name = "Jamie"
...     rows = db.cursor.execute(
...         "SELECT name, species, tank_number FROM fish WHERE name = ?",
...         (target_fish_name,),
...     ).fetchall()
...     for row in rows:
...         for key in row.keys():
...             print(f"{key} = {row[key]}")
... 
name = Jamie
species = cuttlefish
tank_number = 7


# Modifying Data in the SQLite Database
>>> with SqlCtx(cs) as db:
...     new_tank_number = 2
...     moved_fish_name = "Sammy"
...     with db.connection:
...         _ = db.cursor.execute("UPDATE fish SET tank_number = ? WHERE name = ?", (new_tank_number, moved_fish_name))
...         rows = db.cursor.execute("SELECT name, species, tank_number FROM fish").fetchall()
...         for row in rows:
...             for key in row.keys():
...                 print(f"{key} = {row[key]}")
... 
name = Sammy
species = shark
tank_number = 2
name = Jamie
species = cuttlefish
tank_number = 7


# Deleting Data from the SQLite Database
>>> with SqlCtx(cs) as db:
...     target_fish_name = "Sammy"
...     with db.connection:
...         _= db.cursor.execute("DELETE FROM fish WHERE name = ?", (target_fish_name,))
...         rows = db.cursor.execute("SELECT name, species, tank_number FROM fish").fetchall()
...         for row in rows:
...             for key in row.keys():
...                 print(f"{key} = {row[key]}")
... 
name = Jamie
species = cuttlefish
tank_number = 7
```