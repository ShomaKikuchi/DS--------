import sqlite3
import requests
import flet as ft
import time
# API URL 定義
REGION_API_URL = "http://www.jma.go.jp/bosai/common/const/area.json"
WEATHER_API_URL_TEMPLATE = "https://www.jma.go.jp/bosai/forecast/data/forecast/{region_code}.json"
# データベース初期化
def initialize_database():
    conn = sqlite3.connect("weather.db")
    cursor = conn.cursor()
    # 地域テーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS regions (
        region_code TEXT PRIMARY KEY,
        region_name TEXT NOT NULL
    )
    ''')
    # 天気テーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS weather (
        region_code TEXT,
        date TEXT,
        description TEXT,
        temp_min TEXT,
        temp_max TEXT,
        PRIMARY KEY (region_code, date),
        FOREIGN KEY (region_code) REFERENCES regions(region_code)
    )
    ''')
    conn.commit()
    conn.close()
# 地域データを取得してデータベースに保存
def fetch_and_save_regions():
    try:
        response = requests.get(REGION_API_URL)
        response.raise_for_status()
        region_data = response.json()["offices"]
        conn = sqlite3.connect("weather.db")
        cursor = conn.cursor()
        for code, region in region_data.items():
            cursor.execute(
                "REPLACE INTO regions (region_code, region_name) VALUES (?, ?)",
                (code, region["name"]),
            )
        conn.commit()
        conn.close()
    except requests.exceptions.RequestException as e:
        print(f"地域データの取得エラー: {e}")
# 天気データを取得してデータベースに保存
def fetch_and_save_weather(region_code):
    try:
        url = WEATHER_API_URL_TEMPLATE.format(region_code=region_code)
        response = requests.get(url)
        response.raise_for_status()
        weather_data = response.json()
        conn = sqlite3.connect("weather.db")
        cursor = conn.cursor()
        time_series = weather_data[0]["timeSeries"]
        areas = time_series[0]["areas"]
        temp_series = next((s for s in time_series if "temps" in s["areas"][0]), None)
        temps = temp_series["areas"][0]["temps"] if temp_series else []
        for idx, area in enumerate(areas):
            for date, description in zip(time_series[0]["timeDefines"], area["weathers"]):
                min_temp = temps[idx] if idx < len(temps) else "N/A"
                max_temp = temps[idx] if idx < len(temps) else "N/A"
                cursor.execute(
                    "REPLACE INTO weather (region_code, date, description, temp_min, temp_max) VALUES (?, ?, ?, ?, ?)",
                    (region_code, date[:10], description, min_temp, max_temp),
                )
        conn.commit()
        conn.close()
    except requests.exceptions.RequestException as e:
        print(f"天気データの取得エラー ({region_code}): {e}")
# データベースから天気データを取得
def get_weather_from_db(region_code):
    conn = sqlite3.connect("weather.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT date, description, temp_min, temp_max FROM weather WHERE region_code = ?", (region_code,)
    )
    rows = cursor.fetchall()
    conn.close()
    return rows
# Flet アプリケーション
def main(page: ft.Page):
    page.title = "天気予報アプリ"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 10
    # 天気カードを作成する関数
    def build_forecast_card(date, weather_description, temp_min, temp_max):
        return ft.Card(
            content=ft.Column(
                [
                    ft.Text(date, size=16, weight="bold", text_align="center"),
                    ft.Icon(name=ft.Icons.WB_SUNNY, size=40, color=ft.Colors.AMBER),
                    ft.Text(weather_description, text_align="center"),
                    ft.Text(f"{temp_min}°C / {temp_max}°C", weight="bold", text_align="center"),
                ],
                alignment="center",
                horizontal_alignment="center",
            ),
            elevation=4,
            width=150,
            height=200,
        )
    # 地域選択時に天気データを更新
    def update_forecast(e):
        selected_region_code = region_dropdown.value
        if not selected_region_code:
            print("地域コードが選択されていません。")
            return
        # データ取得と表示
        fetch_and_save_weather(selected_region_code)
        weather_rows = get_weather_from_db(selected_region_code)
        forecast_container.controls.clear()
        if not weather_rows:
            forecast_container.controls.append(
                ft.Text("データがありません", color=ft.Colors.RED, size=20)
            )
        else:
            for date, description, temp_min, temp_max in weather_rows:
                forecast_container.controls.append(
                    build_forecast_card(date, description, temp_min, temp_max)
                )
        page.update()
    # 地域データを取得してドロップダウンに追加
    fetch_and_save_regions()
    conn = sqlite3.connect("weather.db")
    cursor = conn.cursor()
    cursor.execute("SELECT region_code, region_name FROM regions")
    region_options = [
        ft.dropdown.Option(key=code, text=name) for code, name in cursor.fetchall()
    ]
    conn.close()
    # UI コンポーネント
    region_dropdown = ft.Dropdown(
        label="地域を選択",
        options=region_options,
        on_change=update_forecast,
        width=300,
    )
    forecast_container = ft.Row(wrap=True, spacing=10, alignment=ft.MainAxisAlignment.START)
    # ページ構成
    page.add(
        ft.AppBar(
            title=ft.Text("天気予報アプリ", size=20, color=ft.Colors.WHITE),
            bgcolor=ft.Colors.INDIGO,
        ),
        ft.Column(
            [region_dropdown, ft.Container(content=forecast_container, padding=10)],
            alignment="start",
            spacing=20,
            scroll="auto",
        ),
    )
# データベース初期化
initialize_database()
# Flet アプリケーションの実行
ft.app(target=main)