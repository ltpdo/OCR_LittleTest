import os
import numpy as np
import cv2
import matplotlib.pyplot as plt
from PIL import Image
from tkinter import Tk, filedialog, simpledialog
from werkzeug.utils import secure_filename
from pdf2image import convert_from_path

from OcrProgram.models import result
from OcrProgram.views import console

DEFAULT_LITTLE_TEST = "DEFAULT"
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "../LittleTestPdf")
ALLOWED_EXTENSIONS = {"pdf"}


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
            title="Select a PDF file",
            filetypes=[("PDF files", "*.pdf")]
        )
        if not file_path:
            return 'No file selected'
        filename = secure_filename(os.path.basename(file_path))
        if allowed_file(filename):
            destination_path = os.path.join(UPLOAD_FOLDER, filename)
            os.rename(file_path, destination_path)
            return f"File uploaded successfully: {destination_path}"
        else:
            return "Invalid file type. Only PDFs are allowed."

    # PDFファイルの選択
    def select_pdf(self):
        pdf_paths = get_pdf_paths()

        if not pdf_paths:
            return "No PDF files found in the folder."

        # Tkinterを非表示モードで初期化
        root = Tk()
        root.withdraw()

        # 選択肢としてPDFファイルのパスを列挙
        pdf_paths_str = "\n".join([f"{i + 1}: {os.path.basename(path)}" for i, path in enumerate(pdf_paths)])
        selection = simpledialog.askstring("Select a PDF", f"Choose a PDF file:\n\n{pdf_paths_str}\n\nEnter number:")

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
        print(f"Total pages: {total_pages}")

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

        # 画像の表示をpltで行う（最大3ページまで表示）
        for i, image_bgr in enumerate(image_bgr_list[:3]):  # 最初の3ページを表示
            plt.figure()
            plt.imshow(cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB))
            plt.title(f"Page {i + 1}")
            plt.axis('off')  # 軸を表示しない
            plt.show()

        # すべての画像が同じサイズの場合、統一サイズとして出力
        if size_is_consistent:
            print(f"All pages have the same size: {previous_size[0]}x{previous_size[1]}")

        return image_bgr_list


class PreprocessingLittleTest(LittleTest):

    def __init__(self, name=DEFAULT_LITTLE_TEST, selected_pdf_path=None):
        super().__init__(name)
        if selected_pdf_path:
            self.selected_pdf_path = selected_pdf_path
        else:
            # パスが指定されていない場合、親クラスのメソッドを使ってPDFファイルを選択
            result = self.select_pdf()
            if "Selected PDF path" in result:
                self.selected_pdf_path = self.selected_pdf_path
            else:
                raise ValueError("PDFファイルが選択されていません。")

    def convert_binarized_image(self):
        image_binarized_list = []

        # 保存先フォルダを作成（存在しない場合は新規作成）
        save_folder = r"C:\Users\桑田倫成\PycharmProjects\OCR_LittleTest\OcrProgram\BinarizedLittleTestImage"
        os.makedirs(save_folder, exist_ok=True)  # フォルダが存在しない場合は作成

        # 親クラスのread_and_convertメソッドを呼び出し
        image_bgr_list = self.read_and_convert()

        # 取得したimage_bgrを処理
        for i, image_bgr in enumerate(image_bgr_list):
            # 画像が空でないことを確認
            if image_bgr is None or image_bgr.size == 0:
                print(f"Image {i + 1} is empty or invalid.")
                continue

            # 1. 赤色の範囲を定義する (HSV色空間)
            lower_red1 = np.array([0, 50, 50])
            upper_red1 = np.array([70, 255, 255])
            lower_red2 = np.array([170, 50, 50])
            upper_red2 = np.array([180, 255, 255])

            # 画像をHSVに変換
            image_hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)

            # 3. 赤色のマスクを作成する
            mask1 = cv2.inRange(image_hsv, lower_red1, upper_red1)
            mask2 = cv2.inRange(image_hsv, lower_red2, upper_red2)
            mask = cv2.bitwise_or(mask1, mask2)

            # 4. 元画像とマスクを用いて赤色の部分を白色にする
            image_bgr[mask == 255] = [255, 255, 255]

            # 5. グレースケールの画像に変換する
            image_gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)

            # 6. 画像を二値化する
            retval, image_binary = cv2.threshold(image_gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            image_binarized_list.append(image_binary)

            # 二値化された画像をPILで保存
            image_pil = Image.fromarray(image_binary)
            save_path = os.path.join(save_folder, f"binarized_image_{i + 1}.png")
            try:
                image_pil.save(save_path)
                print(f"Image {i + 1} saved to {save_path}")
            except Exception as e:
                print(f"Failed to save Image {i + 1}. Error: {e}")

        # 最初の二値化画像を表示
        if image_binarized_list:
            plt.imshow(image_binarized_list[0], cmap='gray')
            plt.show()


