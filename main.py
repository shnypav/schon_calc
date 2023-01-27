import sys
from operator import add, sub, mul, truediv

from PySide6.QtGui import QFontDatabase
from PySide6.QtWidgets import QApplication, QMainWindow

from calc_design import Ui_MainWindow

operations = {
    "+": add,
    "−": sub,
    "×": mul,
    "/": truediv
}

error_zero_div = "Division by zero"
error_undefined = "Result undefined"

default_font_size = 16
default_entry_font_size = 40


class Calculator(QMainWindow):
    def __init__(self) -> None:
        super(Calculator, self).__init__()

        QFontDatabase.addApplicationFont("fonts/Rubik-Regular.ttf")

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.entry = self.ui.entry_field
        self.temp = self.ui.lbl_temp

        self.entry_max_len = self.entry.maxLength()

        # digits
        self.ui.btn_0.clicked.connect(self.add_digit)
        self.ui.btn_1.clicked.connect(self.add_digit)
        self.ui.btn_2.clicked.connect(self.add_digit)
        self.ui.btn_3.clicked.connect(self.add_digit)
        self.ui.btn_4.clicked.connect(self.add_digit)
        self.ui.btn_5.clicked.connect(self.add_digit)
        self.ui.btn_6.clicked.connect(self.add_digit)
        self.ui.btn_7.clicked.connect(self.add_digit)
        self.ui.btn_8.clicked.connect(self.add_digit)
        self.ui.btn_9.clicked.connect(self.add_digit)

        # actions
        self.ui.btn_c.clicked.connect(self.clear_all)
        self.ui.btn_ce.clicked.connect(self.clear_entry)
        self.ui.btn_point.clicked.connect(self.add_point)
        self.ui.btn_neg.clicked.connect(self.add_neg)
        self.ui.btn_backspace.clicked.connect(self.backspace)

        # math
        self.ui.btn_result.clicked.connect(self.calc)
        self.ui.btn_add.clicked.connect(self.math_operation)
        self.ui.btn_minus.clicked.connect(self.math_operation)
        self.ui.btn_mult.clicked.connect(self.math_operation)
        self.ui.btn_div.clicked.connect(self.math_operation)

    @staticmethod
    def remove_zeros(num: str) -> str:
        n = str(float(num))
        return n[:-2] if n[-2:] == ".0" else n

    def add_digit(self) -> None:
        self.clear_error()
        self.replace_prev()
        self.clear_temp()
        btn = self.sender()

        digit_buttons = ("btn_0", "btn_1", "btn_2", "btn_3", "btn_4",
                         "btn_5", "btn_6", "btn_7", "btn_8", "btn_9")

        if btn.objectName() in digit_buttons:
            if self.entry.text() == "0":
                self.entry.setText(btn.text())
            else:
                self.entry.setText(self.entry.text() + btn.text())

        self.adjust_entry_font_size()

    def add_neg(self) -> None:
        self.clear_temp()
        self.replace_prev()

        entry = self.entry.text()

        if "-" not in entry:
            if entry != "0":
                entry = "-" + entry
        else:
            entry = entry[1:]

        if len(entry) == self.entry_max_len + 1 and "-" in entry:
            self.entry.setMaxLength(self.entry_max_len + 1)
        else:
            self.entry.setMaxLength(self.entry_max_len)

        self.entry.setText(entry)
        self.adjust_entry_font_size()

    def add_point(self) -> None:
        self.clear_temp()

        if "." not in self.entry.text():
            self.entry.setText(self.entry.text() + ".")
            self.adjust_entry_font_size()

    def add_temp(self) -> None:
        btn = self.sender()
        entry = self.remove_zeros(self.entry.text())

        if not self.temp.text() or self.get_sign_from_temp() == "=":
            self.temp.setText(entry + f" {btn.text()} ")
            self.adjust_temp_font_size()
            self.entry.setText("0")

    def clear_all(self) -> None:
        self.clear_error()
        self.entry.setText("0")
        self.temp.clear()

    def clear_entry(self) -> None:
        self.clear_error()
        self.clear_temp()
        self.entry.setText("0")

    def replace_prev(self) -> None:
        if self.get_sign_from_temp() == "=":
            self.entry.clear()

    def backspace(self) -> None:
        self.clear_error()
        self.clear_temp()

        entry = self.entry.text()

        match len(entry):
            case 1:
                self.entry.setText("0")
            case 2 if "-" in entry:
                self.entry.setText("0")
            case _:
                self.entry.setText(entry[:-1])

        self.adjust_entry_font_size()

    def get_entry_num(self) -> int | float:
        entry = self.entry.text().strip(".")
        return float(entry) if "." in entry else int(entry)

    def get_temp_num(self) -> int | float | None:
        if self.temp.text():
            temp = self.temp.text().strip(".").split()[0]
            return float(temp) if "." in temp else int(temp)

    def get_sign_from_temp(self) -> str | None:
        if self.temp.text():
            return self.temp.text().strip(".").split()[-1]

    def clear_temp(self) -> None:
        if self.get_sign_from_temp() == "=":
            self.temp.clear()

    def calc(self) -> str | None:
        entry = self.entry.text()
        temp = self.temp.text()

        if temp:
            try:
                result = self.remove_zeros(
                    str(operations[self.get_sign_from_temp()](self.get_temp_num(), self.get_entry_num()))
                )
                self.temp.setText(temp + self.remove_zeros(entry) + " =")
                self.adjust_temp_font_size()
                self.entry.setText(result)
                self.adjust_entry_font_size()
                return result

            except KeyError as ke:
                print(ke)
                pass

            except ZeroDivisionError:
                if self.get_temp_num() == 0:
                    self.show_error(error_undefined)
                else:
                    self.show_error(error_zero_div)

    def math_operation(self) -> None:
        temp = self.temp.text()
        btn = self.sender()

        if not temp:
            self.add_temp()
        else:
            if self.get_sign_from_temp() != btn.text():
                if self.get_sign_from_temp() == "34=":
                    self.add_temp()
                else:
                    self.temp.setText(temp[:-2] + f"{btn.text()} ")
            else:
                self.temp.setText(self.calc() + f" {btn.text()}")

        self.adjust_temp_font_size()

    def show_error(self, error: str) -> None:
        self.entry.setMaxLength(len(error))
        self.entry.setText(error)
        self.adjust_entry_font_size()

    def clear_error(self) -> None:
        if self.entry.text() in (error_undefined, error_zero_div):
            self.entry.setText("0")
            self.entry.setMaxLength(self.entry_max_len)
            self.adjust_entry_font_size()

    def get_entry_text_width(self) -> int:
        return self.entry.fontMetrics().boundingRect(self.entry.text()).width()

    def get_temp_text_width(self) -> int:
        return self.temp.fontMetrics().boundingRect(self.temp.text()).width()

    def adjust_entry_font_size(self) -> None:
        font_size = default_entry_font_size
        while self.get_entry_text_width() > self.entry.width() - 15:
            font_size -= 1
            self.entry.setStyleSheet(f"font-size: {font_size}pt; border: none;")

    def adjust_temp_font_size(self) -> None:
        font_size = default_font_size
        while self.get_temp_text_width() > self.temp.width():
            font_size -= 1
            self.temp.setStyleSheet(f"font-size: {font_size}pt; border: none;")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = Calculator()
    window.show()

    sys.exit(app.exec())
