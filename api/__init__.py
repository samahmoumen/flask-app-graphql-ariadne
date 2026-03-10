import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from ariadne import ObjectType, make_executable_schema, graphql_sync, load_schema_from_path, snake_case_fallback_resolvers


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.getcwd()}/todo.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


GRAPHQL_PLAYGROUND_HTML = """
<!DOCTYPE html>
<html>
  <head>
    <meta charset=utf-8/>
    <title>GraphQL Playground</title>
    <link rel="stylesheet"
      href="//cdn.jsdelivr.net/npm/graphql-playground-react/build/static/css/index.css" />
    <link rel="shortcut icon"
      href="//cdn.jsdelivr.net/npm/graphql-playground-react/build/favicon.png" />
    <script src="//cdn.jsdelivr.net/npm/graphql-playground-react/build/static/js/middleware.js"></script>
  </head>
  <body>
    <div id="root"/>
    <script>
      window.addEventListener('load', function() {
        GraphQLPlayground.init(document.getElementById('root'), {
          endpoint: '/graphql'
        })
      })
    </script>
  </body>
</html>
"""


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    completed = db.Column(db.Boolean, default=False)

# Create tables
with app.app_context():
    db.create_all()


query = ObjectType("Query")

# Resolver function example
def resolve_todos(*_):
    todos = Todo.query.all()
    return [{"id": t.id, "title": t.title, "completed": t.completed} for t in todos]

query.set_field("todos", resolve_todos)

# Load schema from file or define inline
type_defs = """
type Todo {
    id: Int!
    title: String!
    completed: Boolean!
}

type Query {
    todos: [Todo!]!
}
"""

schema = make_executable_schema(type_defs, query, snake_case_fallback_resolvers)


@app.route("/")
def hello():
    return "Hello!"

@app.route("/graphql", methods=["GET"])
def graphql_playground():
    return GRAPHQL_PLAYGROUND_HTML, 200

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


if __name__ == "__main__":
    app.run(debug=True)