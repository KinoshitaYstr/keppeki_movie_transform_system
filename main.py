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

# pyqt関係
import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QLabel, QFileDialog

# pyqtでGUI作成
class MainGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.original_movie_name = ""
        self.font_size = 15 # デフォルトは大きさ15?
        self.initUI()

    def initUI(self):
        self.resize(1000, 500)
        self.setWindowTitle("映像変換器")

        # 映像読込ボタン関係
        # 説明文?
        self.open_movie_label = self.create_label("変形したい映像を選択してください")
        self.open_movie_label.move(10, 10)
        # ボタン
        self.open_movie_button = QPushButton("開く", self)
        self.open_movie_button.clicked.connect(self.open_original_movie)
        self.open_movie_button.move(10, 40)
        # 対象ファイル名
        self.original_movie_name_label = self.create_label("None")
        self.original_movie_name_label.move(130, 47)

        self.show()
    
    def create_label(self, label_content):
        l = QLabel(label_content, self)
        l.resize(self.font_size*len(label_content), self.font_size)
        return l

    # ファイル読み込み
    def open_original_movie(self):
        fname = QFileDialog.getOpenFileName(self, "開く", os.getcwd())
        self.original_movie_name = fname[0]
        self.original_movie_name_label.setText(self.original_movie_name)
        self.original_movie_name_label.resize(self.font_size*len(self.original_movie_name), self.font_size)


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