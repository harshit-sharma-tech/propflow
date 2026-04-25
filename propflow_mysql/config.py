# ─────────────────────────────────────────────
# MySQL Database Configuration
# ─────────────────────────────────────────────
# Change these values to match YOUR MySQL setup
# ─────────────────────────────────────────────

# DB_CONFIG = {
#     'host'    : 'localhost',   # or your MySQL server IP
#     'port'    : 3306,          # default MySQL port
#     'user'    : 'root',        # your MySQL username
#     'password': 'password',  # ← CHANGE THIS
#     'database': 'harsh',    # database name (created by init_db.py)
# }


import os

DB_CONFIG = {
    'host'    : os.environ.get('MYSQLHOST', 'localhost'),
    'port'    : int(os.environ.get('MYSQLPORT', 3306)),
    'user'    : os.environ.get('MYSQLUSER', 'root'),
    'password': os.environ.get('MYSQLPASSWORD', ''),
    'database': os.environ.get('MYSQLDATABASE', 'railway'),
}