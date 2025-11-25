import sqlite3
import sys, os

from PyQt6.QtWidgets import QApplication, QMainWindow, QHeaderView, QTableWidgetItem
from main_ui import Ui_MainWindow
from addEditCoffeeForm_ui import Ui_addEditForm


def resource_path(rel_path):
    if getattr(sys, "frozen", False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, rel_path)


class Cappuccino(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        db_file = resource_path("data/coffee.sqlite")
        self.con = sqlite3.connect(db_file)
        self.cur = self.con.cursor()
        self.initUI()

    def initUI(self):
        self.setupUi(self)
        self.setWindowTitle("Эспрессо")
        self.add_pushButton.clicked.connect(self.add_coffee)
        self.change_pushButton.clicked.connect(self.edit_coffee)
        header = self.coffee_tableWidget.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_compilation()

    def table_compilation(self):
        self.result = self.cur.execute(
            "SELECT id, sort_name, roasting_degree, type, taste, price, size FROM Coffee"
        ).fetchall()
        self.coffee_tableWidget.setRowCount(len(self.result))
        for i, film in enumerate(self.result):
            for j, information in enumerate(film):
                self.coffee_tableWidget.setItem(
                    i, j, QTableWidgetItem(str(information))
                )

    def add_coffee(self):
        self.add_film_widget = AddFilmWidget(self, self.con, "add")
        self.add_film_widget.show()
        self.update_result()

    def edit_coffee(self):
        selected_rows = self.coffee_tableWidget.selectedItems()
        if not selected_rows:
            self.statusbar.showMessage("Выберите строку для редактирования")
            return
        row = selected_rows[0].row()
        selected_id = int(self.coffee_tableWidget.item(row, 0).text())
        self.edit_film_widget = AddFilmWidget(self, self.con, "edit", selected_id)
        self.edit_film_widget.show()
        self.update_result()

    def update_result(self):
        self.con.commit()
        self.table_compilation()


class AddFilmWidget(QMainWindow, Ui_addEditForm):
    def __init__(self, parent=None, con=None, action=None, selected_id=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("Добавить/изменить элемент")
        self.con = con
        self.cur = self.con.cursor()
        self.action = action
        self.edit_row_number = None
        self.selected_id = selected_id
        self.pushButton.clicked.connect(self.change_table)

    def add_film_to_table(self):
        try:
            self.cur.execute(
                "INSERT INTO Coffee (sort_name, roasting_degree, type, taste, price, size) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    self.sort_lineEdit.text(),
                    self.roasting_degree_lineEdit.text(),
                    self.type_lineEdit.text(),
                    self.taste_lineEdit.text(),
                    self.price_lineEdit.text(),
                    self.size_lineEdit.text(),
                ),
            )
            self.con.commit()
            self.parent().update_result()
            self.close()
        except Exception:
            self.statusbar.showMessage("Неверно заполена форма")
            return

    def edit_film_in_table(self):
        try:
            self.cur.execute(
                f"""UPDATE Coffee
                            SET sort_name = ?, roasting_degree = ?, type = ?, taste = ?, price = ?, size = ?
                            WHERE id = {self.selected_id}""",
                (
                    self.sort_lineEdit.text(),
                    self.roasting_degree_lineEdit.text(),
                    self.type_lineEdit.text(),
                    self.taste_lineEdit.text(),
                    self.price_lineEdit.text(),
                    self.size_lineEdit.text(),
                ),
            )
            self.con.commit()
            self.parent().update_result()
            self.close()
        except Exception:
            self.statusbar.showMessage("Неверно заполена форма")
            return

    def change_table(self):
        if self.action == "add":
            self.add_film_to_table()
        elif self.action == "edit":
            self.edit_film_in_table()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = Cappuccino()
    ex.show()
    sys.exit(app.exec())