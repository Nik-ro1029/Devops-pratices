import os
import certifi
from bson import ObjectId
from bson.errors import InvalidId
from flask import Flask, jsonify, redirect, request, send_file, url_for
from pymongo import MongoClient
from pymongo.errors import PyMongoError

app = Flask(__name__)
mongodb_uri = os.getenv(
	"MONGODB_URI",
	"mongodb+srv://Rohith:Ammadu%40123@devops-learning-app.q5aa37y.mongodb.net/?appName=Devops-learning-app",
)

client = MongoClient(
	mongodb_uri,
	serverSelectionTimeoutMS=5000,
	tlsCAFile=certifi.where(),
)
users = client["basic_app"]["users"]
@app.route("/")
def home():
	return send_file("index.html")

@app.route("/api", methods=["GET", "POST"])
def api():
	if request.method == "GET":
		try:
			user_id = request.args.get("user_id")
			if user_id:
				saved_user = users.find_one({"_id": ObjectId(user_id)}, {"_id": 0})
				if saved_user is None:
					return jsonify(error="Saved user could not be retrieved."), 404
				return jsonify(
					message=f'Hello "{saved_user["name"]}", your age is "{saved_user["age"]}"',
					user=saved_user,
				)
			stored_users = list(users.find({}, {"_id": 0}))
		except (InvalidId, PyMongoError, TypeError) as error:
			return jsonify(error=f"Unable to retrieve users: {error}"), 503
		return jsonify(users=stored_users)

	data = request.get_json(silent=True) or request.form
	name = str(data.get("name", "")).strip()
	age = data.get("age")
	if not name or age in (None, ""):
		return jsonify(error="Name and age are required."), 400

	try:
		age = int(age)
		if age < 0:
			raise ValueError("Age must be zero or greater.")
		inserted = users.insert_one({"name": name, "age": age})
		saved_user = users.find_one({"_id": inserted.inserted_id}, {"_id": 0})
		if saved_user is None:
			return jsonify(error="User was saved but could not be retrieved."), 503
	except ValueError as error:
		return jsonify(error=str(error)), 400
	except PyMongoError as error:
		return jsonify(error=f"Unable to save user: {error}"), 503

	return redirect(url_for("api", user_id=str(inserted.inserted_id)), code=303)


if __name__ == "__main__":
	app.run(port=5123)