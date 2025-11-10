import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()


def setup_postgres():
    """Create PostgreSQL database and user (run once during deployment)"""
    admin_url = os.getenv("ADMIN_DATABASE_URL")
    todos_password = os.getenv("TODOS_PASSWORD")

    if not admin_url:
        print("No ADMIN_DATABASE_URL found, skipping PostgreSQL setup")
        return

    # Connect as admin
    conn = psycopg2.connect(admin_url)
    conn.autocommit = True
    cursor = conn.cursor()

    # Create database
    try:
        cursor.execute("CREATE DATABASE todos;")
        print("✓ Database 'todos' created")
    except psycopg2.errors.DuplicateDatabase:
        print("✓ Database 'todos' already exists")

    # Create user
    try:
        cursor.execute("CREATE USER todos WITH PASSWORD %s;", (todos_password,))
        print("✓ User 'todos' created")
    except psycopg2.errors.DuplicateObject:
        print("✓ User 'todos' exists, updating password")
        cursor.execute("ALTER USER todos WITH PASSWORD %s;", (todos_password,))

    # Grant privileges
    cursor.execute("GRANT ALL PRIVILEGES ON DATABASE todos TO todos;")
    print("✓ Privileges granted")

    cursor.close()
    conn.close()

    # Connect to todos database and set ownership
    admin_url_todos = admin_url.rsplit("/", 1)[0] + "/todos"
    conn = psycopg2.connect(admin_url_todos)
    conn.autocommit = True
    cursor = conn.cursor()

    cursor.execute("GRANT ALL ON SCHEMA public TO todos;")
    cursor.execute("ALTER SCHEMA public OWNER TO todos;")
    print("✓ Schema ownership transferred")

    cursor.close()
    conn.close()


if __name__ == "__main__":
    setup_postgres()
