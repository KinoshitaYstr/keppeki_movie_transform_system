# 画像系
import cv2
import numpy as np
# システム関係
import sys
import platform
import os
# ファイル名検索
import glob
# json関係
import json
# pyqt関係
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QLabel, QFileDialog, QColorDialog, QFrame, QLineEdit, QProgressBar, QWidget
from PyQt5.QtGui import QColor
from PyQt5.QtCore import QCoreApplication, QThread, pyqtSignal

class MainGUI(QWidget):
    # イニシャライズ
    def __init__(self, parent=None):
        # すぱー
        super(MainGUI, self).__init__(parent)

        # フォントサイズ
        self.font_size = 15

        # 情報のあるjson名変数
        self.json_name = ""

        # UIつくる
        self.initUI()

    
    # 最初のUI
    def initUI(self):
        # 大きさとタイトル設定
        self.resize(1000, 500)
        self.setWindowTitle("変換気")


        # ファイル読み込みボタン関係
        # 説明文
        self.open_json_name_label = self.create_label("jsonを選択")
        self.open_json_name_label.move(10, 10)
        # 開くボタン
        self.open_json_name_button = QPushButton("選択する", self)
        self.open_json_name_button.clicked.connect(self.select_json_file)
        self.open_json_name_button.move(10, 40)
        # 選択されたものを表示
        self.json_name_label = self.create_label(self.json_name)
        self.json_name_label.move(130, 45)

        # 実行ボタン
        self.go_button = QPushButton("変換する", self)
        self.go_button.clicked.connect(self.go)
        self.go_button.move(10, 70)

        # みせる
        self.show()
    

    # 表示するラベル生成
    def create_label(self, label_content):
        # つくってだす
        l = QLabel(label_content, self)
        l.resize(self.font_size*len(label_content), int(self.font_size*1.3))
        return l
    

    # ファイル選択
    def select_json_file(self):
        # pyqtのファイルサーチウィンドウ出してそこで出される値を取る
        fname = QFileDialog.getOpenFileName(self, "開く", os.getcwd())
        # そのデータから映像名とる
        self.json_name = fname[0]
        

    # 実行
    def go(self):
        print("go")
        # 一回閉じる
        self.close()

        # 変換用のyatusasu
        self.now_transform = NowTransformClass(self, self.json_name)


# 実行用クラス
class NowTransformClass(QWidget):
    # イニシャライズ
    def __init__(self, parent=None, json_name=""):
        print(json_name)
        print("NowTransformClass")
        # すぱー
        super(NowTransformClass, self).__init__()

        # フォルダ内のjsonすべて取る
        self.json_name = json_name

        # UI初期化
        self.initUI()

    # UI設定
    def initUI(self):
        # 実行中の経過を表示
        # 大きさとタイトル
        self.resize(1000, 500)
        self.setWindowTitle("変換してるよ")
        # プログレスばー
        self.progress_bar = QProgressBar(self)
        self.progress_bar.move(10, 10)

        # 見せるぜ
        self.show()

        # 実行とか
        self.thread = TransformThread(self.json_name)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.thread.change_value.connect(self.set_progress_bar_value)
        self.thread.start()

    # プログレスバーデータセット
    def set_progress_bar_value(self, val):
        self.progress_bar.setValue(val)


class TransformThread(QThread):
    # https://codeloop.org/pyqt5-qprogressbar-with-qthread-practical-example/
    # Create a counter thread
    change_value = pyqtSignal(int)
    # イニシャライズ
    def __init__(self, json_name):
        # すぺー
        super(TransformThread,self).__init__()

        # jsonでーた読み取り
        json_open = open(json_name, "r")
        self.json_data = json.load(json_open)

        # cvから大本データ読み取り
        self.original_movie = cv2.VideoCapture(self.json_data["original_name"])
        # フレーム数とる
        self.n_frame = int(self.original_movie.get(cv2.CAP_PROP_FRAME_COUNT))

        # 変換用行列作成
        original_position = np.float32([
            self.json_data["original_position"]["p_up_left"],
            self.json_data["original_position"]["p_up_right"],
            self.json_data["original_position"]["p_under_left"],
            self.json_data["original_position"]["p_under_right"],
        ])
        updated_position = np.float32([
            self.json_data["updated_position"]["p_up_left"],
            self.json_data["updated_position"]["p_up_right"],
            self.json_data["updated_position"]["p_under_left"],
            self.json_data["updated_position"]["p_under_right"],
        ])
        self.matrix = cv2.getPerspectiveTransform(original_position, updated_position)
        
        # 背景の大きさ
        self.back_size = (self.json_data["monitor_size"][0], self.json_data["monitor_size"][0])
        # 背景色
        self.background_color = (
            self.json_data["background_color"][2],
            self.json_data["background_color"][1],
            self.json_data["background_color"][0],
        )
        # 新規作成用
        fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
        fps = int(self.original_movie.get(cv2.CAP_PROP_FPS))
        self.updated_movie = cv2.VideoWriter("result_"+self.json_data["original_name"], fourcc, fps, self.back_size)

    def run(self):
        # 最初にもどす
        # self.original_movie.set(cv2.CAP_PROP_POS_FRAMES, 0)
        # sinntyoku??
        count = 0
        # 実際にやる
        while True:
            count += 1
            # 読み取り
            ret, original_img = self.original_movie.read()
            if not ret:
                break
            # 変形
            updated_img = cv2.warpPerspective(original_img, self.matrix, self.back_size, borderValue=self.background_color)
            self.updated_movie.write(updated_img)
            # sinntyoku osieru
            self.change_value.emit(int(count*100/self.n_frame))
        # 解放
        self.original_movie.release()
        self.updated_movie.release()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_gui = MainGUI()
    sys.exit(app.exec_())