from api import app, db


if __name__ == "__main__":
    app.run(debug=True)



from ariadne import load_schema_from_path, make_executable_schema, graphql_sync, ObjectType
from flask import request, jsonify
from api.queries import resolve_todos
from api import models

# Create Query type and attach resolvers
query = ObjectType("Query")
query.set_field("todos", resolve_todos)

# Load GraphQL schema
type_defs = load_schema_from_path("schema.graphql")

# Make executable schema (no snake_case_fallback_resolvers)
schema = make_executable_schema(type_defs, query)

# Flask route for GraphQL Playground (GET)
@app.route("/graphql", methods=["GET"])
def graphql_playground():
    # Simple HTML to display GraphQL Playground
    playground_html = """
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset=utf-8/>
      <title>GraphQL Playground</title>
      <link rel="stylesheet" href="//cdn.jsdelivr.net/npm/graphql-playground-react@1.7.20/build/static/css/index.css" />
      <script src="//cdn.jsdelivr.net/npm/graphql-playground-react@1.7.20/build/static/js/middleware.js"></script>
    </head>
    <body>
      <div id="root"></div>
      <script>
        window.addEventListener('load', function() {
          GraphQLPlayground.init(document.getElementById('root'), { endpoint: '/graphql' })
        })
      </script>
    </body>
    </html>
    """
    return playground_html

# Flask route to handle GraphQL POST requests
@app.route("/graphql", methods=["POST"])
def graphql_server():
    data = request.get_json()
    success, result = graphql_sync(schema, data, context_value=request, debug=app.debug)
    return jsonify(result)