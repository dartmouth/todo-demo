import streamlit as st
import os
import psycopg2
from dotenv import load_dotenv
from peewee import *
from playhouse.db_url import connect
from urllib.parse import urlparse, urlunparse

load_dotenv()

## Database Set-Up
admin_url = os.getenv("DATABASE_URL")
todos_database_url = os.getenv("TODOS_DATABASE_URL")
todos_password = os.getenv("TODOS_PASSWORD")  # Pull from env

# Only try to create PostgreSQL database if DATABASE_URL is set
if admin_url:
    conn = psycopg2.connect(admin_url)
    conn.autocommit = True
    cursor = conn.cursor()
    
    try:
        cursor.execute("CREATE DATABASE todos;")
        print("Database 'todos' created!")
    except psycopg2.errors.DuplicateDatabase:
        print("Database 'todos' already exists")
    
    # Create user (ignore if already exists)
    try:
        cursor.execute("CREATE USER todos WITH PASSWORD %s;", (todos_password,))
        print("User 'todos' created!")
    except psycopg2.errors.DuplicateObject:
        print("User 'todos' already exists, updating password...")
        cursor.execute("ALTER USER todos WITH PASSWORD %s;", (todos_password,))
    
    # Change schema owner
    cursor.execute("ALTER SCHEMA public OWNER TO todos;")
    print("Schema ownership transferred to todos")
    
    conn.close()
    
    # Use TODOS_DATABASE_URL if provided, otherwise construct it with todos credentials
    if not todos_database_url:
        parsed = urlparse(admin_url)
        todos_database_url = urlunparse((
            parsed.scheme,
            f"todos:{todos_password}@{parsed.netloc}",  # Use todos user and env password
            "/todos",
            parsed.params,
            "sslmode=require",
            parsed.fragment,
        ))
else:
    # Fall back to SQLite if no PostgreSQL URL provided
    todos_database_url = "sqlite:///todos.db"

# Connect to the database
db = connect(todos_database_url)

# Define the Todo model
class Todo(Model):
    task = CharField()
    completed = BooleanField(default=False)
    class Meta:
        database = db

db.connect()
db.create_tables([Todo], safe=True)

# Show which database is being used
db_type = "PostgreSQL" if "postgres" in todos_database_url else "SQLite"
print(f"Using {db_type} database")

def main():
    st.title("Your To-Do List")

    # Get demo secrets from environment
    user_name = os.getenv("USER_NAME", "Guest User")
    api_token = os.getenv("API_TOKEN", None)

    st.write(f"Hello, **{user_name}**! Welcome to your todo list.")

    # Add new todo using a form so pressing Enter will submit
    with st.form("add_todo_form", clear_on_submit=True):
        todo_input = st.text_input("Enter a to-do item:", placeholder="Type a todo and press Enter")
        submitted = st.form_submit_button("Add")
        if submitted and todo_input:
            Todo.create(task=todo_input)
            st.rerun()

    # Display todos
    todos = Todo.select().order_by(Todo.id.desc())

    if todos.count() == 0:
        st.info("No todos yet. Add one above!")

    for todo in todos:
        col1, col2, col3 = st.columns([0.1, 0.7, 0.2])
        # Checkbox for completion (provide an accessible label and hide it visually)
        completed = col1.checkbox("Complete", value=todo.completed, key=f"check_{todo.id}", label_visibility="hidden")
        if completed != todo.completed:
            todo.completed = completed
            todo.save()
            st.rerun()

        # Task text (strikethrough if completed)
        if todo.completed:
            col2.write(f"~~{todo.task}~~")
        else:
            col2.write(todo.task)

        # Delete button
        if col3.button("🗑️", key=f"del_{todo.id}"):
            todo.delete_instance()
            st.rerun()


if __name__ == "__main__":
    main()
