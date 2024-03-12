"# SearchMyPNG" 

sqlite3で作成したDBからキーワード検索を行なってファイル一覧のリストを表示します。

![SSS2024-03-05 162036](https://github.com/hina-choco/SearchMyPNG/assets/162294996/61695cef-48c0-4eb3-ade6-d367e8c0c9f2)

#DataBaseの作成

cmd.exeを起動してcreateDB.pyでデータベース（SDimages.db）を作成します。

Usage: createDB.py [-renew | -update] [ディレクトリ]<br>
Options:<br>
  -renew：データベースをクリアして再構築します。-updateとは同時に指定できません<br>
  -update：データベースの重複している部分を更新します。-renewとは同時に指定できません<br>
  ディレクトリ：データベースに追加するディレクトリを指定します。指定が無い場合はソース内に指定されたディレクトリ（D:¥Picture）を使用します。<br>
  -renew,-update オプションを指定していない場合には、既存のデータベースに追加します。<br>
