# 画像関係
import cv2
import numpy as np
# システム関係
import os
import sys
# 画面情報
from screeninfo import get_monitors
# json
import json
# GUI関係
import pyautogui

def main():
    # コマンドライン引数
    args = sys.argv
    # 入力ファイル名
    input_fname = args[0]
    if not os.path.exists(input_fname):
        print("ファイルが存在しません")
        return
    # 出力名
    output_fname = input_fname.split(".")[0]+".json"

    # 変形設定
    setting_transform(input_fname)

def setting_transform(input_fname):
    # 映像開く
    video = cv2.VideoCapture(input_fname)

    # 映像情報
    video_width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    video_height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # モニター情報
    monitor_width = get_monitors()[0].width
    monitor_height = get_monitors()[0].height

    # 座標関係
    # 元の大きさでそのまま
    original_up_left = [0, 0]
    original_up_right = [video_width, 0]
    original_under_left = [0, video_height]
    original_under_right = [video_width, video_height]
    # np化
    original_pos = np.float32([
        original_up_left, original_up_right, original_under_left, original_under_right,
    ])
    # 変換後の座標
    update_up_left = [0, 0]
    update_up_right = [video_width, 0]
    update_under_left = [0, video_height]
    update_under_right = [video_width, video_height]
    # np化
    update_pos = np.float32([
        update_up_left, update_up_right, update_under_left, update_under_right,
    ])
    
    # opencv表示
    winname = "transform"
    cv2.namedWindow(winname, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(winname, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    # 一枚ずつ表示
    while True:
        # キー入力
        key = cv2.waitKey(1)&0xff
        # 画像🐤
        ret, img = video.read()
        # 読み込みできんかったら映像の最初に移動
        if not ret:
            video.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        # キー入力結果
        if key == 13:
            # エンターキーで終了
            break
        print(key, ret, img)
        
        # 表示
        show_img_fullscreen(img)
    
    # 閉じ
    video.release()
        
# 全画面表示用
def show_img_fullscreen(winname, img):
    cv2.namedWindow(winname, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(winname, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.imshow(winname, img)

if __name__ == "__main__":
    main()