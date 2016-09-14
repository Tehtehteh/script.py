import os
import sqlite3 as lite
from hashlib import md5
from datetime import datetime
import time
import argparse
import sys
from tqdm import tqdm
from configparser import ConfigParser


# ------------------- INIT CONFIG IF NOT EXISTS, ADD IN SECTIONS IF EXISTS ------------#
def initConfig(path, users, extensions, config_name):
    cfg = ConfigParser()
    if os.path.exists(config_name):
        cfg.read(config_name)
        excludes = cfg['MAIN']['excludes'].split("\n")
        extensions_conf = cfg['MAIN']['extensions'].split('\n')
        with open(config_name, "w+", encoding="UTF-8") as f:
            cfg_new = ConfigParser()
            cfg_new.read(config_name)
            cfg_new.add_section('MAIN')
            cfg_new['MAIN']['Users'] = '\n'.join(set(users) - set(cfg['MAIN']['excludes'].split('\n')))
            cfg_new['MAIN']['extensions'] = '\n'.join(extensions_conf)
            cfg_new['MAIN']['excludes'] = '\n'.join(excludes)
            cfg_new.write(f)
    else:
        with open(config_name, "w+", encoding="UTF-8") as f:
            cfg.add_section("MAIN")
            cfg['MAIN']['Users'] = '\n'.join([x for x in (os.walk(path))][0][1])
            cfg['MAIN']['extensions'] = '\n'.join(extensions)
            cfg['MAIN']['excludes'] = ''
            cfg.write(f)


# ------------- GET TUPLE OF USERS, EXTENSIONS -------------------------#

def initEverything(config_name):
    cfg = ConfigParser()
    cfg.read(config_name)
    users = cfg['MAIN']['Users'].split("\n")
    extensions = cfg['MAIN']['extensions'].split("\n")
    excludes = cfg['MAIN']['excludes'].split("\n")
    return users, extensions, excludes


# ---------------------- RECURSIVE FILE SEARCH (ARGUMENT IS USER DIRECTORY (absolutepath)) -----------__#

def get_filepaths(directory):
    file_paths = []
    try:
        for root, directories, files in os.walk(directory):
            for filename in files:
                file_paths.append(os.path.join(root, filename))
    except Exception as e:
        print("error encountered", e, "processing directory", directory)
    return file_paths


# --------------------- CREATE FILE HASH, ARGUMENT IS ABSOLUTE PATH TO FILE -------------------------#

def createHash(path_to_file, BLOCKSIZE=1024):
    hasher = md5()
    if not path_to_file.endswith("~"):
        with open(path_to_file, "rb") as filepath:
            buf = filepath.read(BLOCKSIZE)
            while len(buf) > 0:
                hasher.update(buf)
                buf = filepath.read(BLOCKSIZE)
            return hasher.hexdigest()[:16]


# --------------------- TEST FUNCTION FOR OUTPUTTING USERS IN DB ---------------------------------__#

def getUsersFromDb(db_name):
    with lite.connect(db_name) as con:
        cur = con.cursor()
        try:
            cur.execute("select * from Users")
        except Exception as e:
            with open("error.log", "w+", encoding="utf-8") as log:
                log.write(str(e) + " ".join(str(datetime.now())) + "\n")


# --------------- MAKE DB INCLUDING TABLES IF NO DB FOUND ------------------ #

def initDBFromScratch(userlist, extensions, path, db_name):
    with lite.connect(db_name) as con:
        cur = con.cursor()
        try:
            cur.execute("create table Users (name TEXT primary key not null)")
            cur.execute(
                'create table File (path TEXT primary key not null, old_hash TEXT, new_hash TEXT, flag_exists INTEGER,'
                'date_checked datetime, accepted INTEGER, name TEXT, foreign key(name) references Users(name) '
                'on delete cascade)')
            for user in userlist:
                cur.execute("insert into Users values (?)", (user,))
                for file in list(filter(lambda x: x.endswith(tuple(extensions)), get_filepaths(os.path.join(path, user)))):
                    cur.execute("insert into File values(?,?,?,?,?,?,?)", (file, '', createHash(file), 1,
                                                                               time.strftime('%Y-%m-%d %H:%M:%S'),
                                                                               0, user))
        except Exception as e:
            with open("error.log", "a+", encoding="utf-8") as log:
                log.write('Error encountered while initing DB from scratch: {0}{1}\n'.format(str(e), " ".join(
                    str(datetime.now().time()))))
        finally:
            con.commit()


# ------------------- CREATE HASH FOR NEW USERS ---------------#

def userCreated(user, extensions, cur, path):
    try:
        cur.execute("insert into Users values ('{}')".format(user))
        for file in tqdm(get_filepaths(os.path.join(path,user)), unit='File'):
            if file.endswith(tuple(extensions)) and file not in [x[0] for x in cur.execute("Select * from File ").fetchall()]:
                cur.execute("insert into File values(?,?,?,?,?,?,?)", (file, '', createHash(file), 1,
                                                                       time.strftime('%Y-%m-%d %H:%M:%S'),
                                                                       0, user))
    except Exception as e:
        pass
        with open("error.log", "a+", encoding="utf-8") as log:
            log.write(str(e) + " ".join(str(datetime.now().time())) + "\n")
    finally:
        with open("success.log", "a+", encoding="utf-8") as log:
            log.write(
                "Successfully added new user({}) and his files @  ".format(user) + str(datetime.now().time()) + "\n")


# ----------------- UPDATE DB IN CRON ------------------------#

def updateDBCron(userlist, extensions, excludes, path, db_name):
    with lite.connect(db_name) as con:
        cur = con.cursor()
        try:
            if excludes[0]:
                print("Trying to delete users from exclude config:")
                for exclude in tqdm(excludes, unit='User'):
                    cur.execute("Delete from Users where name=?", (exclude,))
                    cur.execute("Delete from File where name=?", (exclude,))
                    with open("success.log", "a+", encoding="utf-8") as log:
                        log.write(
                            "Successfully deleted exclude " + exclude + " in db at " + str(datetime.now().time()) + "\n")
            for user in userlist:
                print("Here is before user check")
                if user not in excludes and user not in [x[0] for x in cur.execute("Select name from Users").fetchall()]:
                    print('Creating new user', user, ' and fetching his files.')
                    userCreated(user, extensions, cur, path)
                    print("Here in user created")
                else:
                    files = get_filepaths(os.path.join(path, user))
                    for file in list(filter(lambda x: x.endswith(tuple(extensions)), files)):
                        if file.endswith(tuple(extensions)) and file not in [x[0] for x in
                                        cur.execute("Select path from File where name='{}'".format(user)).fetchall()]:
                            cur.execute("insert into File values(?,?,?,?,?,?,?)", (file, '', createHash(file), 1,
                                                                                   time.strftime('%Y-%m-%d %H:%M:%S'),
                                                                                   0, user))
                        elif file.endswith(tuple(extensions)) and createHash(file) != cur.execute('Select old_hash'
                                                                                                 ' from file where '
                                                                                                  'path=?',(file,)).fetchone()[0]:
                            cur.execute(
                                "Update file set new_hash='{0}' where path='{1}'".format(createHash(file), file))
                    for N_file in [x[0] for x in
                                   cur.execute("Select path from File where name=? and flag_exists=?", (user,1)).fetchall()]:
                        if N_file not in files:
                            print("File not found: ", N_file)
                            cur.execute("Update File set flag_exists=? where path=?", (0, N_file))
        except Exception as e:
            pass
            with open("error.log", "a+", encoding="utf-8") as log:
                log.write(str(e) + " " + str(datetime.now().time()) + "\n")
        finally:
            con.commit()
            with open("success.log", "a+", encoding="utf-8") as log:
                log.write("Successfully updated db at " + str(datetime.now().time()) + "\n")


# ----------------- MAIN FUNC -------------------------------#

def main():
    # parser = argparse.ArgumentParser()
    # parser.add_argument("path", help="Top directory for user's directories to check files in")
    # args = parser.parse_args()
    path = '/home/user6/userstest/'
    init_users = []
    init_extensions = (".php", ".js", ".html", ".css")
    try:
        init_users.extend(filter(lambda x: not os.path.isfile(x) and not x.endswith('~'), os.listdir(path)))
    except Exception as e:
        print('Error encountered: ', e, file=sys.stderr)
    config_name = "config.ini"
    db_name = "Monitor/test.db"
    initConfig(path, init_users, init_extensions, config_name)
    users, extensions, excludes = initEverything(config_name)
    if not os.path.exists(db_name):
        initDBFromScratch(users, extensions, path, db_name)
    else:
        updateDBCron(users, extensions, excludes, path, db_name)


if __name__ == '__main__':
    main()
