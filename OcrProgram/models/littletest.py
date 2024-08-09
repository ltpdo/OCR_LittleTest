import os
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
                selected_pdf = pdf_paths[index]
                return f"Selected PDF path: {selected_pdf}"
            else:
                return "Invalid selection."
        else:
            return "No selection made or invalid input."

    def read(self):
        # PDFの各ページを画像に変換
        #images = convert_from_path()
        pass



