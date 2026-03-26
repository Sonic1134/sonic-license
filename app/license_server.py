from flask import Flask, request, jsonify
from psycopg import connect
from psycopg.rows import dict_row
import os
import json
import secrets
import string

app = Flask(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()
ADMIN_SECRET = os.environ.get("ADMIN_SECRET", "").strip()


def get_conn():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL saknas")
    return connect(DATABASE_URL, row_factory=dict_row)


def init_db():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS licenses (
                    license_key TEXT PRIMARY KEY,
                    status TEXT NOT NULL DEFAULT 'PRO',
                    max_activations INTEGER NOT NULL DEFAULT 2,
                    activated_machines JSONB NOT NULL DEFAULT '[]'::jsonb,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
            """)
        conn.commit()


def generate_license_key():
    chars = string.ascii_uppercase + string.digits
    groups = ["".join(secrets.choice(chars) for _ in range(4)) for _ in range(4)]
    return "SONICPRO-" + "-".join(groups)


def require_admin_secret():
    provided = request.headers.get("X-Admin-Secret", "").strip()
    return bool(ADMIN_SECRET) and provided == ADMIN_SECRET


def get_license(license_key):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT license_key, status, max_activations, activated_machines, created_at
                FROM licenses
                WHERE license_key = %s
            """, (license_key,))
            return cur.fetchone()


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "ok",
        "service": "Sonic License Server"
    }), 200


@app.route("/create-license", methods=["POST"])
def create_license():
    if not require_admin_secret():
        return jsonify({
            "success": False,
            "message": "Otillåten begäran"
        }), 403

    data = request.get_json(silent=True) or {}
    status = str(data.get("status", "PRO")).strip().upper() or "PRO"

    try:
        max_activations = int(data.get("max_activations", 2))
    except Exception:
        max_activations = 2

    if max_activations < 1:
        max_activations = 1

    while True:
        key = generate_license_key()
        if not get_license(key):
            break

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO licenses (license_key, status, max_activations, activated_machines)
                VALUES (%s, %s, %s, %s::jsonb)
            """, (
                key,
                status,
                max_activations,
                json.dumps([])
            ))
        conn.commit()

    return jsonify({
        "success": True,
        "license_key": key,
        "status": status,
        "max_activations": max_activations
    }), 200


@app.route("/verify", methods=["POST"])
def verify_license():
    data = request.get_json(silent=True) or {}

    key = str(data.get("license_key", "")).strip().upper()
    machine_id = str(data.get("machine_id", "")).strip()

    if not key or not machine_id:
        return jsonify({
            "valid": False,
            "message": "license_key och machine_id krävs"
        }), 400

    license_info = get_license(key)

    if not license_info:
        return jsonify({
            "valid": False,
            "message": "Licensen finns inte"
        }), 200

    status = str(license_info.get("status", "TRIAL")).upper()
    max_activations = int(license_info.get("max_activations", 2))
    activated_machines = license_info.get("activated_machines") or []

    if machine_id in activated_machines:
        return jsonify({
            "valid": True,
            "status": status,
            "message": "Licensen är redan aktiverad på denna dator"
        }), 200

    if len(activated_machines) < max_activations:
        activated_machines.append(machine_id)

        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE licenses
                    SET activated_machines = %s::jsonb
                    WHERE license_key = %s
                """, (
                    json.dumps(activated_machines),
                    key
                ))
            conn.commit()

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


@app.route("/reset-license", methods=["POST"])
def reset_license():
    if not require_admin_secret():
        return jsonify({
            "success": False,
            "message": "Otillåten begäran"
        }), 403

    data = request.get_json(silent=True) or {}
    key = str(data.get("license_key", "")).strip().upper()

    if not key:
        return jsonify({
            "success": False,
            "message": "license_key krävs"
        }), 400

    if not get_license(key):
        return jsonify({
            "success": False,
            "message": "Licensen finns inte"
        }), 404

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE licenses
                SET activated_machines = '[]'::jsonb
                WHERE license_key = %s
            """, (key,))
        conn.commit()

    return jsonify({
        "success": True,
        "message": "Licensen återställd"
    }), 200


@app.route("/licenses", methods=["GET"])
def list_licenses():
    if not require_admin_secret():
        return jsonify({
            "success": False,
            "message": "Otillåten begäran"
        }), 403

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT license_key, status, max_activations, activated_machines, created_at
                FROM licenses
                ORDER BY created_at DESC
            """)
            rows = cur.fetchall()

    return jsonify(rows), 200


init_db()