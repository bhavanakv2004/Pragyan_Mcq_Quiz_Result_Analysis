from datetime import datetime


def log_activity(user, action):
    with open("logs/audit_log.txt", "a") as f:
        f.write(f"{datetime.now()} | {user} | {action}\n")
