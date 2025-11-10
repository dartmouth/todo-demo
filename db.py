import os
from peewee import *
from playhouse.db_url import connect

# Get database URL from environment, default to SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///todos.db")

# Connect to database
db = connect(DATABASE_URL)


# Define the Todo model
class Todo(Model):
    task = CharField()
    completed = BooleanField(default=False)

    class Meta:
        database = db


def init_db():
    """Initialize database tables"""
    db.connect()
    db.create_tables([Todo], safe=True)
    db_type = "PostgreSQL" if "postgres" in DATABASE_URL else "SQLite"
    print(f"Database initialized: {db_type}")
