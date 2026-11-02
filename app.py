from flask import Flask, render_template, Response, request, session, redirect, url_for
from werkzeug.utils import secure_filename
import os

from database import (
    get_db_connection,
    create_table,
    add_default_profile,
    create_skills_table,
    add_default_skills,
)

app = Flask(__name__)

# Secret key for login session
app.secret_key = "change_this_to_a_strong_secret_key"

# Profile photo upload folder
UPLOAD_FOLDER = "static/images/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# Create database and default profile
create_table()
add_default_profile()

create_skills_table()
add_default_skills()


# ================= HOME =================


@app.route("/")
def home():
    connection = get_db_connection()
    profile = connection.execute("SELECT * FROM profile WHERE id = 1").fetchone()
    skills = connection.execute("SELECT * FROM skills").fetchall()
    projects = connection.execute("SELECT * FROM projects").fetchall()
    connection.close()

    return render_template(
        "index.html", profile=profile, skills=skills, projects=projects
    )


# ================= ADMIN LOGIN =================


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        print("LOGIN USERNAME:", repr(username))
        print("LOGIN PASSWORD LENGTH:", len(password))

        if username == "admin" and password == "12345":
            session["admin"] = True
            return redirect(url_for("admin_dashboard"))

        return "Invalid username or password"

    return render_template("admin_login.html")


# ================= ADMIN DASHBOARD =================


@app.route("/admin/dashboard")
def admin_dashboard():

    if "admin" not in session:
        return redirect(url_for("admin_login"))

    return render_template("admin_dashboard.html")


# ================= ADMIN PROFILE =================


@app.route("/admin/profile", methods=["GET", "POST"])
def admin_profile():

    if "admin" not in session:
        return redirect(url_for("admin_login"))

    connection = get_db_connection()

    if request.method == "POST":

        name = request.form["name"]
        title = request.form["title"]
        about = request.form["about"]

        photo = request.files.get("profile_photo")

        profile = connection.execute("SELECT * FROM profile WHERE id = 1").fetchone()

        filename = profile["photo"]

        if photo and photo.filename != "":
            filename = secure_filename(photo.filename)
            photo.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        connection.execute(
            """
            UPDATE profile
            SET name = ?, title = ?, about = ?, photo = ?
            WHERE id = 1
            """,
            (name, title, about, filename),
        )

        connection.commit()
        connection.close()

        return redirect(url_for("admin_profile"))

    profile = connection.execute("SELECT * FROM profile WHERE id = 1").fetchone()

    connection.close()

    return render_template("admin_profile.html", profile=profile)


# ================= ADMIN SKILLS =================


@app.route("/admin/skills", methods=["GET", "POST"])
def admin_skills():

    if "admin" not in session:
        return redirect(url_for("admin_login"))

    connection = get_db_connection()

    if request.method == "POST":

        skill_name = request.form["skill_name"]

        connection.execute("INSERT INTO skills (name) VALUES (?)", (skill_name,))

        connection.commit()

    skills = connection.execute("SELECT * FROM skills").fetchall()

    connection.close()

    return render_template("admin_skills.html", skills=skills)


# ================= DELETE SKILL =================


@app.route("/admin/delete-skill/<int:skill_id>")
def delete_skill(skill_id):

    if "admin" not in session:
        return redirect(url_for("admin_login"))

    connection = get_db_connection()

    connection.execute("DELETE FROM skills WHERE id = ?", (skill_id,))

    connection.commit()
    connection.close()

    return redirect(url_for("admin_skills"))


# ================= ADMIN PROJECTS =================


@app.route("/admin/projects", methods=["GET", "POST"])
def admin_projects():

    if "admin" not in session:
        return redirect(url_for("admin_login"))

    connection = get_db_connection()

    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        link = request.form["link"]

        connection.execute(
            "INSERT INTO projects (title, description, link) VALUES (?, ?, ?)",
            (title, description, link),
        )

        connection.commit()

    projects = connection.execute("SELECT * FROM projects").fetchall()

    connection.close()

    return render_template("admin_projects.html", projects=projects)


# ================= DELETE PROJECT =================


@app.route("/admin/delete-project/<int:project_id>")
def delete_project(project_id):

    if "admin" not in session:
        return redirect(url_for("admin_login"))

    connection = get_db_connection()

    connection.execute("DELETE FROM projects WHERE id = ?", (project_id,))

    connection.commit()
    connection.close()

    return redirect(url_for("admin_projects"))


# ================= CONTACT SUBMIT =================


@app.route("/contact", methods=["POST"])
def contact():

    name = request.form.get("name")
    email = request.form.get("email")
    message = request.form.get("message")

    connection = get_db_connection()

    connection.execute(
        "INSERT INTO messages (name, email, message) VALUES (?, ?, ?)",
        (name, email, message),
    )

    connection.commit()
    connection.close()

    return redirect(url_for("home") + "#contact")


# ================= ADMIN MESSAGES =================


@app.route("/admin/messages")
def admin_messages():

    if "admin" not in session:
        return redirect(url_for("admin_login"))

    connection = get_db_connection()

    messages = connection.execute("SELECT * FROM messages ORDER BY id DESC").fetchall()

    connection.close()

    return render_template("admin_messages.html", messages=messages)


# ================= DELETE MESSAGE =================


@app.route("/admin/delete-message/<int:message_id>")
def delete_message(message_id):

    if "admin" not in session:
        return redirect(url_for("admin_login"))

    connection = get_db_connection()

    connection.execute("DELETE FROM messages WHERE id = ?", (message_id,))

    connection.commit()
    connection.close()

    return redirect(url_for("admin_messages"))


# ================= ADMIN RESUME =================


@app.route("/admin/resume", methods=["GET", "POST"])
def admin_resume():

    if "admin" not in session:
        return redirect(url_for("admin_login"))

    message = None

    if request.method == "POST":

        if "resume" in request.files:
            file = request.files["resume"]

            if file.filename != "" and file.filename.endswith(".pdf"):

                upload_folder = os.path.join(app.root_path, "static", "files")

                os.makedirs(upload_folder, exist_ok=True)

                file.save(os.path.join(upload_folder, "resume.pdf"))

                message = "Resume updated successfully!"

            else:
                message = "Please upload a valid .pdf file."

    return render_template("admin_resume.html", message=message)


# ================= LOGOUT =================


@app.route("/admin/logout")
def admin_logout():

    session.pop("admin", None)

    return redirect(url_for("admin_login"))


# ================= SITEMAP =================


@app.route("/sitemap.xml")
def sitemap():

    xml = """<?xml version="1.0" encoding="UTF-8"?>
    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
        <url>
            <loc>https://kundan-portfolio-cfne.onrender.com/</loc>
            <changefreq>monthly</changefreq>
            <priority>1.0</priority>
        </url>
    </urlset>"""

    return Response(xml, mimetype="application/xml")


# ================= RUN APP =================

if __name__ == "__main__":
    app.run(debug=True)
