from flask import Flask, request, jsonify
import os
import json
import threading

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LICENSE_FILE = os.path.join(BASE_DIR, "licenses.json")
LOCK = threading.Lock()


def load_licenses():
    if not os.path.exists(LICENSE_FILE):
        return {}

    try:
        with open(LICENSE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_licenses(data):
    temp_file = LICENSE_FILE + ".tmp"
    with open(temp_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    os.replace(temp_file, LICENSE_FILE)


@app.route("/verify", methods=["POST"])
def verify_license():
    data = request.get_json(silent=True) or {}

    key = (data.get("license_key") or "").strip()
    machine_id = (data.get("machine_id") or "").strip()

    if not key or not machine_id:
        return jsonify({
            "valid": False,
            "message": "license_key och machine_id krävs"
        }), 400

    with LOCK:
        licenses = load_licenses()

        if key not in licenses:
            return jsonify({
                "valid": False,
                "message": "Licensen finns inte"
            }), 200

        license_info = licenses[key]
        status = license_info.get("status", "TRIAL")
        max_activations = int(license_info.get("max_activations", 2))
        activated_machines = license_info.get("activated_machines", [])

        if machine_id in activated_machines:
            return jsonify({
                "valid": True,
                "status": status,
                "message": "Licensen är redan aktiverad på denna dator"
            }), 200

        if len(activated_machines) < max_activations:
            activated_machines.append(machine_id)
            license_info["activated_machines"] = activated_machines
            licenses[key] = license_info
            save_licenses(licenses)

            return jsonify({
                "valid": True,
                "status": status,
                "message": "Licensen aktiverades och sparades"
            }), 200

        return jsonify({
            "valid": False,
            "status": status,
            "message": "Max antal aktiveringar uppnått"
        }), 200


@app.route("/licenses", methods=["GET"])
def list_licenses():
    with LOCK:
        licenses = load_licenses()
    return jsonify(licenses), 200


@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "ok", "service": "Sonic License Server"}), 200


if __name__ == "__main__":
    if not os.path.exists(LICENSE_FILE):
        save_licenses({})

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)