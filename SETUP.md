PostAnalyser - Setup & Deployment

Environment variables (recommended):

- SECRET_KEY: Flask secret key (optional)
- SESSION_TYPE: session storage (default: filesystem)
- SMTP_HOST: SMTP server host (e.g., smtp.gmail.com)
- SMTP_PORT: SMTP port (587)
- SMTP_USER: SMTP username
- SMTP_PASS: SMTP password
- EMAIL_FROM: optional from address (defaults to SMTP_USER)
- MYSQL_HOST: If set, enables MySQL mode (optional)
- MYSQL_PORT: MySQL port (default 3306)
- MYSQL_USER: MySQL user
- MYSQL_PASSWORD: MySQL password
- MYSQL_DATABASE: MySQL database name

If you want to migrate local sqlite data to MySQL, configure the MySQL env variables and run:

    python scripts/migrate_to_mysql.py

To initialize DB tables (sqlite or mysql):

    python -c "from db import init_db; init_db()"

SMTP/Email: If SMTP is not configured, the app will print email contents to console for development.

Security note: Do not commit credentials into source control. Use environment variables or a secrets manager in production.
