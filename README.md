"# SearchMyPNG" 

outputディレクトリ以下にあるPNGファイルをデータベース化し、キーワード検索を行なってファイル一覧のリストを表示します。

![SS-2024-06-17 212958](https://github.com/hina-choco/SearchMyPNG/assets/162294996/98452bbf-41b6-4f99-a9a7-96954707cb5f)
![SS-2024-06-17 213229](https://github.com/hina-choco/SearchMyPNG/assets/162294996/87559288-33e1-4464-bbbd-dc44ad6053ac)

#DataBaseの作成<BR>
・初回は"Create Database"ボタンをクリックしてデータベースの作成を行ないます。<BR>
・次回以降は"Update Database"ボタンをクリックするとデータベースの日付よりあとに変化したファイルをデータベースに追加します。<BR>

・検索時に「All images」にチェックが入っていればマッチングしたすべてのファイルをリストアップします。<BR>
チェックが入っていなければマッチングしたファイルのあるディレクトリ単位でリストアップします。

Ver1.0.3 変更点<BR>
・プロンプトの末尾に「'」が付いていたままだったのを修正

Ver1.02 変更点<BR>
・Send to txt2img でプロンプト等をtxt2imgタブに送れるようにした

Ver1.01 変更点<BR>
・config.sysが無い場合でもエラーにならないようにした<BR>
・プロンプトの先頭に「'」が付かないようにした
