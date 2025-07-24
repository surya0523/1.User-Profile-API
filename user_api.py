from flask import Flask, request, render_template
from flask_restful import Resource, Api
import sqlite3, re

app = Flask(__name__)
api = Api(app)

def connect_db():
    conn = sqlite3.connect("users.db", timeout=5)
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn

def init_db():
    with connect_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE
            )
        """)

def validate_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

@app.route("/")
def home():
    return render_template("index.html")

class UserList(Resource):
    def get(self):
        with connect_db() as conn:
            users = conn.execute("SELECT * FROM users").fetchall()
        return [{"id": r[0], "name": r[1], "email": r[2]} for r in users], 200

    def post(self):
        data = request.get_json()
        name, email = data.get("name"), data.get("email")

        if not name or not email:
            return {"message": "Name & Email required"}, 400
        if not validate_email(email):
            return {"message": "Invalid email format"}, 400

        try:
            with connect_db() as conn:
                conn.execute("INSERT INTO users (name, email) VALUES (?, ?)", (name, email))
            return {"message": "User created"}, 201
        except sqlite3.IntegrityError:
            return {"message": "Email already exists"}, 409

class User(Resource):
    def get(self, id):
        with connect_db() as conn:
            row = conn.execute("SELECT * FROM users WHERE id=?", (id,)).fetchone()
        return ({"id": row[0], "name": row[1], "email": row[2]}, 200) if row else ({"message": "User not found"}, 404)

    def put(self, id):
        data = request.get_json()
        name, email = data.get("name"), data.get("email")

        if email and not validate_email(email):
            return {"message": "Invalid email format"}, 400

        with connect_db() as conn:
            if not conn.execute("SELECT * FROM users WHERE id=?", (id,)).fetchone():
                return {"message": "User not found"}, 404
            try:
                if name:
                    conn.execute("UPDATE users SET name=? WHERE id=?", (name, id))
                if email:
                    conn.execute("UPDATE users SET email=? WHERE id=?", (email, id))
                return {"message": "User updated"}, 200
            except sqlite3.IntegrityError:
                return {"message": "Email already exists"}, 409

    def delete(self, id):
        with connect_db() as conn:
            conn.execute("DELETE FROM users WHERE id=?", (id,))
        return {"message": "User deleted"}, 200

api.add_resource(UserList, "/users")
api.add_resource(User, "/users/<int:id>")

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
