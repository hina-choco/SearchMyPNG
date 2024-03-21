import modules.scripts as scripts
from modules import script_callbacks
import gradio as gr
from PIL import Image as PILImage
from sqlalchemy import create_engine, Column, Integer, String, asc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text

def on_ui_tabs():
    with gr.Blocks(analytics_enabled=False) as ui_component:
        with gr.Row():
            checkbox = gr.Checkbox(
                False,
                label="All images"
            )
            textSearch = gr.Textbox(
                label="Search word", interactive=True, lines=1
            )
            btn = gr.Button(
                "Search", scale=1
            )
        with gr.Row():
            listdata = gr.DataFrame(
                label="result list",
                show_label = False,
                interactive = False,
                headers=["dir", "fname", "prompt", "topdir"],
                datatype=["str", "str", "str", "str"],
                col_count=4, height=480,
                order_by=['dir', 'fname'],
                order_directions=['ascending', 'ascending'],
            )
            gallery = gr.Image(
                label="image",
                show_label=False,
                type='pil', height=480,
            )
        with gr.Row():
            promptText = gr.TextArea(
                label="Prompt", interactive=False, lines=10
            )

        btn.click(
            search_db,
            inputs = [checkbox, textSearch],
            outputs = [listdata],
        )
        listdata.select(
            display_image,
            inputs = [listdata],
            #outputs = [gallery],
            outputs = [gallery, promptText],
        )

        return [(ui_component, "SearchMyPNG", "SearchMyPNG_tab")]

def display_image(selected_index: gr.SelectData, listdata):
    fname: String = listdata.iloc[selected_index.index[0]].fname
    dir: String = listdata.iloc[selected_index.index[0]].dir
    if fname == "" :
        return

    prompt: String = listdata.iloc[selected_index.index[0]].prompt
    topdir: String = listdata.iloc[selected_index.index[0]].topdir
    file_path: String = topdir + dir + '/' + fname
    try :
        image = PILImage.open(file_path)
    except Exception as e:
        return
    return image, prompt


def search_db(checkbox, textSearch):
    dbname = 'sqlite:///extensions/SearchMyPNG/SDImages.db'

    # ベースクラスを作成する。 
    Base = declarative_base()
    # ユーザクラスを定義する。 
    class CImage(Base):     
        __tablename__ = 'images'
        id: Integer = Column(Integer, primary_key=True)
        fname: String = Column(String)
        dir: String = Column(String)
        prompt: String = Column(String)
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
        if count > 0 :
            cimage = limages[0]
            ret[0] = [cimage.dir,cimage.fname,cimage.prompt,Topdir]
            for i in range(1,len(limages)):
                cimage = limages[i]
                ret.append([cimage.dir,cimage.fname,cimage.prompt,Topdir])
    else :
        dir: str = ""
        #同じディレクトリは登録しない
        for cimage in cimages:
            if dir != cimage.dir :
                if dir == "":
                    ret[0] = [cimage.dir,cimage.fname,cimage.prompt,Topdir]
                else:
                    ret.append([cimage.dir,cimage.fname,cimage.prompt,Topdir])
                dir = cimage.dir

    # セッションを閉じる。
    session.close()
    return ret

script_callbacks.on_ui_tabs(on_ui_tabs)