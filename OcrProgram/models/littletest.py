import os
import numpy as np
import cv2
from tkinter import Tk, filedialog, simpledialog
from werkzeug.utils import secure_filename
from pdf2image import convert_from_path

from OcrProgram.models import result
from OcrProgram.views import console

DEFAULT_LITTLE_TEST = "DEFAULT"
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "../LittleTestPdf")
ALLOWED_EXTENSIONS = {"pdf"}


class LittleTest(object):

    def __init__(self, name=DEFAULT_LITTLE_TEST):
        self.name = name
        self.selected_pdf_path = None

    # PDFファイルの確認
    def allowed_file(self, filename):
        return "." in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
        if self.allowed_file(filename):
            destination_path = os.path.join(UPLOAD_FOLDER, filename)
            os.rename(file_path, destination_path)
            return f"File uploaded successfully: {destination_path}"
        else:
            return "Invalid file type. Only PDFs are allowed."

    # PDFファイルの選択
    def get_pdf_paths(self):
        files = os.listdir(UPLOAD_FOLDER)
        pdf_files = [os.path.join(UPLOAD_FOLDER, f) for f in files if f.lower().endswith('.pdf')]
        return pdf_files

    def select_pdf(self):
        pdf_paths = self.get_pdf_paths()

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

    def read(self):
        # popplerの設定
        poppler_path = r"C:\Users\桑田倫成\PycharmProjects\OCR_LittleTest\OcrProgram\models\poppler\Library\bin"

        if self.selected_pdf_path is None:
            return "No PDF file selected."

        # PDFの各ページを画像に変換
        images = convert_from_path(self.selected_pdf_path, poppler_path=poppler_path)

        # 画像の総枚数をターミナルに出力
        total_pages = len(images)
        print(f"Total pages: {total_pages}")

        # 各ページの画像を表示（最大3枚まで）
        for i, image in enumerate(images[:3]):
            # PIL.ImageからNumPy配列に変換
            image_np = np.array(image)

            # 画像のサイズをターミナルに出力
            height, width, _ = image_np.shape
            print(f"Page {i + 1}: {width}x{height}")

            # RGBからBGRに変換 (OpenCVはBGR形式を使用するため)
            image_bgr = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)

            # 画像を表示
            cv2.imshow(f'Page {i + 1}', image_bgr)
            cv2.waitKey(0)  # キーが押されるまで待機

        # すべてのウィンドウを閉じる
        cv2.destroyAllWindows()




