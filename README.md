
---

# 🏗️ Technical Architecture & Documentation: Flask-GraphQL API

This documentation outlines the design and implementation of a Task Management API (ToDo) using a **Schema-First** approach. By decoupling the API contract from the business logic, we ensure a scalable and maintainable backend architecture.

---

## 1. Core Component Infrastructure

### 🔹 Flask: The Web Framework (The Host)

Flask serves as the entry point and transport layer. Instead of defining multiple RESTful routes, it exposes a single endpoint that acts as a gateway for all GraphQL operations.

```python
# Location: main.py
# Role: Expose the unified /graphql endpoint
@app.route("/graphql", methods=["POST"])
def graphql_server():
    data = request.get_json()
    # Hand over execution to Ariadne's engine
    success, result = graphql_sync(schema, data, context_value=request)
    return jsonify(result), 200 if success else 400

```

### 🔹 GraphQL: The Query Language (The Contract)

GraphQL defines the data types and the interface. It allows clients to specify the exact shape of the response, preventing over-fetching and under-fetching of data.

```graphql
# Location: schema.graphql
# Role: Define types, Query (Read), and Mutation (Write) operations
type Todo {
    id: ID!
    description: String!
    completed: Boolean!
}

type Query {
    todos: [Todo]! # Predictable list return
}

```

### 🔹 Ariadne: The Execution Engine (The Bridge)

Ariadne parses the `.graphql` schema and maps fields to Python functions known as **Resolvers**. It translates the GraphQL request into executable Python logic.

```python
# Location: main.py
# Role: Bind the schema to Python logic via ObjectType
query = ObjectType("Query")
query.set_field("todos", resolve_todos) 

```

---

## 2. The Internal Package Architecture (`api/__init__.py`)

In a modular Flask application, `__init__.py` is the most critical file for **Dependency Management**. We used it to solve the "Circular Import" problem common in SQLAlchemy projects.

```python
# Location: api/__init__.py
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# 1. Initialize the Flask instance
app = Flask(__name__)

# 2. Configure SQLite Database Path
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.getcwd()}/todo.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# 3. Initialize SQLAlchemy ONCE to share across the package
db = SQLAlchemy(app)

```

**Technical Impact:** By initializing `db` here, we ensure that `models.py`, `queries.py`, and `mutations.py` all reference the same database session, preventing `Table 'todo' already defined` errors.

---

## 3. Implementation of API Components

### 🧬 Data Layer (`models.py`)

Maps Python classes to the relational database. Each class inherits from `db.Model`, allowing SQLAlchemy to handle the SQL generation.

```python
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String)
    completed = db.Column(db.Boolean, default=False)
    
    def to_dict(self): # Helper for GraphQL conversion
        return {"id": self.id, "description": self.description, "completed": self.completed}

```

### 🔍 Read Operations (`queries.py`)

Resolvers designed for data retrieval. They utilize the SQLAlchemy query interface to fetch records.

* **`resolve_todos`**: Fetches all records from the `Todo` table.
* **`resolve_todo`**: Takes a `todoId` argument to return a specific record.

### ⚡ Write Operations (`mutations.py`)

Resolvers that modify the database state.

* **Input Handling**: Uses `@convert_kwargs_to_snake_case` to bridge the gap between GraphQL's `camelCase` and Python's `snake_case`.
* **State Management**: Implements `db.session.add()` and `db.session.commit()` with robust `try-except` blocks to return structured error messages to the client.

---

This expanded guide is designed to serve as a high-level technical reference. It includes deep-dives into the **Package Pattern** and a robust **Log of "Silent Failures"**—the kind of bugs that don't crash the app but stop your data from flowing correctly.

---

# 🏗️ Advanced Technical Architecture: Flask + Ariadne

## 1. The Package Pattern (`api/__init__.py`)

In professional Python development, we avoid putting everything in one file. By using a package structure (`api/`), we create a "State Manager."

* **Role of `__init__.py**`: It treats the `api` folder as a single module. By initializing `SQLAlchemy(app)` here, you create a global `db` object.
* **The Circular Import Fix**: In `models.py`, we import `db` from the package (`from . import db`). This ensures the models are registered to the *existing* database instance rather than creating a new, conflicting one.

---

## 2. Component Logic & Data Flow

### 🧬 Model Serialization (`api/models.py`)

SQLAlchemy objects are not JSON-serializable by default.

* **Technical Detail**: We implement a `to_dict()` method. GraphQL resolvers require a dictionary or an object with attributes matching the schema. This method acts as our internal **DTO (Data Transfer Object)**.

### ⚡ Resolver Architecture (`api/mutations.py`)

This is where the business logic lives.

* **Snake Case Decorator**: `@convert_kwargs_to_snake_case` is a middleware that intercepts the GraphQL `info` object and transforms incoming arguments. Without this, your Python function would expect `dueDate` (CamelCase), violating PEP 8 standards.
* **Atomic Transactions**: We use `db.session.add()` followed by `db.session.commit()`. If the commit fails (e.g., database lock), the `except` block catches it to prevent a 500 Internal Server Error, returning a structured `GraphQL error` instead.

---

## 🚀 Getting Started (Step-by-Step)

### 1. Isolated Environment Setup

```bash
mkdir todo_api && cd todo_api
python3 -m venv venv
source venv/bin/activate
# Using constraints ensures your MacBook doesn't pull incompatible versions
pip install flask ariadne flask-sqlalchemy

```

### 2. Physical Database Initialization

You cannot query a database that doesn't exist. This step creates the `todo.db` SQLite file and maps the schema.

```python
python3
>>> from main import app, db
>>> from api.models import Todo # Ensures models are loaded into metadata
>>> with app.app_context():
...     db.create_all()
>>> exit()

```

---

## 🛠️ Extended Troubleshooting (The "Engineer's Log")

### 🚩 Resolved Startup Failures

| Error Message | Root Cause | Technical Resolution |
| --- | --- | --- |
| **`ImportError: ... snake_case_fallback_resolvers`** | Ariadne v0.15+ removed this internal function. | Remove the import. Ariadne now handles this automatically or via explicit `ObjectType` bindings. |
| **`AttributeError: 'NoneType' has no attribute 'to_dict'`** | Your resolver tried to serialize a Todo that wasn't found in the DB. | Add an `if todo:` check before calling `.to_dict()`. Return a "Not Found" error instead. |
| **`RuntimeError: Working outside of application context`** | Accessing the database without an active Flask "State". | Always use `with app.app_context():` when running scripts outside the main web loop. |

### 🚩 Silent Data Failures (Logic Bugs)

* **The "Invisible Update"**:
* *Symptom*: Mutation returns `success: true`, but the database remains unchanged.
* *Cause*: Missing `db.session.commit()`. SQLAlchemy tracks changes in a "Sandbox" until you explicitly commit.


* **The "Date Format Trap"**:
* *Symptom*: `ValueError: time data '2026-03-10' does not match format '%d-%m-%Y'`.
* *Cause*: Your resolver expects `DD-MM-YYYY` but the user sent `YYYY-MM-DD`.
* *Fix*: Standardize on ISO format or provide a clear error message in the `errors` array of your `TodoResult`.


* **The "Zombie Process"**:
* *Symptom*: `OSError: [Errno 48] Address already in use`.
* *Cause*: A previous `flask run` crashed but didn't release port 5000.
* *Fix*: Run `lsof -i :5000` then `kill -9 <PID>`.



---

## ✅ Master "Do's and Don'ts"

### 🟢 Do...

* **Explicit Imports**: Use `from api import app` rather than importing from `main.py` when working in sub-modules to avoid recursion.
* **Use Type Checking**: Even though Python is dynamic, checking if `todo_id` is an integer/string before querying saves database overhead.
* **Leverage the Explorer**: Use the `ExplorerPlayground` (Apollo Sandbox) to view the "Schema" tab. It is the best documentation for your API.

### 🔴 Don't...

* **Don't ignore the `info` parameter**: In resolvers, `info` contains valuable metadata about the request (like headers or user context).
* **Don't put logic in `main.py**`: Keep `main.py` thin. It should only be used for configuration and binding. Logic belongs in the `api/` package.
* **Don't neglect the `.gitignore**`: Never commit your `venv/` or `todo.db` to GitHub.

---
