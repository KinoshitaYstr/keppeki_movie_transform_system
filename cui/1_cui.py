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
    input_fname = args[1]
    if not os.path.exists(input_fname):
        print("ファイルが存在しません")
        return
    # 出力名
    # output_fname = input_fname.split(".")[0]+".json"
    output_fname = "new_"+input_fname

    # 変形設定
    datas = setting_transform(input_fname)
    print(datas)
    with open(input_fname.split(".")[0]+".json") as f:
        json.dump(datas, f, indent=2)

    # 変形して保存
    create_transform_video(input_fname, output_fname, datas)

def create_transform_video(input_fname, output_fname, datas):
    print("create_transform_video")
    # 辞書と入力ファイルがあってるか確認
    if input_fname != datas["fname"]:
        print("ふぁいるちゃうで")
        return
    
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

    while True:
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


def setting_transform(input_fname):
    print("setting_transform")
    # 映像開く
    video = cv2.VideoCapture(input_fname)
    # 開けた確認
    if not video.isOpened():
        print("video open error")
        return

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
    update_up_right = [monitor_width, 0]
    update_under_left = [0, monitor_height]
    update_under_right = [monitor_width, monitor_height]
    update_array = [update_up_left, update_up_right, update_under_left, update_under_right]
    
    # opencv表示
    winname = "transform"
    cv2.namedWindow(winname, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(winname, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    # 一枚ずつ表示
    while True:
        # 画像
        ret, img = video.read()
        # 読み込みできんかったら映像の最初に移動
        if not ret:
            video.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        # キー入力
        key = cv2.waitKey(1)&0xff
        # キー入力結果
        if key == 13:
            # エンターキーで終了
            break
        elif key == ord('1'):
            # 1なら左上の位置をマウスの位置に合わせる
            update_array[0] = pyautogui.position()
        elif key == ord('2'):
            # 2なら右上の位置をマウスの位置に合わせる
            update_array[1] = pyautogui.position()
        elif key == ord('3'):
            # 3なら左下の位置をマウスの位置に合わせる
            update_array[2] = pyautogui.position()
        elif key == ord('4'):
            # 4なら右下の位置をマウスの位置に合わせる
            update_array[3] = pyautogui.position()
        
        # 変形後の座標np化
        update_pos = np.float32(update_array)
        # 変換行列作成
        matrix = cv2.getPerspectiveTransform(
            original_pos, update_pos
        )
        # 変換
        update_img = cv2.warpPerspective(
            img, matrix, (monitor_width, monitor_height)
        )
        
        # 表示
        show_img_fullscreen(winname, update_img)
    
    # 閉じ
    video.release()
    # 画面と次
    cv2.destroyAllWindows()

    # 大きさとか座標の辞書か
    result = {
        "fname": input_fname,
        "monitor_width": monitor_width,
        "monitor_height": monitor_height,
        "video_width": video_width,
        "video_height": video_height,
        "update_up_left": update_array[0],
        "update_up_right": update_array[1],
        "update_under_left": update_array[2],
        "update_under_right": update_array[3]
    }

    return result
        
# 全画面表示用
def show_img_fullscreen(winname, img):
    cv2.namedWindow(winname, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(winname, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.imshow(winname, img)

if __name__ == "__main__":
    main()