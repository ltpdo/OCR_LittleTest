import tkinter as tk
from PIL import Image, ImageTk
import pyautogui

RESIZE_RATIO = 2  # 縮小倍率の規定

class ImageAnnotator:
    def __init__(self, root, file_path):
        self.root = root
        self.file_path = file_path
        self.start_x = None
        self.start_y = None
        self.rectangles = []  # 座標を保存するリスト

        # 指定された画像ファイルを読み込み、リサイズ
        self.img = Image.open(self.file_path)
        self.img_resized = self.img.resize(
            (int(self.img.width / RESIZE_RATIO), int(self.img.height / RESIZE_RATIO)),
            Image.BILINEAR
        )

        # Tkinterで表示できるように画像を変換
        self.img_tk = ImageTk.PhotoImage(self.img_resized)

        # Canvasウィジェットの設定
        self.canvas = tk.Canvas(root, bg="black", width=self.img_resized.width, height=self.img_resized.height)
        self.canvas.create_image(0, 0, image=self.img_tk, anchor=tk.NW)
        self.canvas.pack()

        # イベントバインディング
        self.canvas.bind("<ButtonPress-1>", self.start_point_get)
        self.canvas.bind("<B1-Motion>", self.rect_drawing)
        self.canvas.bind("<ButtonRelease-1>", self.release_action)

    def start_point_get(self, event):
        # スタートポイントを設定
        self.start_x, self.start_y = event.x, event.y
        # 古い矩形を削除
        self.canvas.delete("rect1")

    def rect_drawing(self, event):
        if self.start_x is None or self.start_y is None:
            return

        end_x = min(self.img_resized.width, event.x)
        end_y = min(self.img_resized.height, event.y)

        # 古い矩形を削除（ドラッグ中に一時的に表示する）
        self.canvas.delete("rect1")

        # 新しい矩形を描画
        self.canvas.create_rectangle(self.start_x, self.start_y, end_x, end_y, outline="red", tag="rect1")

    def release_action(self, event):
        if self.start_x is None or self.start_y is None:
            return

        # 最終的な座標を取得し、リストに追加
        start_x, start_y, end_x, end_y = [round(n * RESIZE_RATIO) for n in self.canvas.coords("rect1")]
        self.rectangles.append((start_x, start_y, end_x, end_y))

        # スタートポイントをリセット
        self.start_x = self.start_y = None

        # 座標を表示
        print(f"start_x: {start_x}, start_y: {start_y}, end_x: {end_x}, end_y: {end_y}")

