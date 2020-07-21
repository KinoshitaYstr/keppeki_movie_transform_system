import cv2
import numpy as np
from tqdm import tqdm
import os
import ctypes
import pyautogui
from screeninfo import get_monitors
import moviepy.editor as mp
import argparse
import random
import json
import pydub
from pydub import AudioSegment

# pyqt関係
import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QLabel, QFileDialog, QColorDialog, QFrame, QLineEdit
from PyQt5.QtGui import QColor
from PyQt5.QtCore import QCoreApplication

# pyqtでGUI作成
class MainGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.original_movie_name = ""
        self.font_size = 15 # デフォルトは大きさ15?
        self.background_color = QColor(0, 0, 0)
        self.output_name = "result.mp4"
        self.click_circle_area = 30
        self.initUI()
        self.set_position = {}

    def on_mouse(self, event, x, y, flag, params):
        if event == cv2.EVENT_LBUTTONDOWN:
            params["clicked"] = True

    def initUI(self):
        self.resize(1000, 500)
        self.setWindowTitle("映像変換器")

        # 映像読込ボタン関係
        # 説明文?
        self.open_movie_label = self.create_label("変形したい映像の選択")
        self.open_movie_label.move(10, 10)
        # ボタン
        self.open_movie_button = QPushButton("開く", self)
        self.open_movie_button.clicked.connect(self.open_original_movie)
        self.open_movie_button.move(10, 40)
        # 対象ファイル名
        self.original_movie_name_label = self.create_label("None")
        self.original_movie_name_label.move(130, 47)

        # 背景色の指定
        self.select_back_color_label = self.create_label("背景色の選択")
        self.select_back_color_label.move(10, 90)
        self.sample_back_color_frame = QFrame(self)
        self.sample_back_color_frame.setStyleSheet("QWidget { background-color : %s }" % self.background_color.name())
        self.sample_back_color_frame.resize(100, 100)
        self.sample_back_color_frame.move(130, 120)
        self.select_back_color_button = QPushButton("選択", self)
        self.select_back_color_button.clicked.connect(self.select_background_color)
        self.select_back_color_button.move(10, 120)

        # ファイル名の指定
        self.output_name_label = self.create_label("出力ファイル名")
        self.output_name_label.move(10, 230+7)
        self.output_name_edit = QLineEdit(self.output_name, self)
        self.output_name_edit.move(130, 230)

        # 変形実行ボタン作成
        self.transform_button = QPushButton("変形", self)
        self.transform_button.clicked.connect(self.go_transform)
        self.transform_button.move(10, 280)

        self.show()
    
    def create_label(self, label_content):
        l = QLabel(label_content, self)
        l.resize(self.font_size*len(label_content), self.font_size)
        return l

    # ファイル選択
    def open_original_movie(self):
        fname = QFileDialog.getOpenFileName(self, "開く", os.getcwd())
        self.original_movie_name = fname[0]
        self.original_movie_name_label.setText(self.original_movie_name)
        self.original_movie_name_label.resize(self.font_size*len(self.original_movie_name), self.font_size)
    
    # 背景色の選択
    def select_background_color(self):
        col = QColorDialog.getColor()
        if col.isValid():
            self.background_color = col
            self.sample_back_color_frame.setStyleSheet("QWidget { background-color : %s }" % self.background_color.name())

    # 変形実行ボタン
    def go_transform(self):
        self.output_name = self.output_name_edit.text()
        # print(self.output_name)
        # QCoreApplication.instance().quit()
        self.close()
        self.set_transform_movie()
        
        # self.go_transform_movie()
        # self.get_sound()
    
    # 映像変形の指定？関数
    def set_transform_movie(self):
        video = cv2.VideoCapture(self.original_movie_name)

        img_width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
        img_height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        back_size = (get_monitors()[0].width, get_monitors()[0].height)
        rate = 1 if 1 <= back_size[0]/img_width else back_size[0]/img_width
        rate = rate if rate <= back_size[1]/img_height else back_size[1]/img_height
        p_up_left = [0, 0]
        p_up_right = [img_width, 0]
        p_under_left = [0, img_height]
        p_under_right = [img_width, img_height]
        
        origina_position = {}
        origina_position['p_up_left'] = p_up_left
        origina_position['p_up_right'] = p_up_right
        origina_position['p_under_left'] = p_under_left
        origina_position['p_under_right'] = p_under_right
        img_original = np.float32([
            p_up_left, p_up_right, p_under_left, p_under_right
        ])

        p_up_left = [0, 0]
        p_up_right = [int(img_width*rate), 0]
        p_under_left = [0, int(img_height*rate)]
        p_under_right = [int(img_width*rate), int(img_height*rate)]

        params = {"clicked": False}

        self.winname = "transform"
        cv2.namedWindow(self.winname, cv2.WINDOW_NORMAL)
        cv2.setWindowProperty(self.winname, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.setMouseCallback(self.winname, self.on_mouse, params)
        now_select_area_flag = -1
        while True:
            key = cv2.waitKey(1)&0xff
            ret, self.img = video.read()
            if not ret:
                video.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue
            # エンターキー
            if key == 13:
                break
            if params["clicked"]:
                params["clicked"] = False
                if now_select_area_flag == -1:
                    if self.judge_area(p_up_left):
                        now_select_area_flag = 1
                    elif self.judge_area(p_up_right):
                        now_select_area_flag = 2
                    elif self.judge_area(p_under_left):
                        now_select_area_flag = 3
                    elif self.judge_area(p_under_right):
                        now_select_area_flag = 4
                else:
                    now_select_area_flag = -1
            elif now_select_area_flag == 1:
                p_up_left = pyautogui.position()
            elif now_select_area_flag == 2:
                p_up_right = pyautogui.position()
            elif now_select_area_flag == 3:
                p_under_left = pyautogui.position()
            elif now_select_area_flag == 4:
                p_under_right = pyautogui.position()
            img_trans = np.float32([
                p_up_left, p_up_right, p_under_left, p_under_right
            ])
            matrix = cv2.getPerspectiveTransform(img_original, img_trans)
            rgb = self.background_color.getRgb()
            self.img = cv2.warpPerspective(self.img, matrix, back_size, borderValue=(rgb[2], rgb[1], rgb[0]))
            cv2.circle(self.img, tuple(p_up_left), self.click_circle_area, (0, 0, 255, 1))
            cv2.circle(self.img, tuple(p_up_right), self.click_circle_area, (0, 0, 255, 1))
            cv2.circle(self.img, tuple(p_under_left), self.click_circle_area, (0, 0, 255, 1))
            cv2.circle(self.img, tuple(p_under_right), self.click_circle_area, (0, 0, 255, 1))
            self.show_img_fullscreen()
        cv2.destroyAllWindows()
        video.release()
        self.set_position['p_up_left'] = p_up_left
        self.set_position['p_up_right'] = p_up_right
        self.set_position['p_under_left'] = p_under_left
        self.set_position['p_under_right'] = p_under_right
        json_datas = {}
        json_datas["target_name"] = self.original_movie_name
        json_datas["original_pos"] = origina_position
        json_datas["transform_pos"] = self.set_position
        json_datas["back_size"] = back_size
        json_datas["back_color"] = self.background_color.name()
        # 座標をjsonでせーぶ
        # print(self.set_position)
        with open("pos.json", 'w') as f:
            json.dump(json_datas, f, indent=2)
    
    def judge_area(self, target):
        pos = pyautogui.position()
        d = (pos[0]-target[0])^2
        d += (pos[1]-target[1])^2
        return d < self.click_circle_area^2

    def show_img_fullscreen(self):
        cv2.namedWindow(self.winname, cv2.WINDOW_NORMAL)
        cv2.setWindowProperty(self.winname, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.imshow(self.winname, self.img)    
    
    def go_transform_movie(self):
        # 一度音楽を別で保存(抽出)してから変形後の動画に乗っける感じ
        video = cv2.VideoCapture(self.original_movie_name)
        fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
        fps = int(video.get(cv2.CAP_PROP_FPS))
        back_size = (get_monitors()[0].width, get_monitors()[0].height)
        output = cv2.VideoWriter("result.mp4", fourcc, fps, back_size)
        while True:
            ret, img = video.read()
            if not ret:
                break
        video.release()
        output.release()
    
    def get_sound(self):
        # 元映像から音声抽出
        format_name = self.original_movie_name.split(".")[-1]
        print(format_name)
        base_sound = AudioSegment.from_file(self.original_movie_name, format=format_name)
        base_sound.export("tmp.mp3")

# 基礎機能
def onMouse(event, x, y, flag, params):
    if event == cv2.EVENT_LBUTTONDOWN:
        params["clicked"] = True

def copy_movie_audio(input_name, output_name, tmp_output_name="tmp.mp3", fname="tmp.mp3"):
    clip = mp.VideoFileClip(input_name).subclip()
    clip.audio.write_audiofile(fname)
    clip = mp.VideoFileClip(tmp_output_name).subclip()
    clip.write_videofile(output_name, audio=fname)

def judge_area(target, length=10):
    pos = pyautogui.position()
    d = (pos[0]-target[0])*(pos[0]-target[0])
    d += (pos[1]-target[1])*(pos[1]-target[1])
    return d < length*length

def imshow_fullscreen(winname, img):
    cv2.namedWindow(winname, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(winname, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.imshow(winname, img)
    delete_frame(winname)

def delete_frame(winname, rgb=(0, 0, 0)):
    if os.name == 'nt':
        hwnd = ctypes.windll.user32.FindWindowW(0, winname)
        ctypes.windll.user32.SetClassLongPtrW(hwnd, -10, ctypes.windll.Gdi32.CreateSolidBrush(rgb[0], rgb[1], rgb[2]))

def main():
    parser = argparse.ArgumentParser(description="映像射影変換ツール\npython3 main.py input_name output_name")
    parser.add_argument('input_name', help="射影変換対象動画名")
    parser.add_argument('output_name', help="変換後出力動画名(mp4)")
    
    args = parser.parse_args()

    input_name = args.input_name
    output_name = args.output_name
    tmp_output_name = "tmp_{}.mp4".format(random.randint(0,1000000000))
    tmp_sound = "tmp_{}.mp3".format(random.randint(0,1000000000))
    
    video = cv2.VideoCapture(input_name)

    img_width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    img_height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    n_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = int(video.get(cv2.CAP_PROP_FPS))

    params = {"clicked": False}
    cv2.namedWindow("cap", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("cap", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.setMouseCallback("cap", onMouse, params)

    back_size = (get_monitors()[0].width, get_monitors()[0].height)

    rate = 1 if 1 <= back_size[0]/img_width else back_size[0]/img_width
    rate = rate if rate <= back_size[1]/img_height else back_size[1]/img_height

    p_up_left = [0, 0]
    p_up_right = [img_width, 0]
    p_under_left = [0, img_height]
    p_under_right = [img_width, img_height]
    
    img_original = np.float32([
        p_up_left, p_up_right, p_under_left, p_under_right
    ])

    p_up_left = [0, 0]
    p_up_right = [int(img_width*rate), 0]
    p_under_left = [0, int(img_height*rate)]
    p_under_right = [int(img_width*rate), int(img_height*rate)]

    flag = -1
    while True:
        ret, img = video.read()
        if not ret:
            video.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue
        key = cv2.waitKey(1)&0xff
        if key == ord('s'):
            break
        elif key == ord('q'):
            video.release()
            return

        if flag == -1 and params["clicked"]:
            params["clicked"] = False
            if judge_area(p_up_left):
                flag = 1
            elif judge_area(p_up_right):
                flag = 2
            elif judge_area(p_under_left):
                flag = 3
            elif judge_area(p_under_right):
                flag = 4
        elif params["clicked"]:
            params["clicked"] = False
            flag = -1
        elif flag == 1:
            p_up_left = pyautogui.position()
        elif flag == 2:
            p_up_right = pyautogui.position()
        elif flag == 3:
            p_under_left = pyautogui.position()
        elif flag == 4:
            p_under_right = pyautogui.position()

        img_trans = np.float32([
            p_up_left, p_up_right, p_under_left, p_under_right
        ])
        matrix = cv2.getPerspectiveTransform(img_original, img_trans)
        img = cv2.warpPerspective(img, matrix, back_size)

        cv2.circle(img, tuple(p_up_left), 10, (0, 0, 255), 1)
        cv2.circle(img, tuple(p_up_right), 10, (0, 0, 255), 1)
        cv2.circle(img, tuple(p_under_left), 10, (0, 0, 255), 1)
        cv2.circle(img, tuple(p_under_right), 10, (0, 0, 255), 1)

        imshow_fullscreen("cap", img)
    
    cv2.destroyAllWindows()
    video.set(cv2.CAP_PROP_POS_FRAMES, 0)

    fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
    output = cv2.VideoWriter(tmp_output_name, fourcc, fps, back_size)
    
    for i in tqdm(range(n_frames)):
        ret, img = video.read()
        if not ret:
            break
        img = cv2.warpPerspective(img, matrix, back_size)
        output.write(img)

    video.release()
    output.release()

    copy_movie_audio(input_name, output_name, tmp_output_name, tmp_sound)

    os.remove(tmp_output_name)
    os.remove(tmp_sound)

if __name__ != "__main__":
    main()
else:
    app = QApplication(sys.argv)
    main_gui = MainGUI()
    sys.exit(app.exec_())