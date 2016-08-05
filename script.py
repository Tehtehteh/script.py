import os
import sqlite3 as lite
from hashlib import md5
from datetime import datetime
import time
from configparser import ConfigParser

#------------ USER's LIST GENERATOR --------------------------#
def initString(users):
    for user in users:
        yield user

#--------------- NEW INIT CONFIG -------------------------#
def newinitConfig(path):
    cfg = ConfigParser()
    if os.path.exists(path + "config.ini"):
        cfg.read(path + "config.ini")
        cfg.add_section("MAIN")
        pass
    #TODO generate valid config file and set users based on set(users) - set(excludes)
#------------------- INIT CONFIG IF NOT EXISTS, PASS IF EXISTS ------------#
def initConfig(path, users, extensions):
    cfg = ConfigParser()
    if os.path.exists(path + "config.ini"):
        cfg.read(path + "config.ini")
        excludes = cfg['MAIN']['excludes'].split("\n")
        extensions_conf = cfg['MAIN']['extensions'].split('\n')
        with open(path + "config.ini", "w+", encoding="UTF-8") as f:
            cfg_new = ConfigParser()
            cfg_new.read(path + "config.ini")
            cfg_new.add_section('MAIN')
            cfg_new['MAIN']['Users'] = '\n'.join(set(users) - set(cfg['MAIN']['excludes'].split('\n')))
            print(users)
            cfg_new['MAIN']['extensions'] = '\n'.join(extensions_conf)
            cfg_new['MAIN']['excludes'] = '\n'.join(excludes)
            cfg_new.write(f)
    else:
        with open(path + "config.ini", "w+", encoding="UTF-8") as f:
            cfg.add_section("MAIN")
            cfg['MAIN']['Users'] = '\n'.join(list(os.walk(path))[0][1])
            cfg['MAIN']['extensions'] = '\n'.join(extensions)
            cfg['MAIN']['excludes'] = ''
            cfg.write(f)

#TODO config for extensions, excludes and users

#------------- GET LIST OF USERS DIRECTORIES (STR) --------------------#

def initUsers(path):
    for x in os.walk(path):
        yield x[1]

#-------------- ASSIGNING DICT -----------------------------#

def searchFiles(directory, extensions):
    directory = "C:\\Users\\tehfv\\Desktop\\rte\\" + user
    files = [{'filename': x, 'hash': os.urandom(5)}
             for x in lsr(directory)[1]
             if any(map(lambda q: x.endswith(q), extensions))]

#-------------- RECURSIVE FILE SEARCH ----------------------#

def lsr(path):
    items = os.listdir(os.path.abspath(path))
    Dirs, Files = [], []
    for i in items:
        p = os.path.join(path, i)
        if os.path.isdir(p): Dirs.append(p)
        elif os.path.isfile(p): Files.append(p)
    ChildDirs, ChildFiles = [], []
    for d in Dirs:
        a, b = lsr(d)
        ChildDirs.extend(a)
        ChildFiles.extend(b)
    Dirs.extend(ChildDirs)
    Files.extend(ChildFiles)
    return Dirs, Files

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

def getUsersFromDb():
    with lite.connect('test.db') as con:
        cur = con.cursor()
        try:
            cur.execute("select * from Users")
        except Exception as e:
            with open("error.log", "w+", encoding="utf-8") as log:
                log.write(str(e) + " ".join(str(datetime.now())) + "\n")

#------------------ CREATE TABLE USERS AND INSERT TO IT ----------------_#

def initDB(userlist):
    print(userlist, "------ USER LIST ")
    with lite.connect('test.db') as con:
        cur = con.cursor()
        try:
            cur.execute("create table Users (name TEXT primary key)")
        except Exception as e:
            with open("error.log", "w+", encoding="utf-8") as log:
                log.write(str(e) + str(datetime.now().time()) + "\n")
        try:
            for user in userlist:
                cur.execute("insert into Users values (?)", user)
        except Exception as e:
            with open("error.log", "w+", encoding="utf-8") as log:
                log.write(str(e) + " ".join(str(datetime.now().time())) + "\n")

#--------------- MAKE DB INCLUDING TABLES IF NO DB FOUND ------------------ #

def initDBFromScratch(userlist, extensions, path):
    with lite.connect("test.db") as con:
        cur = con.cursor()
        try:
            cur.execute("create table Users (name TEXT primary key)")
            cur.execute("create table File (path TEXT primary key, old_hash TEXT, new_hash TEXT, flag_exists INTEGER,"
                        "date_checked datetime, accepted INTEGER, name TEXT, foreign key(name) references Users(name))")
            for user in userlist:
                cur.execute("insert into Users values (?)",(user,))
                for file in get_filepaths(os.path.join(path + user)):
                    if file.endswith(extensions):
                        cur.execute("insert into File values(?,?,?,?,?,?,?)",(file, createHash(file), '',1,
                                                                              time.strftime('%Y-%m-%d %H:%M:%S'),
                                                                              0,user))
        except Exception as e:
            with open("error.log", "a+", encoding="utf-8") as log:
                log.write(str(e) + " ".join(str(datetime.now().time())) + "\n")

#------------------- CREATE HASH FOR NEW USERS ---------------#

def userCreated(user, extensions, cur, path):
        try:
            cur.execute("insert into Users values ('{}')".format(user))
            for file in get_filepaths(os.path.join(path+user)):
                if (file) not in [x[0] for x in cur.execute("Select * from File").fetchall()] and file.endswith(extensions):
                    cur.execute("insert into File values(?,?,?,?,?,?,?)", (file, '', createHash(file), 1,
                                                                               time.strftime('%Y-%m-%d %H:%M:%S'),
                                                                               0, user))
        except Exception as e:
                with open("error.log", "a+", encoding="utf-8") as log:
                    log.write(str(e) + " ".join(str(datetime.now().time())) + "\n")

# ----------------- UPDATE DB IN CRON ------------------------#
def updateDBinCron(userList, extensions, path, db_name):
    with lite.connect(db_name) as con:
        cur = con.cursor()
        try:
            for user in userList:
                if user not in [x[0] for x in cur.execute("SELECT * FROM USERS").fetchall()]:
                    userCreated(user, extensions, cur, path)
                else:
                    for file in get_filepaths(path+user):
                        pass
                    #TODO set existence flag to 0, when file not found
        except Exception as e:
            print(e)


def updateDBCron(userlist, extensions, path):
    with lite.connect("test.db") as con:
        cur = con.cursor()
        try:
            for user in userlist:
                if user not in [x[0] for x in cur.execute("Select * from Users").fetchall()]:
                    userCreated(user, extensions, cur, path)
                else:
                    for file in get_filepaths(os.path.join(path + user)):
                        if file not in [x[0] for x in cur.execute("Select * from File where name='{}'".format(user)).fetchall()]\
                                and file.endswith(extensions):
                                    cur.execute("insert into File values(?,?,?,?,?,?,?)",(file, createHash(file), '',1,
                                                                                      time.strftime('%Y-%m-%d %H:%M:%S'),
                                                                                      0,user))
                        if file.endswith(extensions) and createHash(file)!=cur.execute("Select *"
                                                                                       " from file where path='{}'".format(file)).fetchall()[0][1]:
                            cur.execute("Update file set new_hash='{0}' where path='{1}'".format(createHash(file), file))
                        elif file.endswith(extensions):

                            #TODO check if file is not exists in DB -> add new file to DB
                            pass
        except Exception as e:
            with open("error.log", "a+", encoding="utf-8") as log:
                log.write(str(e) + " ".join(str(datetime.now().time())) + "\n")

#----------------- MAIN FUNC -------------------------------#
def main():
    new_path = "/var/www/"
    old_path = "/home/user6/userstest/"
    extensions = (".php", ".js", ".html", ".css")
    users = list(initUsers(old_path))[0]
    cfg = ConfigParser()
    initConfig(old_path, list(initUsers(old_path))[0], extensions)
    if (not os.path.exists("test.db")):
        initDBFromScratch(users, extensions, old_path)
    else:
        updateDBCron(users, extensions, old_path)

if __name__=='__main__':
    main()

#TODO success.log