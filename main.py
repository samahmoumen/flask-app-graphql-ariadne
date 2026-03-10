from flask import request, jsonify
from ariadne import (
    load_schema_from_path, 
    make_executable_schema, 
    graphql_sync, 
    snake_case_fallback_resolvers, 
    ObjectType
)
from ariadne.explorer import ExplorerPlayground
PLAYGROUND_HTML = ExplorerPlayground(title="Todo API").html(None)

# Import the app and db we already created in the api folder
from api import app, db
from api.queries import resolve_todos, resolve_todo
from api.mutations import (
    resolve_create_todo, 
    resolve_mark_done, 
    resolve_delete_todo, 
    resolve_update_due_date
)

# 1. Map the Query fields to their Python resolvers
query = ObjectType("Query")
query.set_field("todos", resolve_todos)
query.set_field("todo", resolve_todo)

# 2. Map the Mutation fields to their Python resolvers
mutation = ObjectType("Mutation")
mutation.set_field("createTodo", resolve_create_todo)
mutation.set_field("markDone", resolve_mark_done)
mutation.set_field("deleteTodo", resolve_delete_todo)
mutation.set_field("updateDueDate", resolve_update_due_date)

# 3. Load the schema and create the executable schema
type_defs = load_schema_from_path("schema.graphql")
schema = make_executable_schema(
    type_defs, [query, mutation], snake_case_fallback_resolvers
)

@app.route('/')
def hello():
    return 'Hello!'

@app.route("/graphql", methods=["GET"])
def graphql_playground():
    # This serves the interactive UI for testing
    return PLAYGROUND_HTML, 200

@app.route("/graphql", methods=["POST"])
def graphql_server():
    data = request.get_json()

    success, result = graphql_sync(
        schema,
        data,
        context_value=request,
        debug=app.debug
    )

    status_code = 200 if success else 400
    return jsonify(result), status_code

# This part ensures the database tables are created before the app starts
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)