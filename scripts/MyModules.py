import os
import modules.scripts as scripts
from modules import script_callbacks
import gradio as gr
from PIL import Image as PILImage
from sqlalchemy import create_engine, Column, Integer, String, asc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
import json

MODE_INIT = 0
MODE_UPDATE = 1

with open('config.json') as f:
    di = json.load(f)
topdir = (di['outdir_samples'])  # deep insider：キーを指定して値を取得

def on_ui_tabs():
    with gr.Blocks(analytics_enabled=False) as ui_component:
        with gr.Row():
            with gr.Column():
                textSearch = gr.Textbox(
                    label="Search word", interactive=True, lines=1
                )
                checkbox = gr.Checkbox(
                    False,
                    label="All images"
                )
            search_btn = gr.Button(
                "Search", scale=1
            )
            with gr.Column():
                dbini = gr.Button(
                    "Create Database", scale=1
                )
                dbupd = gr.Button(
                    "Update Database", scale=1
                )
        with gr.Row():
            listdata = gr.DataFrame(
                label="result list",
                show_label = False,
                interactive = False,
                headers=["dir", "fname", "prompt", "topdir"],
                datatype=["str", "str", "str", "str"],
                col_count=4, height=400,
                order_by=['dir', 'fname'],
                order_directions=['ascending', 'ascending'],
            )
            gallery = gr.Image(
                label="image",
                show_label=False,
                type='filepath', height=480,
            )
        with gr.Row():
            promptText = gr.TextArea(
                label="Prompt", interactive=False, lines=10
            )

        dbini.click(
            create_db
        )
        dbupd.click(
            update_db
        )
        search_btn.click(
            search_db,
            inputs = [checkbox, textSearch],
            outputs = [listdata],
        )
        listdata.select(
            display_image,
            inputs = [listdata],
            outputs = [gallery, promptText],
        )

    return [(ui_component, "SearchMyPNG", "SearchMyPNG_tab")]

def display_image(selected_index: gr.SelectData, listdata):
    fname: String = listdata.iloc[selected_index.index[0]].fname
    dir: String = listdata.iloc[selected_index.index[0]].dir
    if fname == "" :
        return "",""

    prompt: String = listdata.iloc[selected_index.index[0]].prompt
    topdir: String = listdata.iloc[selected_index.index[0]].topdir
    file_path: String = topdir + dir + '/' + fname
    image = file_path
    return image, prompt

# ベースクラスを作成する。 
Base = declarative_base()
# ユーザクラスを定義する。 
class CImage(Base):     
    __tablename__ = 'images'
    id: Integer = Column(Integer, primary_key=True)
    fname: String = Column(String)
    dir: String = Column(String)
    prompt: String = Column(String)

def get_metadata(file_path: str):
    try:
        img = PILImage.open(file_path)
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

def write_db(mode: int):
    dbname = 'sqlite:///extensions/SearchMyPNG/SDImages.db'

    try :
        timestamp_db = os.path.getctime('extensions/SearchMyPNG/SDImages.db')
        s = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp_db))
        #print( "db "+s )
    except Exception as e:
        mode = MODE_INIT
        print( "Create new SDImage.db")

    # エンジンを生成する 
    engine = create_engine(dbname)  
    # セッションを作成する。 
    Session = sessionmaker(bind=engine) 
    session = Session()

    result = session.execute(
        text("SELECT COUNT(*) FROM sqlite_master WHERE TYPE='table' AND NAME='env';")
    ).fetchone()
    if result == (0,): #存在しないとき
        print("Create new table env")
        session.execute( 
            text('CREATE TABLE env (id INTEGER PRIMARY KEY AUTOINCREMENT, topdir TEXT);')
        )
        sql = f"insert into env (topdir) values ('{topdir}');"
        session.execute( text(sql) )
        session.commit()
    else :
        if mode == MODE_INIT:
            session.execute( text('delete from env;') )
            sql = f"insert into env (topdir) values ('{topdir}');"
            session.execute( text(sql) )
            session.commit()

    result = session.execute(
        text("SELECT COUNT(*) FROM sqlite_master WHERE TYPE='table' AND NAME='images';")
    ).fetchone()
    if result == (0,): #存在しないとき
        print("Create new table images")
        session.execute(
            text('CREATE TABLE images(id INTEGER PRIMARY KEY AUTOINCREMENT, fname TEXT, dir TEXT, prompt TEXT);')
        )
        session.commit()
    else : 
        if mode == MODE_INIT:
            session.execute( text('DELETE from images;') )
            session.commit()

    count = 0
    if mode == MODE_INIT :
        countall = 0
        for root, dirs, files in os.walk(topdir):
            subdir = root.replace(topdir, '')
            for file in files:
                if file.lower().endswith('.png'):
                    countall += 1
        print( f"All:{countall}")

        dispper = 0
        for root, dirs, files in os.walk(topdir):
            subdir = root.replace(topdir, '')
#            print( "Add "+subdir )
            for file in files:
                if file.lower().endswith('.png'):
                    pngfile = os.path.join(root, file)
                    prompt = get_metadata(pngfile)
                    record = CImage(fname=file, dir=subdir, prompt=f"\'{prompt}\'")
                    session.add(record)
                    count += 1
                    percent = int( count/countall * 100 )
                    if (percent % 10) == 0: 
                        if percent > dispper:
                            print( f"{percent}% complete" )
                            dispper = percent
        session.commit()
        print(f"write {count} records.")
    else :
        for root, dirs, files in os.walk(topdir):
            subdir = root.replace(topdir, '')
            timestamp = os.path.getctime(root)
            if timestamp_db > timestamp : continue

            s = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
            print( "Update "+subdir+" "+s )
            sql = f"DELETE from images where dir like '{subdir}';"
            session.execute( text(sql) )
            for file in files:
                if file.lower().endswith('.png'):
                    pngfile = os.path.join(root, file)
                    prompt = get_metadata(pngfile)
                    record = CImage(fname=file, dir=subdir, prompt=f"\'{prompt}\'")
                    session.add(record)
                    count += 1
        session.commit()
        print(f"write {count} records.")

    # セッションを閉じる。
    session.close()
    engine.dispose()
    return

def create_db():
    print(
        "Building Database ... This can take a while, please check the progress in the terminal."
    )
    write_db( MODE_INIT )
    print( "Done.")
    return

def update_db():
    print(
        "Building Database ... This can take a while, please check the progress in the terminal."
    )
    write_db( MODE_UPDATE )
    print( "Done.")
    return

def search_db(checkbox, textSearch):
    dbname = 'sqlite:///extensions/SearchMyPNG/SDImages.db'

   # エンジンを生成する 
    engine = create_engine(dbname)  
    # セッションを作成する。 
    Session = sessionmaker(bind=engine) 
    session = Session()

    # Selectクエリを実行する。 
    result = session.execute( text('select topdir from env') )
    envs = list( result )
    Topdir = envs[0].topdir

    sql = f'\'%{textSearch}%\''
    cimages = session.query(CImage).filter(CImage.prompt.like(sql)).order_by(CImage.dir.asc(), CImage.fname.asc())
    ret = [[]]
    if (checkbox):
        #全部登録
        limages = list(cimages)
        count = len(limages)
        print( f"find {count} records" )
        if count > 0 :
            ret = [[]]*count
            for i in range(0,count):
                cimage = limages[i]
                ret[i] = [cimage.dir,cimage.fname,cimage.prompt,Topdir]
    else :
        dir: str = ""
        count = 0
        #同じディレクトリは登録しない
        for cimage in cimages:
            if dir != cimage.dir :
                if dir == "":
                    ret[0] = [cimage.dir,cimage.fname,cimage.prompt,Topdir]
                else:
                    ret.append([cimage.dir,cimage.fname,cimage.prompt,Topdir])
                count += 1
                dir = cimage.dir
        print( f"find {count} directories" )

    # セッションを閉じる。
    session.close()
    engine.dispose()
    return ret

script_callbacks.on_ui_tabs(on_ui_tabs)