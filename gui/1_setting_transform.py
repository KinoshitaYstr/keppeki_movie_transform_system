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

class GUI():
    def __init__(self):
        # 画面作成
        self.root = tkinter.Tk()

        # 変数(グローバル変数)
        self.select_input_fname = ""
        self._select_input_fname = tkinter.StringVar(self.root)
        self._select_input_fname.set("選択ファイル：")

        # タイトル
        self.root.title("setting transform")
        # 大きさ
        self.root.geometry("800x570")

        # 説明
        self.detail = tkinter.Label(text=u'映像(音無し)の射影変換を行うもの。\n入力ファイル名(動画)と出力ファイル名(json)を入力して実行する。\n実行中、キーの1で右上、2で左上、3で右下、4で左下をマウスに合わせる。\nエンターキーで出力する。')
        self.detail.pack()

        # 入力ファイル名
        # 説明
        self.input_fname_detail = tkinter.Label(text=u'\n入力ファイル名(パス)')
        self.input_fname_detail.pack()
        # # フォーム
        # input_fname_edit_box = tkinter.Entry()
        # input_fname_edit_box.pack()
        # ファイル選択するためのボタン
        self.select_input_file_button = tkinter.Button(text=u'選択する')
        def select_input_file(event):
            self.select_input_fname = fd.askopenfilename()
            self._select_input_fname.set("選択ファイル："+self.select_input_fname)
        self.select_input_file_button.bind("<Button-1>", select_input_file)
        self.select_input_file_button.pack()
        # 選択結果
        self.result_select_input_fname = tkinter.Label(textvariable=self._select_input_fname)
        self.result_select_input_fname.pack()

        # 出力ファイル名
        # 説明
        self.output_fname_detail = tkinter.Label(text=u'\n出力ファイル名(パス)')
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
            # 入力ファイル名撮る
            input_fname = self.select_input_fname
            # 出力ファイル名撮る
            output_fname = self.output_fname_edit_box.get()

            self.root.destroy()
            # sys.exit()
            
            # 処理
            datas = self.setting_transform(input_fname)
            print(datas)
            # 結果json保存
            with open(output_fname, "w") as f:
                json.dump(datas, f, indent=2)


        # 生成
        self.go_button = tkinter.Button(text=u'実行')
        self.go_button.bind("<Button-1>", go)
        self.go_button.pack()

        # 表示
        self.root.mainloop()

    # 全画面表示用
    def show_img_fullscreen(self, winname, img):
        cv2.namedWindow(winname, cv2.WINDOW_NORMAL)
        cv2.setWindowProperty(winname, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.imshow(winname, img)

    # メイン処理
    def setting_transform(self, input_fname):
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
            self.show_img_fullscreen(winname, update_img)
        
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
    
if __name__ == "__main__":
    gui = GUI()