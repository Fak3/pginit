#!/usr/bin/env python
import os, sys
from textwrap import dedent

import psycopg2


def postgres_connect(db_config, **kwargs):
    args = "user='%(USER)s' password='%(PASSWORD)s' dbname='%(NAME)s' host='%(HOST)s' port='%(PORT)s'"
    conn = psycopg2.connect(args % dict(db_config, **kwargs))

    # It is required to run CREATE DATABASE statement outside of transactions.
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    return conn


def postgres_connect_superuser(db_config):
    superuser = input('Please enter postgres superuser name [default: postgres]:')
    superuser = superuser.strip() or 'postgres'
    try:
        conn = postgres_connect(db_config, USER=superuser, PASSWORD='', NAME='postgres')
    except Exception as e:
        if re.search('role ".*" does not exist', str(e)):
            print(str(e))
        elif 'password' in str(e):
            message = dedent('''\n
                Failed to connect as '%s' using empty password.
                To fix this, please consider setting 'trust' policy for local users in pg_hba.conf,
                as in the example below:

                ############################# pg_hba.conf ############################
                # TYPE  DATABASE        USER            ADDRESS                 METHOD
                local   all             all                                     trust
                host    all             all             127.0.0.1/32            trust
                host    all             all             ::1/128                 trust
            ''' % username)
            raise Exception(message) from e
        else:
            raise

    return conn


def postgres_init(connection, user, password, database):
    print(f"Trying to create user '{user}' ...")
    cur = connection.cursor()

    try:
        cur.execute(f"create user {user} password '{password}' createdb;")
    except Exception as e:
        if f'role "{user}" already exists' in str(e):
            print(str(e).strip())
        else:
            raise
    else:
        print(f"create user {user} ok")


    # Also create user's own database to be able to login with psql
    try:
        cur.execute(f"create database {user} owner = {user};")
    except Exception as e:
        if f'database "{user}" already exists' in str(e):
            print(str(e).strip())
        else:
            raise
    else:
        print(f"create database {user} ok")

    print(f"Trying to create database '{database}' ...")
    try:
        cur.execute(f"create database {database} owner = {user};")
    except Exception as e:
        if f'database "{database}" already exists' in str(e):
            print(str(e).strip())
        else:
            raise
    else:
        print(f"create database {database} ok")


def main():
    sys.path.insert(0, os.getcwd())

    if len(sys.argv) == 1 and 'DJANGO_SETTINGS_MODULE' not in os.environ:
        print('Please provide settings path or set DJANGO_SETTINGS_MODULE env variable.')
        sys.exit(1)
    elif len(sys.argv) == 2:
        os.environ['DJANGO_SETTINGS_MODULE'] = sys.argv[1]
    elif len(sys.argv) > 2:
        print('Too many arguments!')
        sys.exit(1)

    from django.conf import settings

    DB = settings.DATABASES['default']
    conn = postgres_connect_superuser(DB)

    postgres_init(conn, DB['USER'], DB['PASSWORD'], DB['NAME'])


if __name__ == '__main__':
    main()
