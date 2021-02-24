# 画像関係
import cv2
import numpy as np
# 画面情報
from screeninfo import get_monitors
# システム関係
import os
import sys
# json
import json
# GUI関係
import pyautogui
# GUI(tkinter)
import tkinter
import tkinter.filedialog as fd
# ばー
from tqdm import tqdm

class GUI():
    def __init__(self):
        # 画面作成
        self.root = tkinter.Tk()

        # タイトル
        self.root.title("go transform")
        # 大きさ
        self.root.geometry("800x500")

        # 変数関係
        self.select_input_fname = ""
        self.var_select_input_fname = tkinter.StringVar(self.root)
        self.var_select_input_fname.set("選択ファイル：")

        # 説明
        self.detail = tkinter.Label(text="1_setting_transformで設定したものを実行する者。\n設定ファイル(json)の選択と出力ファイル名の入力をして実行する。")
        self.detail.pack()

        # 入力ファイル名選択
        # 説明
        self.detail_input_file = tkinter.Label(text="\njsonファイル名(jsonファイル)")
        self.detail_input_file.pack()
        # ボタン
        self.select_input_fname_button = tkinter.Button(text="選択する")
        def select_input_file(event):
            self.select_input_fname = fd.askopenfilename()
            self.var_select_input_fname.set("選択ファイル："+self.select_input_fname)
        self.select_input_fname_button.bind("<Button-1>", select_input_file)
        self.select_input_fname_button.pack()
        # 千九結果
        self.result_select_input_fname = tkinter.Label(textvariable=self.var_select_input_fname)
        self.result_select_input_fname.pack()

        # 出力ファイル名
        # 説明
        self.output_fname_detail = tkinter.Label(text=u'\n出力ファイル名(mp4形式)')
        self.output_fname_detail.pack()
        # フォーム
        self.output_fname_edit_box = tkinter.Entry()
        self.output_fname_edit_box.pack()

        # 実行ボタン
        # 上のとスペース
        self.space = tkinter.Label(text=u'\n')
        self.space.pack()
        # 実行時の処理
        def go(event):
            # 入力ファイル名とる
            input_fname = self.select_input_fname
            # 出力ファイル名とる
            output_fname = self.output_fname_edit_box.get()

            self.root.destroy()

            # 実行
            f = open(input_fname, "r")
            datas = json.load(f)
            f.close()
            self.create_transform_video(datas, output_fname)

        # 生成
        self.go_button = tkinter.Button(text=u'実行')
        self.go_button.bind("<Button-1>", go)
        self.go_button.pack()

        # 表示
        self.root.mainloop()
    
    def create_transform_video(self, datas, output_fname):
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
        fps = video.get(cv2.CAP_PROP_FPS)
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
    gui = GUI()