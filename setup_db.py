from sqlite_utils import Database

# データベースファイル名（まだなければ自動作成される）
db = Database("tasks.db")

# "tasks" テーブルを作成（存在しない場合のみ作成）
if "tasks" not in db.table_names():
    db["tasks"].create({
        "id": int,           # 自動採番
        "name": str,         # タスク名
        "priority": int,     # 優先度（1,2,3 など）
        "deadline": str,     # 締切日（YYYY-MM-DD）※空でもOK
        "created_at": str,   # 作成日
    }, pk="id")
    print("tasks テーブルを作成しました！")
else:
    print("tasks テーブルはすでに存在します。")
