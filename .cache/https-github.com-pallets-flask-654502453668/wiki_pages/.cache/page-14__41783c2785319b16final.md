# Database Management
## Overview
The Flask framework provides a flexible and modular structure for managing databases, supporting various database engines, including SQLite, PostgreSQL, and MySQL, as seen in `examples/tutorial/flaskr/db.py`.

## Key Components / Concepts
The key components of database management in Flask include:
* Database engines: Flask supports various database engines, such as SQLite, PostgreSQL, and MySQL.
* SQLAlchemy: A popular ORM (Object-Relational Mapping) tool for Python that provides a high-level interface for interacting with databases.
* Flask-SQLAlchemy: A Flask extension that integrates SQLAlchemy with the Flask framework, utilized in `examples/tutorial/flaskr/db.py`.

## How it Works
The database management process in Flask involves the following steps:
1. Choose a database engine: Select a suitable database engine based on the project's requirements, as demonstrated in `examples/tutorial/flaskr/schema.sql`.
2. Install the required packages: Install the necessary packages, such as Flask-SQLAlchemy and the database engine's driver.
3. Configure the database: Configure the database connection using the chosen engine and packages.
4. Define models: Define models using SQLAlchemy or Flask-SQLAlchemy to interact with the database.

## Example(s)
Here's an example of how to use Flask-SQLAlchemy to define a model and interact with a database:
```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///example.db"
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

# Create the database tables
with app.app_context():
    db.create_all()

# Insert a new user into the database
new_user = User(name="John Doe")
db.session.add(new_user)
db.session.commit()
```

## Diagram(s)
```mermaid
flowchart LR
    A[Choose Database Engine] --> B[Install Required Packages]
    B --> C[Configure Database]
    C --> D[Define Models]
    D --> E[Interact with Database]
```
Database Management Flowchart

## References
* `examples/tutorial/flaskr/db.py`
* `examples/tutorial/flaskr/schema.sql`
* `examples/tutorial/tests/test_db.py`