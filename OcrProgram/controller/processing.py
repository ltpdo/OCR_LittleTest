from OcrProgram.models import littletest

def processing_order_little_test():
    da2 = littletest.LittleTest()
    # 小テストのアップロード
    #da2.upload()
    # PDFファイルの選択
    da2.select_pdf()
    # PDFファイルの読み込み
    da2.read()