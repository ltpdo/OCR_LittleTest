import os
import numpy as np
import cv2
import matplotlib.pyplot as plt
import pyautogui
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import Tk, filedialog, simpledialog
from werkzeug.utils import secure_filename
from pdf2image import convert_from_path

from OcrProgram.models import result
from OcrProgram.views import console

DEFAULT_LITTLE_TEST = "DEFAULT"
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "../LittleTestPdf")
ALLOWED_EXTENSIONS = {"pdf"}
RESIZE_RATIO = 2


# PDFファイルの確認
def allowed_file(filename):
    return "." in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# PDFファイルの選択
def get_pdf_paths():
    files = os.listdir(UPLOAD_FOLDER)
    pdf_files = [os.path.join(UPLOAD_FOLDER, f) for f in files if f.lower().endswith('.pdf')]
    return pdf_files


class LittleTest(object):

    def __init__(self, name=DEFAULT_LITTLE_TEST):
        self.name = name
        self.selected_pdf_path = None

    # PDFのアップロード
    def upload(self):
        root = Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(
            title="PDFファイルを選んでください。",
            filetypes=[("PDF files", "*.pdf")]
        )
        if not file_path:
            return 'ファイルが選ばれていません。'
        filename = secure_filename(os.path.basename(file_path))
        if allowed_file(filename):
            destination_path = os.path.join(UPLOAD_FOLDER, filename)
            os.rename(file_path, destination_path)
            return f"ファイルのアップロードが成功しました。: {destination_path}"
        else:
            return "PDFファイルではありません。"

    # PDFファイルの選択
    def select_pdf(self):
        pdf_paths = get_pdf_paths()

        if not pdf_paths:
            return "PDFファイルが見つかりません。"

        # Tkinterを非表示モードで初期化
        root = Tk()
        root.withdraw()

        # 選択肢としてPDFファイルのパスを列挙
        pdf_paths_str = "\n".join([f"{i + 1}: {os.path.basename(path)}" for i, path in enumerate(pdf_paths)])
        selection = simpledialog.askstring("PDFファイルを選んでください。",
                                           f"PDFファイルを選んでください。:\n\n{pdf_paths_str}\n\n数字を入力してください。:")

        # ユーザーが番号を入力した場合
        if selection and selection.isdigit():
            index = int(selection) - 1
            if 0 <= index < len(pdf_paths):
                self.selected_pdf_path = pdf_paths[index]  # 選択されたPDFファイルのパスを格納
                return f"Selected PDF path: {self.selected_pdf_path}"
            else:
                return "Invalid selection."
        else:
            return "No selection made or invalid input."

    # PDFファイルを画像に変換
    def read_and_convert(self):
        # popplerの設定
        poppler_path = r"C:\Users\桑田倫成\PycharmProjects\OCR_LittleTest\OcrProgram\models\poppler\Library\bin"

        if self.selected_pdf_path is None:
            return "No PDF file selected."

        # PDFの各ページを画像に変換
        images = convert_from_path(self.selected_pdf_path, poppler_path=poppler_path)

        # 画像の総枚数をターミナルに出力
        total_pages = len(images)
        print(f"合計枚数: {total_pages}")

        # 画像のサイズを保持するための変数
        previous_size = None
        size_is_consistent = True

        image_bgr_list = []

        # 各ページの画像を処理
        for i, image in enumerate(images):
            # PIL.ImageからNumPy配列に変換
            image_np = np.array(image)

            # 画像のサイズを取得
            height, width, _ = image_np.shape

            if previous_size is None:
                previous_size = (width, height)
            elif (width, height) != previous_size:
                size_is_consistent = False

            # サイズの一貫性を確認するための出力
            if i == 0 or not size_is_consistent:
                print(f"Page {i + 1}: {width}x{height}")
                previous_size = (width, height)

            # RGBからBGRに変換 (OpenCVはBGR形式を使用するため)
            image_bgr = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
            image_bgr_list.append(image_bgr)

        self.display_images(image_bgr_list)

        return image_bgr_list

    # 画像を表示するメソッド
    def display_images(self, images, max_pages=3):
        for i, image_bgr in enumerate(images[:max_pages]):  # 最初のmax_pagesページを表示
            plt.figure()
            plt.imshow(cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB))
            plt.title(f"Page {i + 1}")
            plt.axis('off')  # 軸を表示しない
            plt.show()


class PreprocessingLittleTest(LittleTest):

    def __init__(self, name=DEFAULT_LITTLE_TEST, selected_pdf_path=None):
        super().__init__(name)
        if selected_pdf_path:
            self.selected_pdf_path = selected_pdf_path
        else:
            result = self.select_pdf()
            if "Selected PDF path" in result:
                self.selected_pdf_path = self.selected_pdf_path
            else:
                raise ValueError("PDFファイルが選択されていません。")

        self.annotator = None  # ImageAnnotator インスタンスを保持する変数

    def convert_binarized_image(self):
        image_binarized_list = []
        save_folder = r"C:\Users\桑田倫成\PycharmProjects\OCR_LittleTest\OcrProgram\BinarizedLittleTestImage"
        os.makedirs(save_folder, exist_ok=True)
        image_bgr_list = self.read_and_convert()

        for i, image_bgr in enumerate(image_bgr_list):
            if image_bgr is None or image_bgr.size == 0:
                print(f"Image {i + 1} is empty or invalid.")
                continue

            lower_red1 = np.array([0, 50, 50])
            upper_red1 = np.array([70, 255, 255])
            lower_red2 = np.array([170, 50, 50])
            upper_red2 = np.array([180, 255, 255])

            image_hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)
            mask1 = cv2.inRange(image_hsv, lower_red1, upper_red1)
            mask2 = cv2.inRange(image_hsv, lower_red2, upper_red2)
            mask = cv2.bitwise_or(mask1, mask2)
            image_bgr[mask == 255] = [255, 255, 255]
            image_gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
            retval, image_binary = cv2.threshold(image_gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            image_binarized_list.append(image_binary)

            image_pil = Image.fromarray(image_binary)
            save_path = os.path.join(save_folder, f"binarized_image_{i + 1}.png")
            try:
                image_pil.save(save_path)
                print(f"Image {i + 1} saved to {save_path}")
            except Exception as e:
                print(f"Failed to save Image {i + 1}. Error: {e}")

        if image_binarized_list:
            self.display_images(image_binarized_list)

    def select_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png;*.jpg;*.jpeg")],
            title="Select an Image file"
        )
        if not file_path:
            raise ValueError("画像ファイルが選択されていません。")
        return file_path

    def annotate_image(self):
        file_path = self.select_file()
        self.annotator = self.ImageAnnotator(file_path)
        self.annotator.annotate_image()

    def display_rectangles(self):
        if self.annotator and self.annotator.rectangles:
            print("Rectangle coordinates:")
            for i, (start_x, start_y, end_x, end_y) in enumerate(self.annotator.rectangles):
                print(f"Rectangle {i + 1}: start_x={start_x}, start_y={start_y}, end_x={end_x}, end_y={end_y}")
        else:
            print("No rectangles found.")

    def display_remove(self):
        self.display_rectangles()

        # ここで削除機能を呼び出す例
        try:
            index_to_remove = int(input("Enter the rectangle number to remove (or 0 to skip): ")) - 1
            if index_to_remove >= 0:
                self.remove_rectangle(index_to_remove)
        except ValueError:
            print("Invalid input. Please enter a number.")

        self.display_rectangles()

    def remove_rectangle(self, index):
        if self.annotator and 0 <= index < len(self.annotator.rectangles):
            removed = self.annotator.rectangles.pop(index)
            print(f"Removed rectangle: {removed}")
        else:
            print("Invalid rectangle number.")

    class ImageAnnotator:
        def __init__(self, file_path):
            self.file_path = file_path
            self.start_x = None
            self.start_y = None
            self.rectangles = []
            self.img_tk = None  # インスタンス変数としてimg_tkを定義

        def start_point_get(self, event, canvas):
            self.start_x, self.start_y = event.x, event.y
            canvas.delete("rect1")

        def rect_drawing(self, event, canvas):
            if self.start_x is None or self.start_y is None:
                return

            end_x = min(canvas.winfo_width(), event.x)
            end_y = min(canvas.winfo_height(), event.y)

            canvas.delete("rect1")
            canvas.create_rectangle(self.start_x, self.start_y, end_x, end_y, outline="red", tag="rect1")

        def release_action(self, event, canvas):
            if self.start_x is None or self.start_y is None:
                return

            start_x_val, start_y_val, end_x_val, end_y_val = [round(n * RESIZE_RATIO) for n in canvas.coords("rect1")]
            self.rectangles.append((start_x_val, start_y_val, end_x_val, end_y_val))

            self.start_x = self.start_y = None
            print(f"start_x: {start_x_val}, start_y: {start_y_val}, end_x: {end_x_val}, end_y: {end_y_val}")

        def annotate_image(self):
            root = tk.Tk()
            root.protocol("WM_DELETE_WINDOW", lambda: self.quit_me(root))
            root.attributes("-topmost", True)

            img = Image.open(self.file_path)
            img_resized = img.resize(
                (int(img.width / RESIZE_RATIO), int(img.height / RESIZE_RATIO)),
                Image.BILINEAR
            )

            self.img_tk = ImageTk.PhotoImage(img_resized, master=root)
            canvas = tk.Canvas(root, bg="black", width=img_resized.width, height=img_resized.height)
            canvas.create_image(0, 0, image=self.img_tk, anchor=tk.NW)
            canvas.pack()

            canvas.bind("<ButtonPress-1>", lambda event: self.start_point_get(event, canvas))
            canvas.bind("<B1-Motion>", lambda event: self.rect_drawing(event, canvas))
            canvas.bind("<ButtonRelease-1>", lambda event: self.release_action(event, canvas))

            root.mainloop()

        def quit_me(self, root_window):
            root_window.quit()
            root_window.destroy()