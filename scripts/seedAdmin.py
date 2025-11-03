# scripts/seed_admins.py
"""
Seed initial admin users.
- Uses instance/config.py for DB path and app factory.
- Prefers environment variables; falls back to interactive prompts.
"""
import sys, os

# Go one folder up from /scripts to the project root (where /app lives)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from getpass import getpass
from app import create_app
from app.database import db
from app.models import Admin

def prompt_or_env(env_key, prompt_text, secret=False):
    val = os.environ.get(env_key)
    if val:
        print(f"{env_key} found in environment, using that value.")
        return val
    # prompt
    if secret:
        return getpass(prompt_text + ": ")
    return input(prompt_text + ": ")

def create_if_not_exists(username, password, role="admin"):
    existing = Admin.query.filter_by(username=username).first()
    if existing:
        print(f"[skip] user '{username}' already exists (role={existing.role})")
        return existing
    u = Admin(username=username, password=password, role=role)
    db.session.add(u)
    db.session.commit()
    print(f"[created] {role} '{username}'")
    return u

def main():
    app = create_app()
    with app.app_context():
        # Superadmin
        super_username = prompt_or_env("SEED_SUPER_USERNAME", "Enter superadmin username", secret=False)
        super_password = prompt_or_env("SEED_SUPER_PASSWORD", "Enter superadmin password", secret=True)
        if not super_username or not super_password:
            print("Superadmin username/password must be provided. Aborting.")
            return
        create_if_not_exists(super_username, super_password, role="superadmin")

        # Admin (candidate)
        admin_username = prompt_or_env("SEED_ADMIN_USERNAME", "Enter candidate admin username", secret=False)
        admin_password = prompt_or_env("SEED_ADMIN_PASSWORD", "Enter candidate admin password", secret=True)
        if not admin_username or not admin_password:
            print("Admin username/password must be provided. Aborting.")
            return
        create_if_not_exists(admin_username, admin_password, role="admin")

if __name__ == "__main__":
    main()