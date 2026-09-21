import os
from pathlib import Path

import certifi
from flask import Flask, jsonify, redirect, render_template_string, request, send_file, url_for
from pymongo import MongoClient
from pymongo.errors import PyMongoError

app = Flask(__name__)
index_file = Path(__file__).with_name("index.html")
mongodb_uri = os.getenv(
	"MONGODB_URI",
	"mongodb+srv://Rohith:Ammadu%40123@devops-learning-app.q5aa37y.mongodb.net/?appName=Devops-learning-app",
)
client = MongoClient(mongodb_uri, tlsCAFile=certifi.where()) if mongodb_uri else None
users = client[os.getenv("MONGODB_DATABASE", "basic_app")]["users"] if client else None


def render_form(error=None):
	return render_template_string(index_file.read_text(encoding="utf-8"), error=error)


@app.route("/")
def home():
	return render_form()


@app.route("/success")
def success():
	return send_file("success.html")


@app.route("/api", methods=["GET", "POST"])
def api():
	if request.method == "GET":
		if users is None:
			return jsonify(error="MONGODB_URI is not configured."), 503
		try:
			stored_users = list(users.find({}, {"_id": 0}))
		except PyMongoError as error:
			return jsonify(error=f"Unable to retrieve users: {error}"), 503
		return jsonify(stored_users)

	data = request.get_json(silent=True) or request.form
	name = str(data.get("name", "")).strip()
	age = data.get("age")
	if not name or age in (None, ""):
		return render_form("Name and age are required."), 400

	try:
		age = int(age)
		if age < 0:
			raise ValueError("Age must be zero or greater.")
	except ValueError as error:
		return render_form(str(error)), 400

	if users is None:
		return render_form("MONGODB_URI is not configured."), 503
	try:
		users.insert_one({"name": name, "age": age})
	except PyMongoError as error:
		return render_form(f"Unable to save data: {error}"), 503

	return redirect(url_for("success"))


if __name__ == "__main__":
	app.run(port=5123)