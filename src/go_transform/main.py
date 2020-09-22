# 画像系
import cv2
import numpy as np
# システム関係
import sys
import platform
# ファイル名検索
import glob
# json関係
import json
# pyqt関係
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QLabel, QFileDialog, QColorDialog, QFrame, QLineEdit, QProgressBar, QWidget
from PyQt5.QtGui import QColor
from PyQt5.QtCore import QCoreApplication

class MainGUI(QWidget):
    # イニシャライズ
    def __init__(self, parent=None):
        # すぱー
        super(MainGUI, self).__init__(parent)

        # フォントサイズ
        self.font_size = 15

        # 情報のあるjson名変数
        self.json_filenames = []

        # jsonフォルダパス入れるもの
        self.json_dir = ""

        # UIつくる
        self.initUI()

    
    # 最初のUI
    def initUI(self):
        # 大きさとタイトル設定
        self.resize(1000, 500)
        self.setWindowTitle("変換気")


        # ファイル読み込みボタン関係
        # 説明文
        self.open_json_dir_label = self.create_label("フォルダを選択")
        self.open_json_dir_label.move(10, 10)
        # 開くボタン
        self.open_json_dir_button = QPushButton("選択する", self)
        self.open_json_dir_button.clicked.connect(self.select_jsons_dir)
        self.open_json_dir_button.move(10, 40)
        # 選択されたものを表示
        self.json_dir_label = self.create_label(self.json_dir)
        self.json_dir_label.move(130, 45)

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
    

    # フォルダ選択
    def select_jsons_dir(self):
        self.json_dir = QFileDialog.getExistingDirectory(self)
        self.json_dir_label.setText(self.json_dir)
        self.json_dir_label.resize(self.font_size*len(self.json_dir), self.font_size)

    # 実行
    def go(self):
        print("go")
        # 一回閉じる
        self.close()

        # 変換用のyatusasu
        self.now_transform = NowTransformClass(self)

        # self.show()

        # # 一個ずつみる
        # for json_name in json_names:
        #     # 読み込み
        #     json_open = open(json_name, "r")
        #     json_data = json.load(json_open)
        #     print(json_data)

        #     test_max = 100
        #     for i in range(test_max):
        #         self.progress_bar.setValue(i)



# 実行用クラス
class NowTransformClass(QWidget):
    # イニシャライズ
    def __init__(self, parent=None):
        print("NowTransformClass")
        # すぱー
        super(NowTransformClass, self).__init__()

        # json名取得
        # self.json_names = glob.glob(json_dir+"/*.json")

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

        


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_gui = MainGUI()
    sys.exit(app.exec_())