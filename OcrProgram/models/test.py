from PIL import Image
import numpy as np
import os
import cv2

# ダミーの二値化画像データを作成
dummy_image = np.zeros((100, 100), dtype=np.uint8)  # 100x100の黒画像
cv2.circle(dummy_image, (50, 50), 25, (255, 255, 255), -1)  # 白い円を描画

# NumPy配列をPIL Imageに変換
image_pil = Image.fromarray(dummy_image)

# 保存先フォルダ
save_folder = r"C:\Users\桑田倫成\PycharmProjects\OCR_LittleTest\OcrProgram\BinarizedLittleTestImage"
os.makedirs(save_folder, exist_ok=True)

# 保存ファイルパス
save_path = os.path.join(save_folder, "test_image_pil.png")

# 画像を保存
image_pil.save(save_path)
print(f"Image successfully saved to {save_path}")
