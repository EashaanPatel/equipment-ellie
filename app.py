from __future__ import annotations

import json
import os
import tempfile
import uuid
from datetime import datetime, timedelta

from flask import Flask, jsonify, request, send_from_directory

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data.json")

app = Flask(__name__, static_folder="static", static_url_path="/static")


def _now_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def _due_iso() -> str:
    return (datetime.utcnow() + timedelta(days=1)).replace(microsecond=0).isoformat() + "Z"


def _load_data() -> dict:
    if not os.path.exists(DATA_FILE):
        return {"equipment": [], "people": [], "checkouts": []}
    with open(DATA_FILE, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _save_data(data: dict) -> None:
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    fd, temp_path = tempfile.mkstemp(dir=os.path.dirname(DATA_FILE))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2)
        os.replace(temp_path, DATA_FILE)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def _find_by_id(items: list[dict], item_id: str) -> dict | None:
    return next((item for item in items if item["id"] == item_id), None)


def _active_checkout(data: dict, equipment_id: str) -> dict | None:
    return next(
        (
            checkout
            for checkout in data["checkouts"]
            if checkout["equipment_id"] == equipment_id
            and checkout["checked_in_at"] is None
        ),
        None,
    )


@app.route("/")
def index() -> object:
    return send_from_directory(app.static_folder, "index.html")


@app.route("/api/equipment", methods=["GET"])
def list_equipment() -> object:
    data = _load_data()
    return jsonify(data["equipment"])


@app.route("/api/people", methods=["GET"])
def list_people() -> object:
    data = _load_data()
    return jsonify(data["people"])


@app.route("/api/equipment", methods=["POST"])
def create_equipment() -> object:
    payload = request.get_json(force=True)
    name = payload.get("name", "").strip()
    if not name:
        return jsonify({"error": "Equipment name is required."}), 400

    data = _load_data()
    new_equipment = {
        "id": str(uuid.uuid4()),
        "name": name,
        "tag": payload.get("tag", "").strip(),
        "description": payload.get("description", "").strip(),
        "status": "available",
        "checked_out_to": None,
        "due_at": None,
    }
    data["equipment"].append(new_equipment)
    _save_data(data)
    return jsonify(new_equipment), 201


@app.route("/api/people", methods=["POST"])
def create_person() -> object:
    payload = request.get_json(force=True)
    name = payload.get("name", "").strip()
    if not name:
        return jsonify({"error": "Person name is required."}), 400

    data = _load_data()
    new_person = {
        "id": str(uuid.uuid4()),
        "name": name,
        "email": payload.get("email", "").strip(),
        "role": payload.get("role", "").strip(),
    }
    data["people"].append(new_person)
    _save_data(data)
    return jsonify(new_person), 201


@app.route("/api/equipment/<equipment_id>", methods=["PUT"])
def update_equipment(equipment_id: str) -> object:
    payload = request.get_json(force=True)
    data = _load_data()
    equipment = _find_by_id(data["equipment"], equipment_id)
    if not equipment:
        return jsonify({"error": "Equipment not found."}), 404

    if "name" in payload and not payload["name"].strip():
        return jsonify({"error": "Equipment name is required."}), 400

    for key in ["name", "tag", "description"]:
        if key in payload:
            equipment[key] = payload[key].strip()

    _save_data(data)
    return jsonify(equipment)


@app.route("/api/people/<person_id>", methods=["PUT"])
def update_person(person_id: str) -> object:
    payload = request.get_json(force=True)
    data = _load_data()
    person = _find_by_id(data["people"], person_id)
    if not person:
        return jsonify({"error": "Person not found."}), 404

    if "name" in payload and not payload["name"].strip():
        return jsonify({"error": "Person name is required."}), 400

    for key in ["name", "email", "role"]:
        if key in payload:
            person[key] = payload[key].strip()

    _save_data(data)
    return jsonify(person)


@app.route("/api/equipment/<equipment_id>", methods=["DELETE"])
def delete_equipment(equipment_id: str) -> object:
    data = _load_data()
    equipment = _find_by_id(data["equipment"], equipment_id)
    if not equipment:
        return jsonify({"error": "Equipment not found."}), 404
    if equipment["status"] == "checked_out":
        return jsonify({"error": "Cannot delete checked-out equipment."}), 400

    data["equipment"] = [item for item in data["equipment"] if item["id"] != equipment_id]
    _save_data(data)
    return jsonify({"status": "deleted"})


@app.route("/api/people/<person_id>", methods=["DELETE"])
def delete_person(person_id: str) -> object:
    data = _load_data()
    person = _find_by_id(data["people"], person_id)
    if not person:
        return jsonify({"error": "Person not found."}), 404

    checked_out = [
        equipment
        for equipment in data["equipment"]
        if equipment["checked_out_to"] == person_id
    ]
    if checked_out:
        return jsonify({"error": "Person currently has equipment checked out."}), 400

    data["people"] = [item for item in data["people"] if item["id"] != person_id]
    _save_data(data)
    return jsonify({"status": "deleted"})


@app.route("/api/checkout", methods=["POST"])
def checkout_equipment() -> object:
    payload = request.get_json(force=True)
    equipment_id = payload.get("equipment_id")
    person_id = payload.get("person_id")

    data = _load_data()
    equipment = _find_by_id(data["equipment"], equipment_id)
    person = _find_by_id(data["people"], person_id)

    if not equipment:
        return jsonify({"error": "Equipment not found."}), 404
    if not person:
        return jsonify({"error": "Person not found."}), 404
    if equipment["status"] == "checked_out":
        return jsonify({"error": "Equipment already checked out."}), 400

    checkout_record = {
        "id": str(uuid.uuid4()),
        "equipment_id": equipment_id,
        "person_id": person_id,
        "checked_out_at": _now_iso(),
        "due_at": _due_iso(),
        "checked_in_at": None,
        "handoff": False,
    }

    equipment["status"] = "checked_out"
    equipment["checked_out_to"] = person_id
    equipment["due_at"] = checkout_record["due_at"]

    data["checkouts"].append(checkout_record)
    _save_data(data)
    return jsonify(checkout_record), 201


@app.route("/api/checkin", methods=["POST"])
def checkin_equipment() -> object:
    payload = request.get_json(force=True)
    equipment_id = payload.get("equipment_id")

    data = _load_data()
    equipment = _find_by_id(data["equipment"], equipment_id)
    if not equipment:
        return jsonify({"error": "Equipment not found."}), 404
    if equipment["status"] != "checked_out":
        return jsonify({"error": "Equipment is not checked out."}), 400

    checkout_record = _active_checkout(data, equipment_id)
    if not checkout_record:
        return jsonify({"error": "Active checkout not found."}), 400

    checkout_record["checked_in_at"] = _now_iso()
    equipment["status"] = "available"
    equipment["checked_out_to"] = None
    equipment["due_at"] = None

    _save_data(data)
    return jsonify({"status": "checked_in"})


@app.route("/api/transfer", methods=["POST"])
def transfer_equipment() -> object:
    payload = request.get_json(force=True)
    equipment_id = payload.get("equipment_id")
    person_id = payload.get("person_id")

    data = _load_data()
    equipment = _find_by_id(data["equipment"], equipment_id)
    person = _find_by_id(data["people"], person_id)
    if not equipment:
        return jsonify({"error": "Equipment not found."}), 404
    if not person:
        return jsonify({"error": "Person not found."}), 404
    if equipment["status"] != "checked_out":
        return jsonify({"error": "Equipment is not checked out."}), 400

    checkout_record = _active_checkout(data, equipment_id)
    if not checkout_record:
        return jsonify({"error": "Active checkout not found."}), 400

    checkout_record["checked_in_at"] = _now_iso()
    checkout_record["handoff"] = True

    new_checkout = {
        "id": str(uuid.uuid4()),
        "equipment_id": equipment_id,
        "person_id": person_id,
        "checked_out_at": _now_iso(),
        "due_at": _due_iso(),
        "checked_in_at": None,
        "handoff": True,
        "handoff_from": checkout_record["person_id"],
    }

    equipment["checked_out_to"] = person_id
    equipment["due_at"] = new_checkout["due_at"]

    data["checkouts"].append(new_checkout)
    _save_data(data)
    return jsonify(new_checkout), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
