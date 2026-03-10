from ariadne import convert_kwargs_to_snake_case
from .models import Todo

def resolve_todos(obj, info):
    try:
        # Fetches all items and converts them to dictionaries
        todos = [todo.to_dict() for todo in Todo.query.all()]
        payload = {
            "success": True,
            "todos": todos
        }
    except Exception as error:
        payload = {
            "success": False,
            "errors": [str(error)]
        }
    return payload

@convert_kwargs_to_snake_case
def resolve_todo(obj, info, todo_id):
    """
    Fetches a single Todo by its ID.
    The decorator converts 'todoId' from GraphQL to 'todo_id' for Python.
    """
    try:
        todo = Todo.query.get(todo_id)
        if todo:
            payload = {
                "success": True,
                "todo": todo.to_dict()
            }
        else:
            payload = {
                "success": False,
                "errors": [f"Todo item matching id {todo_id} not found"]
            }
    except Exception as error:
        payload = {
            "success": False,
            "errors": [str(error)]
        }
    return payload