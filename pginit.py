#!/usr/bin/env python
from __future__ import print_function
import os, sys, re
from textwrap import dedent

import psycopg2
from psycopg2.errors import DuplicateObject, DuplicateDatabase
import six


def postgres_connect(db_config, **kwargs):
    args = "user='%(USER)s' password='%(PASSWORD)s' dbname='%(NAME)s' host='%(HOST)s' port='%(PORT)s'"
    print('Connecting with %(HOST)s:%(PORT)s/%(NAME)s' % dict(db_config, **kwargs))
    conn = psycopg2.connect(args % dict(db_config, **kwargs))

    # It is required to run CREATE DATABASE statement outside of transactions.
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    return conn


def postgres_connect_superuser(db_config, username, dbname):
    try:
        conn = postgres_connect(db_config, NAME=dbname, USER=username, PASSWORD='')
    except Exception as e:
        if re.search('role ".*" does not exist', str(e)):
            raise
        elif 'password' in str(e) or 'authentication failed for user' in str(e):
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
            six.raise_from(Exception(message), e)
        else:
            raise

    return conn


def postgres_init(connection, user, password, database):
    print("Trying to create user '{user}' with password '{password}' ...".format(**locals()))
    cur = connection.cursor()

    try:
        cur.execute("create user {user} password '{password}' createdb;".format(**locals()))
    except DuplicateObject as e:
        print(str(e).strip())
    except Exception as e:
        if 'role "{user}" already exists'.format(**locals()) in str(e):
            print(str(e).strip())
        else:
            raise
    else:
        print("create user {user} ok".format(**locals()))


    # Also create user's own database to be able to login with psql
    try:
        cur.execute("create database {user} owner = {user};".format(**locals()))
    except DuplicateDatabase as e:
        print(str(e).strip())
    except Exception as e:
        if 'database "{user}" already exists'.format(**locals()) in str(e):
            print(str(e).strip())
        else:
            raise
    else:
        print("create database {user} ok".format(**locals()))

    print("Trying to create database '{database}' ...".format(**locals()))
    try:
        cur.execute("create database {database} owner = {user};".format(**locals()))
    except DuplicateDatabase as e:
        print(str(e).strip())
    except Exception as e:
        if 'database "{database}" already exists'.format(**locals()) in str(e):
            print(str(e).strip())
        else:
            raise
    else:
        print("create database {database} ok".format(**locals()))



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


    superuser = six.moves.input('Please enter postgres superuser name [default: postgres]:')
    superuser = superuser.strip() or 'postgres'

    DB = settings.DATABASES['default']
    conn = postgres_connect_superuser(DB, username=superuser, dbname='postgres')

    postgres_init(conn, DB['USER'], DB['PASSWORD'], DB['NAME'])

    conn = postgres_connect_superuser(DB, username=superuser, dbname=DB['NAME'])
    print("Trying to create extension hstore ...")
    cur = conn.cursor()
    cur.execute("CREATE EXTENSION IF NOT EXISTS hstore;")
    print("create extension ok")


if __name__ == '__main__':
    main()
