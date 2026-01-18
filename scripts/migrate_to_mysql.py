import os
from db import migrate_sqlite_to_mysql

if __name__ == '__main__':
    print('Starting migration to MySQL...')
    migrate_sqlite_to_mysql()
    print('Done')