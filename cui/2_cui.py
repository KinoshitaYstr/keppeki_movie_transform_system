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
# ばー
from tqdm import tqdm

def main():
    # コマンドライン引数
    args = sys.argv
    # 入力ファイル名
    input_fname = args[1]
    if not os.path.exists(input_fname):
        print("ファイルが存在しません")
        return
    # json読み込み
    f = open(input_fname, "r")
    datas = json.load(f)
    print(datas)
    # 出力ファイル名
    output_fname = args[2]
    if os.path.exists(output_fname):
        print("出力ファイル名が違反")
        return
    
    # 変換
    create_transform_video(datas, output_fname)

def create_transform_video(datas, output_fname):
    print("create_transform_video")
    # 入力ファイル名撮る
    input_fname = datas["fname"]
    
    # 座標設定
    # 元の情報
    original_pos = np.float32([
        [0, 0],
        [datas["video_width"], 0],
        [0, datas["video_height"]],
        [datas["video_width"], datas["video_height"]]
    ])
    # 変換後の座標
    update_pos = np.float32([
        datas["update_up_left"], datas["update_up_right"], datas["update_under_left"], datas["update_under_right"]
    ])
    # 変換表列
    matrix = cv2.getPerspectiveTransform(original_pos, update_pos)
    
    # 背景情報
    monitor_width = datas["monitor_width"]
    monitor_height = datas["monitor_height"]

    # 映像関係
    # 映像開く
    video = cv2.VideoCapture(input_fname)
    # 新規作成
    fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
    fps = int(video.get(cv2.CAP_PROP_FPS))
    update_video = cv2.VideoWriter(output_fname, fourcc, fps, (monitor_width, monitor_height))

    # 映像の枚数
    n_frame = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

    for i in tqdm(range(n_frame)):
        # 読み取り
        ret, img = video.read()
        if not ret:
            break

        # 変形
        update_img = cv2.warpPerspective(img, matrix, (monitor_width, monitor_height))

        # 書き込み
        update_video.write(update_img)

    # 解放
    video.release()
    update_video.release()

if __name__ == "__main__":
    main()