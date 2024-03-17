"# SearchMyPNG" 

sqlite3で作成したDBからキーワード検索を行なってファイル一覧のリストを表示します。

![SSS2024-03-05 162036](https://github.com/hina-choco/SearchMyPNG/assets/162294996/61695cef-48c0-4eb3-ade6-d367e8c0c9f2)

#DataBaseの作成

cmd.exeを起動してcreateDB.pyでデータベース（SDimages.db）を作成します。

Usage: createDB.py [ -init ディレクトリ | -renew [ディレクトリ] | -update [ディレクトリ] ]<br>
Options:<br>
  -init ディレクトリ: データベースの初期化を行ないます。引数のディレクトリを基本ディレクトリとして記録し、基本ディレクトリ内にあるすべてのPNGファイルの記録を行ないます。引数のディレクトリは必須項目です。<br>
  -renew：データベースをクリアして再構築します。引数にディレクトリがある場合には、基本ディレクトリを新しいディレクトリに変更して再検索します。<br>
  -update：データベースを更新します。引数に基本ディレクトリ以下のディレクトリを指定して部分的な修正が可能です。<br>
  
  引数がディレクトリのみの場合には、データベースへの追加を行ないます。<br>

#使用例）<br>
1. SDの出力ディレクトリがD:\Pictureで初回起動する場合<br>
  createDB.py -init D:\Picture<br>
2. D:\Picture\2024-03-16に画像の増減があった場合<br>
  createDB.py -update D:\Picture\2024-03-16<br>
3. D:\Picture\2024-03-17に画像の新規追加があった場合<br>
  createDB.py D:\Picture\2024-03-17<br>
