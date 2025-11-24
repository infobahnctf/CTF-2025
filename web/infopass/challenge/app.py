import os
from flask import Flask, request, redirect, session

SECRET_KEY = os.environ.get("SECRET_KEY", "supersecret")
PORT = int(os.environ.get("PORT", 1337))

app = Flask(__name__)
app.secret_key = SECRET_KEY

users = {}


@app.after_request
def add_csp_header(response):
    response.headers["Content-Security-Policy"] = "default-src 'none';"
    return response


@app.route("/", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if not username or not password:
            return "Missing username or password"
        users[username] = password
        session["user"] = username
        return redirect("/dashboard")
    return """
        <h2>Register</h2>
        <form method="post">
            <input name="username" placeholder="Username"><br>
            <input name="password" type="password" placeholder="Password"><br>
            <button type="submit">Register</button>
        </form>
    """


@app.route("/dashboard")
def dashboard():
    user = session.get("user")
    if not user:
        return redirect("/")
    return f"""
        <h2>Dashboard</h2>
        <p>Welcome, {user}!</p>
        <a href="/logout">Logout</a>
    """


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")


if __name__ == "__main__":
    app.run(port=PORT)
