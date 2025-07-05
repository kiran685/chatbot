from flask import Flask, render_template, request, redirect, session, jsonify, Response
from database import init_db, register_user, verify_user, get_chat_history, get_all_users, get_all_chats
from chatbot_core import get_bot_response
import csv
from io import StringIO

app = Flask(__name__)
app.secret_key = "secret123"
init_db()

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

@app.route("/")
def home():
    if "user_id" in session:
        return render_template("index.html")
    return redirect("/login")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user_id = verify_user(request.form["username"], request.form["password"])
        if user_id:
            session["user_id"] = user_id
            return redirect("/")
        return "Invalid credentials!"
    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        if register_user(request.form["username"], request.form["password"]):
            return redirect("/login")
        return "Username already exists!"
    return render_template("signup.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/chat", methods=["POST"])
def chat():
    if "user_id" not in session:
        return jsonify({"response": "Please log in first!"})
    user_message = request.form.get("message")
    response = get_bot_response(session["user_id"], user_message)
    return jsonify({"response": response})

@app.route("/history")
def history():
    if "user_id" not in session:
        return redirect("/login")
    chats = get_chat_history(session["user_id"])
    return render_template("history.html", chats=chats)

@app.route("/export_csv")
def export_csv():
    if "user_id" not in session:
        return redirect("/login")
    chats = get_chat_history(session["user_id"])
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["User Message", "Bot Response", "Timestamp"])
    writer.writerows(chats)
    output.seek(0)
    return Response(output, mimetype="text/csv", headers={"Content-Disposition": "attachment;filename=chat_history.csv"})

@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        if request.form["username"] == ADMIN_USERNAME and request.form["password"] == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect("/admin")
        return "Invalid admin credentials!"
    return render_template("admin_login.html")

@app.route("/admin")
def admin_panel():
    if not session.get("admin"):
        return redirect("/admin_login")
    return render_template("admin_panel.html", users=get_all_users(), chats=get_all_chats())

@app.route("/export_all_csv")
def export_all_csv():
    if not session.get("admin"):
        return redirect("/admin_login")
    chats = get_all_chats()
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["Username", "User Message", "Bot Response", "Timestamp"])
    writer.writerows(chats)
    output.seek(0)
    return Response(output, mimetype="text/csv", headers={"Content-Disposition": "attachment;filename=all_chat_history.csv"})

if __name__ == "__main__":
    app.run(debug=True)
