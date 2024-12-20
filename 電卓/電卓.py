import flet as ft
import math

# 基本ボタン
class CalcButton(ft.ElevatedButton):
    def __init__(self, text, button_clicked, expand=1):
        super().__init__()
        self.text = text
        self.expand = expand
        self.on_click = button_clicked
        self.data = text

# 数字ボタン
class DigitButton(CalcButton):
    def __init__(self, text, button_clicked, expand=1):
        CalcButton.__init__(self, text, button_clicked, expand)
        self.bgcolor = ft.colors.WHITE24
        self.color = ft.colors.WHITE

# 演算ボタン
class ActionButton(CalcButton):
    def __init__(self, text, button_clicked):
        CalcButton.__init__(self, text, button_clicked)
        self.bgcolor = ft.colors.ORANGE
        self.color = ft.colors.WHITE

# その他の操作ボタン
class ExtraActionButton(CalcButton):
    def __init__(self, text, button_clicked):
        CalcButton.__init__(self, text, button_clicked)
        self.bgcolor = ft.colors.BLUE_GREY_100
        self.color = ft.colors.BLACK

# 科学計算ボタン
class ScientificActionButton(CalcButton):
    def __init__(self, text, button_clicked):
        CalcButton.__init__(self, text, button_clicked)
        self.bgcolor = ft.colors.GREEN
        self.color = ft.colors.WHITE

# 電卓アプリ
class CalculatorApp(ft.Container):
    def __init__(self):
        super().__init__()
        self.reset()
        self.is_scientific_mode = False  # 科学計算モードフラグ
        self.result = ft.Text(value="0", color=ft.colors.WHITE, size=20)
        self.width = 350
        self.bgcolor = ft.colors.BLACK
        self.border_radius = ft.border_radius.all(20)
        self.padding = 20
        self.content = ft.Column(
            controls=[
                ft.Row(controls=[self.result], alignment="end"),
                ft.Row(
                    controls=[
                        ExtraActionButton("AC", self.button_clicked),
                        ExtraActionButton("+/-", self.button_clicked),
                        ExtraActionButton("%", self.button_clicked),
                        ActionButton("/", self.button_clicked),
                    ]
                ),
                # 科学計算ボタンの追加
                ft.Row(
                    controls=[
                        ScientificActionButton("sin", self.button_clicked),
                        ScientificActionButton("cos", self.button_clicked),
                        ScientificActionButton("tan", self.button_clicked),
                        ScientificActionButton("sqrt", self.button_clicked),
                        ScientificActionButton("log", self.button_clicked),  # 新規ボタン
                    ]
                ),
                ft.Row(
                    controls=[
                        DigitButton("7", self.button_clicked),
                        DigitButton("8", self.button_clicked),
                        DigitButton("9", self.button_clicked),
                        ActionButton("*", self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        DigitButton("4", self.button_clicked),
                        DigitButton("5", self.button_clicked),
                        DigitButton("6", self.button_clicked),
                        ActionButton("-", self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        DigitButton("1", self.button_clicked),
                        DigitButton("2", self.button_clicked),
                        DigitButton("3", self.button_clicked),
                        ActionButton("+", self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        DigitButton("0", self.button_clicked, expand=2),
                        DigitButton(".", self.button_clicked),
                        ActionButton("=", self.button_clicked),
                    ]
                ),
                # モード切替ボタン
                ft.Row(
                    controls=[
                        ExtraActionButton("Sci", self.toggle_scientific_mode),
                    ]
                ),
            ]
        )

    def toggle_scientific_mode(self, e):
        # 科学計算モードのトグル
        self.is_scientific_mode = not self.is_scientific_mode
        self.result.value = "Sci Mode" if self.is_scientific_mode else "Standard Mode"
        self.update()

    def button_clicked(self, e):
        data = e.control.data
        print(f"Button clicked with data = {data}")
        try:
            if self.result.value == "Error" or data == "AC":
                self.result.value = "0"
                self.reset()
            elif data in ("1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "."):
                if self.result.value == "0" or self.new_operand:
                    self.result.value = data
                    self.new_operand = False
                else:
                    self.result.value += data
            elif data in ("+", "-", "*", "/"):
                self.result.value = self.calculate(
                    self.operand1, float(self.result.value), self.operator
                )
                self.operator = data
                self.operand1 = float(self.result.value)
                self.new_operand = True
            elif data == "=":
                self.result.value = self.calculate(
                    self.operand1, float(self.result.value), self.operator
                )
                self.reset()
            elif data == "%":
                self.result.value = float(self.result.value) / 100
                self.reset()
            elif data == "+/-":
                self.result.value = str(-float(self.result.value))
            elif self.is_scientific_mode:
                self.result.value = self.perform_scientific_calculation(data, float(self.result.value))
        except ValueError:
            self.result.value = "Error"
        self.update()

    def perform_scientific_calculation(self, data, num):
        # 科学計算の処理を分離
        try:
            if data == "sin":
                return math.sin(math.radians(num))
            elif data == "cos":
                return math.cos(math.radians(num))
            elif data == "tan":
                return math.tan(math.radians(num))
            elif data == "sqrt":
                return math.sqrt(num) if num >= 0 else "Error"
            elif data == "log":
                return math.log10(num) if num > 0 else "Error"
        except ValueError:
            return "Error"

    def calculate(self, operand1, operand2, operator):
        # 基本計算の処理
        if operator == "+":
            return operand1 + operand2
        elif operator == "-":
            return operand1 - operand2
        elif operator == "*":
            return operand1 * operand2
        elif operator == "/":
            return "Error" if operand2 == 0 else operand1 / operand2

    def reset(self):
        self.operator = "+"
        self.operand1 = 0
        self.new_operand = True

# メイン関数
def main(page: ft.Page):
    page.title = "Scientific Calculator"
    calc = CalculatorApp()
    page.add(calc)

ft.app(target=main)
