#! /usr/bin/env python
import os
import sys
import sqlite3
import tkinter as tk
from PIL import Image

Topdir = "D:\\Picture"

def display_metadata(file_path):
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

n = 0
update = False
renew = False
topdir = Topdir
options = 0
for arg in sys.argv :
    n += 1
    if n == 1 : continue
    if arg == "-update" : 
        update = True
        options += 1
    elif arg == "-renew" : 
        renew = True
        options += 1
    else : topdir = arg
if options > 1 : 
    print("option err")
    sys.exit()

dbname = 'SDimages.db'
conn = sqlite3.connect(dbname)
cur = conn.cursor()

cur.execute("SELECT COUNT(*) FROM sqlite_master WHERE TYPE='table' AND NAME='images';")
if cur.fetchone() == (0,): #存在しないとき
    print("Create new table")
    cur.execute(
        'CREATE TABLE images(id INTEGER PRIMARY KEY AUTOINCREMENT, fname TEXT, dir TEXT, prompt TEXT);'
    )
    conn.commit()

if renew :
    cur.execute(
        'DELETE from images;'
    )
    conn.commit()
    print("*renew* Delete all records.")

count = 0
for root, dirs, files in os.walk(topdir):
    if update :
        cur.execute( f"DELETE from images where dir like '{root}%';" )
    for file in files:
        if file.lower().endswith('.png'):
            pngfile = os.path.join(root, file)
            #print(pngfile)
            prompt = display_metadata(pngfile)
            query = u'''insert into images (fname, dir, prompt) values (?, ?, ?) '''
            cur.execute( query, (f"{file}", f"{root}", f"\'{prompt}\'") )
            count += 1
conn.commit()
print(f"write {count} records.")

cur.close()
conn.close()
