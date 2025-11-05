import streamlit as st
import os
from dotenv import load_dotenv
from peewee import *
from playhouse.db_url import connect

# Load environment variables from .env file
load_dotenv()

# Database configuration
# If DATABASE_URL exists, use it (PostgreSQL in production)
# Otherwise, default to SQLite for local development
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///todos.db")

# Connect to database using the URL
db = connect(DATABASE_URL)


# Define the Todo model
class Todo(Model):
    task = CharField()
    completed = BooleanField(default=False)

    class Meta:
        database = db


# Create tables if they don't exist
db.connect()
db.create_tables([Todo], safe=True)


def main():
    st.title("Your To-Do List")

    # Get demo secrets from environment
    user_name = os.getenv("USER_NAME", "Guest User")
    api_token = os.getenv("API_TOKEN", None)

    st.write(f"Hello, **{user_name}**! Welcome to your to-do list.")

    # Show which database is being used (helpful for workshop demo)
    db_type = "PostgreSQL" if "postgres" in DATABASE_URL else "SQLite"
    st.caption(f"Using {db_type} database")

    # Add new todo
    todo_input = st.text_input("Enter a to-do item:")
    if st.button("Add") and todo_input:
        Todo.create(task=todo_input)
        st.rerun()

    # Display todos
    todos = Todo.select().order_by(Todo.id.desc())

    if todos.count() == 0:
        st.info("No todos yet. Add one above!")

    for todo in todos:
        col1, col2, col3 = st.columns([0.1, 0.7, 0.2])

        # Checkbox for completion
        completed = col1.checkbox("", value=todo.completed, key=f"check_{todo.id}")
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
