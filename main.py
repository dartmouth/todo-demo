import streamlit as st
import os
from db import Todo, init_db

# Initialize database
init_db()


def main():
    st.title("📝 Your To-Do List")

    # Welcome message
    user_name = os.getenv("USER_NAME", "Guest")
    st.write(f"Hello, **{user_name}**!")

    # Add new todo
    with st.form("add_todo_form", clear_on_submit=True):
        new_task = st.text_input(
            "Add a new task:", placeholder="What needs to be done?"
        )
        if st.form_submit_button("Add Task") and new_task:
            Todo.create(task=new_task)
            st.rerun()

    # Display todos
    todos = Todo.select().order_by(Todo.id.desc())

    if todos.count() == 0:
        st.info("No tasks yet. Add one above!")
        return

    # Show each todo
    for todo in todos:
        col1, col2, col3 = st.columns([0.1, 0.7, 0.2])

        # Checkbox to mark complete
        is_done = col1.checkbox(
            "Done",
            value=todo.completed,
            key=f"check_{todo.id}",
            label_visibility="collapsed",
        )

        # Update if checkbox changed
        if is_done != todo.completed:
            todo.completed = is_done
            todo.save()
            st.rerun()

        # Display task (strikethrough if completed)
        if todo.completed:
            col2.markdown(f"~~{todo.task}~~")
        else:
            col2.write(todo.task)

        # Delete button
        if col3.button("🗑️", key=f"del_{todo.id}"):
            todo.delete_instance()
            st.rerun()


if __name__ == "__main__":
    main()
