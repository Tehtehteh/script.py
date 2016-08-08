import os
import sqlite3 as lite
from hashlib import md5
from datetime import datetime
import time
from configparser import ConfigParser


#------------------- INIT CONFIG IF NOT EXISTS, PASS IF EXISTS ------------#
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
            #print(users)
            cfg_new['MAIN']['extensions'] = '\n'.join(extensions_conf)
            cfg_new['MAIN']['excludes'] = '\n'.join(excludes)
            cfg_new.write(f)
    else:
        with open(config_name, "w+", encoding="UTF-8") as f:
            cfg.add_section("MAIN")
            cfg['MAIN']['Users'] = '\n'.join(list(os.walk(path))[0][1])
            cfg['MAIN']['extensions'] = '\n'.join(extensions)
            cfg['MAIN']['excludes'] = ''
            cfg.write(f)

#TODO config for extensions, excludes and users
#------------- GET TUPLE OF USERS, EXTENSIONS -------------------------#

def initEverything(config_name):
    cfg = ConfigParser()
    cfg.read(config_name)
    users = cfg['MAIN']['Users'].split("\n")
    extensions = cfg['MAIN']['extensions'].split("\n")
    return users, extensions

#------------- GET LIST OF USERS DIRECTORIES (STR) --------------------#

def initUsers(path):
    for x in os.walk(path):
        yield x[1]

#---------------------- RECURSIVE FILE SEARCH (ARGUMENT IS USER DIRECTORY (absolutepath)) -----------__#

def get_filepaths(directory):
    file_paths = []
    for root, directories, files in os.walk(directory):
        for filename in files:
            file_paths.append(os.path.join(root,filename))
    return file_paths

#--------------------- CREATE FILE HASH, ARGUMENT IS ABSOLUTE PATH TO FILE -------------------------#

def createHash(path_to_file, BLOCKSIZE=1024):
    hasher = md5()
    if not path_to_file.endswith("~"):
        with open(path_to_file, "rb") as filepath:
            buf = filepath.read(BLOCKSIZE)
            while len(buf) > 0:
                hasher.update(buf)
                buf = filepath.read(BLOCKSIZE)
            return hasher.hexdigest()[:16]

#--------------------- TEST FUNCTION FOR OUTPUTTING USERS IN DB ---------------------------------__#

def getUsersFromDb(db_name):
    with lite.connect(db_name) as con:
        cur = con.cursor()
        try:
            cur.execute("select * from Users")
        except Exception as e:
            with open("error.log", "w+", encoding="utf-8") as log:
                log.write(str(e) + " ".join(str(datetime.now())) + "\n")



#--------------- MAKE DB INCLUDING TABLES IF NO DB FOUND ------------------ #

def initDBFromScratch(userlist, extensions, path, db_name):
    with lite.connect(db_name) as con:
        cur = con.cursor()
        try:
            cur.execute("create table Users (name TEXT primary key)")
            cur.execute("create table File (path TEXT primary key, old_hash TEXT, new_hash TEXT, flag_exists INTEGER,"
                        "date_checked datetime, accepted INTEGER, name TEXT, foreign key(name) references Users(name))")
            for user in userlist:
                cur.execute("insert into Users values (?)", (user,))
                for file in get_filepaths(os.path.join(path + user)):
                    print(type(file), "----- QEQ")
                    if file.endswith(tuple(extensions)):
                        cur.execute("insert into File values(?,?,?,?,?,?,?)", (file, createHash(file), '', 1,
                                                                              time.strftime('%Y-%m-%d %H:%M:%S'),
                                                                              0, user))
        except Exception as e:
            with open("error.log", "a+", encoding="utf-8") as log:
                log.write(str(e) + " ".join(str(datetime.now().time())) + "\n")
        finally:
            con.commit()

#------------------- CREATE HASH FOR NEW USERS ---------------#

def userCreated(user, extensions, cur, path):
        try:
            cur.execute("insert into Users values ('{}')".format(user))
            for file in get_filepaths(os.path.join(path+user)):
                if file not in [x[0] for x in cur.execute("Select * from File").fetchall()] and file.endswith(tuple(extensions)):
                    cur.execute("insert into File values(?,?,?,?,?,?,?)", (file, '', createHash(file), 1,
                                                                               time.strftime('%Y-%m-%d %H:%M:%S'),
                                                                               0, user))
        except Exception as e:
                with open("error.log", "a+", encoding="utf-8") as log:
                    log.write(str(e) + " ".join(str(datetime.now().time())) + "\n")

# ----------------- UPDATE DB IN CRON ------------------------#

def updateDBCron(userlist, extensions, path, db_name):
    with lite.connect(db_name) as con:
        cur = con.cursor()
        try:
            for user in userlist:
                if user not in [x[0] for x in cur.execute("Select * from Users").fetchall()]:
                    userCreated(user, extensions, cur, path)
                else:
                    for file in get_filepaths(os.path.join(path + user)):
                        if file not in [x[0] for x in cur.execute("Select * from File where name='{}'".format(user)).fetchall()]\
                                and file.endswith(tuple(extensions)):
                                    cur.execute("insert into File values(?,?,?,?,?,?,?)", (file, createHash(file), '', 1,
                                                                                      time.strftime('%Y-%m-%d %H:%M:%S'),
                                                                                      0, user))
                        elif file.endswith(tuple(extensions)) and createHash(file)!=cur.execute("Select *"
                                                                                       " from file where path='{}'".format(file)).fetchall()[0][1]:
                            cur.execute("Update file set new_hash='{0}' where path='{1}'".format(createHash(file), file))
                        for N_file in [x[0] for x in cur.execute("Select path from file where name=?", (user,)).fetchall()]:
                            if N_file not in get_filepaths(os.path.join(path + user)):
                                print("File not found anymore ---", N_file)
                                cur.execute("Update file set flag_exists=? where path=?", (0, N_file))
        except Exception as e:
            with open("error.log", "a+", encoding="utf-8") as log:
                log.write(str(e) + " " + str(datetime.now().time()) + "\n")
        finally:
            con.commit()
            with open("success.log", "a+", encoding="utf-8") as log:
                log.write("Successfully updated db at " +  str(datetime.now().time())+ "\n")

#----------------- MAIN FUNC -------------------------------#
def main():
    new_path = "/var/www/"
    old_path = "/home/user6/userstest/"
    init_extensions = (".php", ".js", ".html", ".css")
    init_users = list(initUsers(old_path))[0]
    config_name = "config.ini"
    db_name = "test.db"
    initConfig(old_path, init_users, init_extensions, config_name)
    users, extensions = initEverything(config_name)
    #print((extensions))
    #print(users)
    if (not os.path.exists(db_name)):
        initDBFromScratch(users, extensions, old_path, db_name)
    else:
        updateDBCron(users, extensions, old_path, db_name)

if __name__=='__main__':
    main()

#TODO success.log