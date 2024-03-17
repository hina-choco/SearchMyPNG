#! /usr/bin/env python
import os
import sys
import sqlite3
import tkinter as tk
from PIL import Image

def display_metadata(file_path: str):
    try:
        img = Image.open(file_path)
        metadata = img.info
        info = ""
        for key, value in metadata.items():
            if key == 'workflow' :
                info = f"ComfyUI {key}"
            else :
                info = f"{value}"
    except Exception as e:
        info = "Error"
    return info

init: bool = False
update: bool = False
renew: bool = False
topdir = ""
argdir = ""
options = 0
for n in range(1,len(sys.argv)):
    arg = sys.argv[n]
    print( arg )
    if arg == "-update" : 
        update = True
        options += 1
    elif arg == "-renew" : 
        renew = True
        options += 1
    elif arg == "-init" :
        init = True
        options += 1
    else : argdir = arg
if options > 1 : 
    print("option err")
    sys.exit()

if init and argdir == "" :
    print("init need Topdir")
    sys.exit()

dbname = 'SDimages.db'
conn = sqlite3.connect(dbname)
cur = conn.cursor()

if init :
    cur.execute("SELECT COUNT(*) FROM sqlite_master WHERE TYPE='table' AND NAME='env';")
    if cur.fetchone() == (0,): #存在しないとき
        print("Create new table env")
        cur.execute(
            'CREATE TABLE env (id INTEGER PRIMARY KEY AUTOINCREMENT, topdir TEXT);'
        )
    else :
        cur.execute( 'DELETE from env;' )
    topdir = argdir
    cur.execute( f"insert into env (topdir) values ('{topdir}');" )
    conn.commit()
    print( f"init topdir={topdir}")
else :
    if renew and argdir != "" :
        topdir = argdir
        cur.execute( f"update env set topdir='{topdir}';" )
        conn.commit()
        print( f"renew topdir={topdir}")
    else :
        cur.execute( "SELECT topdir from env;")
        rows = list( cur.fetchall() )
        row = rows[0]
        topdir = str(row[0])
        print( f"get topdir={topdir}")
        if argdir == "" : argdir = topdir

cur.execute("SELECT COUNT(*) FROM sqlite_master WHERE TYPE='table' AND NAME='images';")
if cur.fetchone() == (0,): #存在しないとき
    print("Create new table images")
    cur.execute(
        'CREATE TABLE images(id INTEGER PRIMARY KEY AUTOINCREMENT, fname TEXT, dir TEXT, prompt TEXT);'
    )
    conn.commit()
else : 
    if renew or init :
        cur.execute( 'DELETE from images;' )
        conn.commit()

count = 0
for root, dirs, files in os.walk(argdir):
    if update :
        subdir = root.replace(topdir, '')
        cur.execute( f"DELETE from images where dir like '{subdir}';" )
    for file in files:
        if file.lower().endswith('.png'):
            pngfile = os.path.join(root, file)
            subdir = root.replace(topdir, '')
            prompt = display_metadata(pngfile)
            query = u'''insert into images (fname, dir, prompt) values (?, ?, ?) '''
            cur.execute( query, (f"{file}", f"{subdir}", f"\'{prompt}\'") )
            count += 1
conn.commit()
print(f"write {count} records.")

cur.close()
conn.close()
