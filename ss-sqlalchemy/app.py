from flask import Flask
from sqlalchemy import create_engine, text, Table, Column, Integer, String, MetaData, insert
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import select
from sqlalchemy.sql.schema import ForeignKey

from .settings import Config

app = Flask(__name__)
app.config.from_object(Config)

SQLALCHEMY_DATABASE_URI = app.config.get('SQLALCHEMY_DATABASE_URI')
print(SQLALCHEMY_DATABASE_URI)

# The engine object is lazy initialized because the connection wil only establish once a task is assigned
engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=True, future=True)

# Create the MetaData object which will handle information for the table.
# For ORM, use declarative base or create a registry then use it to create base
metadata = MetaData()

# Assign the book table to the metadata collection (this is called declared) TODO: create example of reflected
book_table = Table("book", metadata,
                   Column('book_id', Integer, primary_key=True),
                   Column('user_id', ForeignKey(
                       'user.user_id'), nullable=False),
                   Column('book_name', String(30)))

user_table = Table("user", metadata,
                   Column('user_id', Integer, primary_key=True),
                   Column('user_name', String(128)))

metadata.create_all(engine)

# Connection object is created from Engine (the only user-facing purpose)
with engine.connect() as conn:
    conn.execute(
        text("CREATE TABLE IF NOT EXISTS user (user_id int, user_name varchar(128))"))

    # The colon format acts as a parameter symbol
    conn.execute(text("INSERT INTO user (user_id, user_name) VALUES (:userId, :userName)"), [
                 {"userId": 1, "userName": "Hoang"}, {"userId": 2, "userName": "Hoang 2"}])

    # insert function generate the values clause automatically. insert() will generate Insert object
    conn.execute(insert(user_table), [{"user_id": 3, "user_name": "Hoang 3"}])

    # This will only commit when run commit explicitly
    conn.commit()

    result = conn.execute(
        text("SELECT * from user WHERE user_id > :x").bindparams(x=1))
    print('Result from Connection Object:')
    print(result.all())

# Deos not hold on to the Connection object but rather create a new Connection object for the next query
with Session(engine) as session:
    session.execute(
        text("CREATE TABLE IF NOT EXISTS book (book_id int, book_name varchar(30))"))
    result = session.execute(
        text("SELECT * from user WHERE user_id > :x").bindparams(x=1))
    # This is not allowed since select() composed against ORM. Use ORM entities instead.
    # result = session.execute(select(
    #     ('Username: ' + user_table.c.user_name).label("username"),).order_by(user_table.c.user_name))
    print('Result from Session object:')
    print(result.all())

    # Follow Martin Fowler's Unit of work which keeps track everything until you are done to make the change to DB.
    session.flush()


with engine.connect() as conn:
    result = conn.execute(select(
        (user_table.c.user_name).label("username"),).order_by(user_table.c.user_name))

    print(result.all())

# Select object allows labeling for easy retrieval. TODO Explain carefully the objects and its purposes.
# a_complicated_select_object = select(
#     ('Username: ' + user_table.c.user_name).label("username"),).order_by(user_table.c.user_name)
# a_complicated_on_clause_select_object = select(book_table.c.user_name).select_from(
#     user_table).join(book_table, book_table.c.user_id == user_table.c.user_id)


@app.route('/')
def hello():
    print(engine.echo)

    return 'success'
