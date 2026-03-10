from datetime import datetime
from ariadne import convert_kwargs_to_snake_case
from . import db
from .models import Todo

@convert_kwargs_to_snake_case
def resolve_create_todo(obj, info, description, due_date):
    try:
        due_date = datetime.strptime(due_date, '%d-%m-%Y').date()
        todo = Todo(description=description, due_date=due_date)
        db.session.add(todo)
        db.session.commit()
        payload = {"success": True, "todo": todo.to_dict()}
    except ValueError:
        payload = {
            "success": False,
            "errors": ["Incorrect date format. Use dd-mm-yyyy"]
        }
    return payload

@convert_kwargs_to_snake_case
def resolve_mark_done(obj, info, todo_id):
    try:
        todo = Todo.query.get(todo_id)
        if todo:
            todo.completed = True
            db.session.commit()
            payload = {"success": True, "todo": todo.to_dict()}
        else:
            payload = {"success": False, "errors": [f"ID {todo_id} not found"]}
    except Exception as error:
        payload = {"success": False, "errors": [str(error)]}
    return payload

@convert_kwargs_to_snake_case
def resolve_delete_todo(obj, info, todo_id):
    try:
        todo = Todo.query.get(todo_id)
        if todo:
            db.session.delete(todo)
            db.session.commit()
            payload = {"success": True}
        else:
            payload = {"success": False, "errors": [f"ID {todo_id} not found"]}
    except Exception as error:
        payload = {"success": False, "errors": [str(error)]}
    return payload

@convert_kwargs_to_snake_case
def resolve_update_due_date(obj, info, todo_id, new_date):
    try:
        todo = Todo.query.get(todo_id)
        if todo:
            todo.due_date = datetime.strptime(new_date, '%d-%m-%Y').date()
            db.session.commit()
            payload = {"success": True, "todo": todo.to_dict()}
        else:
            payload = {"success": False, "errors": [f"ID {todo_id} not found"]}
    except ValueError:
        payload = {"success": False, "errors": ["Use dd-mm-yyyy format"]}
    except Exception as error:
        payload = {"success": False, "errors": [str(error)]}
    return payload