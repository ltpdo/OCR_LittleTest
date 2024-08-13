from OcrProgram.models import littletest

def processing_order_little_test():
    da2 = littletest.LittleTest()
    # 小テストのアップロード
    #da2.upload()
    # PDFファイルの選択
    da2.select_pdf()
    # PDFファイルの読み込みと変換
    da2.read_and_convert()

    da2 = littletest.PreprocessingLittleTest()
    # PDFファイルを2値化処理
    da2.convert_binarized_image()