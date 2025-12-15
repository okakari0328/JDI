import flet as ft
from sqlite_utils import Database
from datetime import datetime
import calendar
from datetime import date



def main(page: ft.Page):
    # DB 接続
    db = Database("tasks.db")


    page.title = "Study Task Manager"
    page.window_width = 500
    page.window_height = 700

    # --- 入力欄 ---
    task_name = ft.TextField(label="タスク名", width=300)
    priority = ft.Dropdown(
        label="優先度",
        width=150,
        options=[
            ft.dropdown.Option("1"),
            ft.dropdown.Option("2"),
            ft.dropdown.Option("3")
        ]
    )
    deadline = ft.TextField(label="期限 (YYYY-MM-DD)・任意", width=200)

    task_list_column = ft.Column()

    def load_tasks():
        task_list_column.controls.clear()

        for task in db["tasks"].rows:
            # タスク表示テキスト
            text = ft.Text(
                f"{task['name']} / 優先度: {task['priority']} / 期限: {task['deadline'] or 'なし'}",
                size=16
            )

            # 削除ボタン
            delete_button = ft.IconButton(
                icon=ft.Icons.DELETE,
                icon_color="red",
                data=task["id"],  # このタスクのID
                on_click=delete_task
            )

            # 1行にまとめる
            row = ft.Row(
                [text, delete_button],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            )

            task_list_column.controls.append(row)

        page.update()


    # --- タスク追加処理 ---
    def add_task(e):
        name = task_name.value.strip()
        prio = priority.value
        dline = deadline.value.strip()

        if name == "":
            page.snack_bar = ft.SnackBar(ft.Text("タスク名は必須です"))
            page.snack_bar.open = True
            page.update()
            return

        # 空欄なら deadline="" のまま保存
        db["tasks"].insert({
            "name": name,
            "priority": int(prio) if prio else None,
            "deadline": dline if dline else "",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
        })

        # 入力欄をリセット
        task_name.value = ""
        priority.value = None
        deadline.value = ""
        page.update()
        
        load_tasks()
        calendar_container.content = build_calendar(today.year, today.month)
        page.update()

    add_button = ft.ElevatedButton(text="追加", width=120, on_click=add_task)

    def delete_task(e):
        task_id = e.control.data  # 押されたボタンに入れておいたタスクID

        db["tasks"].delete(task_id)

        load_tasks()  # 再読み込み
        calendar_container.content = build_calendar(today.year, today.month)
        page.update()
    

    # --- タスクリスト表示領域 ---
    task_list_container = ft.Container(
        content=task_list_column,
        padding=10,
        bgcolor="#f0f0f0",
        border_radius=10,
        height=400,
        width=450,
    )

    def build_calendar(year, month):
        # DB から期限のあるタスクだけ抽出
        deadline_tasks = {
            task["deadline"]: task["name"]
            for task in db["tasks"].rows
            if task["deadline"] not in ("", None)
        }

        cal = calendar.Calendar(firstweekday=6)  # 日曜始まり
        month_weeks = cal.monthdatescalendar(year, month)

        # カラム名（曜日）
        table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Sun")),
                ft.DataColumn(ft.Text("Mon")),
                ft.DataColumn(ft.Text("Tue")),
                ft.DataColumn(ft.Text("Wed")),
                ft.DataColumn(ft.Text("Thu")),
                ft.DataColumn(ft.Text("Fri")),
                ft.DataColumn(ft.Text("Sat")),
            ],
            rows=[]
        )

        # 各週を DataRow として追加
        for week in month_weeks:
            row_cells = []
            for day in week:
                date_str = day.strftime("%Y-%m-%d")
                is_this_month = (day.month == month)
                has_task = (date_str in deadline_tasks)

                # 表示テキスト
                text_color = "black" if is_this_month else "gray"
                mark = " ●" if has_task else ""   # 期限の印
                text = ft.Text(f"{day.day}{mark}", color=text_color)

                row_cells.append(ft.DataCell(text))

            table.rows.append(ft.DataRow(row_cells))

        return table
    # カレンダー表示
    calendar_container = ft.Container()

    # --- レイアウト ---
    page.add(
        ft.Row(
            [
                # ===== 左側：タスク関連 =====
                ft.Column(
                    [
                        ft.Text("タスクリスト", size=25, weight="bold"),
                        ft.Row([task_name]),
                        ft.Row([priority, deadline]),
                        ft.Row([add_button]),
                        ft.Text("登録済みタスク：", size=18),
                        task_list_container,
                    ],
                    expand=True,
                    scroll="auto",
                ),

                # 区切り線
                ft.VerticalDivider(width=1),

                # ===== 右側：カレンダー =====
                ft.Column(
                    [
                        ft.Text("カレンダー", size=22, weight="bold"),
                        calendar_container,
                    ],
                    width=550,     # ← カレンダー側の幅（調整可）
                    alignment=ft.MainAxisAlignment.START,
                ),
            ],
            expand=True,
        )
    )

    # 起動時にタスクを読み込む
    load_tasks()
    # 初期表示：今月を描画
    today = date.today()
    calendar_container.content = build_calendar(today.year, today.month)
    page.update()



ft.app(target=main)
