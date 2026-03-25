import os
import json
import random
import string

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LICENSE_FILE = os.path.join(BASE_DIR, "app", "licenses.json")


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


def random_block(length=4):
    chars = string.ascii_uppercase + string.digits
    return "".join(random.choices(chars, k=length))


def generate_license_key():
    return f"SONICPRO-{random_block()}-{random_block()}-{random_block()}"


def create_license(status="PRO", max_activations=2):
    licenses = load_licenses()

    while True:
        key = generate_license_key()
        if key not in licenses:
            break

    licenses[key] = {
        "status": status,
        "max_activations": max_activations,
        "activated_machines": []
    }

    save_licenses(licenses)
    return key


if __name__ == "__main__":
    new_key = create_license(status="PRO", max_activations=1)
    print("Ny licens skapad:")
    print(new_key)