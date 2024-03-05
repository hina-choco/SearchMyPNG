import modules.scripts as scripts
from modules import script_callbacks
import gradio as gr
from PIL import Image as PILImage
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Topdir = 'D:\\Picture\\'

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
                headers=["dir", "fname", "prompt"],
                datatype=["str", "str", "str"],
                col_count=3, height=480,
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
            display_metadata,
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
    fname = listdata.iloc[selected_index.index[0]].fname
    dir = listdata.iloc[selected_index.index[0]].dir
    if fname == "" or dir == "" :
        return

    prompt = listdata.iloc[selected_index.index[0]].prompt
    file_path = Topdir + dir + '/' + fname
    try :
        image = PILImage.open(file_path)
    except Exception as e:
        return
    return image, prompt


def display_metadata(checkbox, textSearch):
    dbname = 'sqlite:///extensions/SearchMyPNG/SDImages.db'

    # ベースクラスを作成する。 
    Base = declarative_base()
    # ユーザクラスを定義する。 
    class User(Base):     
        __tablename__ = 'images'      
        id = Column(Integer, primary_key=True)
        fname = Column(String)
        dir = Column(String)
        prompt = Column(String)
    # エンジンを生成する 
    engine = create_engine(dbname)  
    # セッションを作成する。 
    Session = sessionmaker(bind=engine) 
    session = Session()

    # Selectクエリを実行する。 
    sql = f'\'%{textSearch}%\''
    users = session.query(User).filter(User.prompt.like(sql))
    ret = [[""]*3]
    if (checkbox):
        #全部登録
        for user in users:
            rest = user.dir.replace(Topdir, '')
            ret.append([rest,user.fname,user.prompt])
    else :
        dir = ""
        #同じディレクトリは登録しない
        for user in users:
            if dir != user.dir :
                rest = user.dir.replace(Topdir, '')
                ret.append([rest,user.fname,user.prompt])
                dir = user.dir

    # セッションを閉じる。
    session.close()
    return ret

script_callbacks.on_ui_tabs(on_ui_tabs)