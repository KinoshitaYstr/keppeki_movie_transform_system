# システム関係
import sys
import platform
import os
# pyqt関係
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QLabel, QFileDialog, QColorDialog, QFrame, QLineEdit, QProgressBar, QWidget
from PyQt5.QtGui import QColor
from PyQt5.QtCore import QCoreApplication, QThread, pyqtSignal
# 音声関係
import moviepy.editor as mp


class MainGUI(QWidget):
    # イニシャライズ
    def __init__(self, parent=None):
        # すぺー
        super(MainGUI, self).__init__(parent)

        # フォントサイズ
        self.font_size = 15

        # コピー元
        self.original_movie_name = ""
        # コピー先
        self.target_movie_name = ""

        # UIつくる
        self.initUI()
    
    # UI作成
    def initUI(self):
        # 大きさとタイトル設定
        self.resize(1000, 500)
        self.setWindowTitle("音源コピー")

        # ファイル読み込みボタン関係
        # コピー元指定用
        # 説明文
        self.open_original_movie_name_label = self.create_label("コピー元の動画を選択")
        self.open_original_movie_name_label.move(10, 10)
        # 開くボタン
        self.open_original_movie_name_button = QPushButton("選択する", self)
        self.open_original_movie_name_button.clicked.connect(self.select_original_movie_name)
        self.open_original_movie_name_button.move(10, 40)
        # コピー先指定用
        # 説明文
        self.open_target_movie_name_label = self.create_label("コピー先の動画を選択")
        self.open_target_movie_name_label.move(10, 80)
        # 開くボタン
        self.open_target_movie_name_button = QPushButton("選択する", self)
        self.open_target_movie_name_button.clicked.connect(self.select_target_movie_name)
        self.open_target_movie_name_button.move(10, 110)

        # 実行ボタン
        self.go_button = QPushButton("変換する", self)
        self.go_button.clicked.connect(self.go)
        self.go_button.move(10, 150)


        # みせｒつ
        self.show()

    
    # 表示するラベル生成
    def create_label(self, label_content):
        # つくってだす
        l = QLabel(label_content, self)
        l.resize(self.font_size*len(label_content), int(self.font_size*1.3))
        return l


    # コピー元ファイル選択
    def select_original_movie_name(self):
        # pyqtのファイルサーチウィンドウ出してそこで出される値を取る
        fname = QFileDialog.getOpenFileName(self, "開く", os.getcwd())
        # そのデータから映像名とる
        self.original_movie_name = fname[0]

    # コピー先ファイル選択
    def select_target_movie_name(self):
        # pyqtのファイルサーチウィンドウ出してそこで出される値を取る
        fname = QFileDialog.getOpenFileName(self, "開く", os.getcwd())
        # そのデータから映像名とる
        self.target_movie_name = fname[0]


    # コピーする
    def go(self):
        # さっきまでのを非表示
        self.open_original_movie_name_label.hide()
        self.open_original_movie_name_button.hide()
        self.open_target_movie_name_button.hide()
        self.open_target_movie_name_label.hide()
        self.go_button.hide()
        
        # スレッド作った方がよい？？
        # 実際にやる
        # 先のファイル名を一度替える
        os.rename(self.target_movie_name, self.target_movie_name+".tmp")
        # 音声抽出
        original_sound = mp.VideoFileClip(self.original_movie_name).subclip()
        original_sound.audio.write_audiofile("tmp.mp3")
        # 音声付与
        output = mp.VideoFileClip(self.target_movie_name+".tmp").subclip()
        output.write_videofile(self.target_movie_name, audio="tmp.mp3")

        # 不要なもの消す
        os.remove("tmp.mp3")
        os.remove(self.target_movie_name+".tmp")

        self.close()

    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_gui = MainGUI()
    sys.exit(app.exec_())