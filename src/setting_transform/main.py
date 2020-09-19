# 画像関係(映像もちょっと)
import cv2
import numpy as np
# システム周りいじじするもの
import os
import sys
# GUI関係
import pyautogui
# 画面関係
from screeninfo import get_monitors
# jsonで結果出す予定よ
import json
# pyqt関係
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QLabel, QFileDialog, QColorDialog, QFrame, QLineEdit
from PyQt5.QtGui import QColor
from PyQt5.QtCore import QCoreApplication

# pyqtでGUI作成
class MainGUI(QMainWindow):
    # イニシャライズ
    def __init__(self):
        # すーぱー
        super().__init__()

        # 保持するための変数設定(初期設定いるもの)
        # 元の動画名
        self.original_movie_name = ""
        # 表示させるラベル文字の大きさ
        self.font_size = 15 # デフォルトは大きさ15?
        # 映像背景の色
        self.background_color = QColor(0, 0, 0)
        # 座標出力のときのjsonの名前
        self.output_name = "result.json"
        # クリック有効範囲
        self.click_circle_area = 10
        
        # UIつくるぜ！！
        self.initUI()


    # 最初のUI
    def initUI(self):
        # 大崎とタイトル設定
        self.resize(1000, 500)
        self.setWindowTitle("映像変換器")


        # 映像読込ボタン関係

        # 説明文?
        self.open_movie_label = self.create_label("変形したい映像の選択")
        # 表示座標
        self.open_movie_label.move(10, 10)

        # ボタン
        self.open_movie_button = QPushButton("開く", self)
        # ボタン押されたときにやること
        self.open_movie_button.clicked.connect(self.open_original_movie)
        # 表示座標
        self.open_movie_button.move(10, 40)

        # 対象ファイル名
        self.original_movie_name_label = self.create_label("None")
        # 表示座標
        self.original_movie_name_label.move(130, 47)


        # 背景色設定関係

        # 説明らべる
        self.select_back_color_label = self.create_label("背景色の選択")
        # 表示座標
        self.select_back_color_label.move(10, 90)
        
        # 指定されてる色のサンプル表示関係
        # サンプルUI
        self.sample_back_color_frame = QFrame(self)
        # CSSで実際に色指定
        self.sample_back_color_frame.setStyleSheet("QWidget { background-color : %s }" % self.background_color.name())
        # 大きさ設定
        self.sample_back_color_frame.resize(100, 100)
        # 表示座標
        self.sample_back_color_frame.move(130, 120)
        
        # 設定ボタン作成
        self.select_back_color_button = QPushButton("選択", self)
        # ボタン押されたときの処理
        self.select_back_color_button.clicked.connect(self.select_background_color)
        # 表示座標
        self.select_back_color_button.move(10, 120)


        # ファイル名(json)の指定
 
        # 説明ラベル
        self.output_name_label = self.create_label("出力ファイル名(.json)")
        # 表示座標
        self.output_name_label.move(10, 230+7)
        # テキストボックスで出力名変えられる
        self.output_name_edit = QLineEdit(self.output_name, self)
        # 表示座標
        self.output_name_edit.move(130+30, 230)


        # 変形実行ボタン作成
        # ボタン作る
        self.transform_button = QPushButton("変形", self)
        # 押されたときにやりたいこと
        self.transform_button.clicked.connect(self.go_transform)
        # 表示座標
        self.transform_button.move(10, 280)

        # みせるぜ！！
        self.show()
    


    # 表示するラベル生成
    def create_label(self, label_content):
        # つくってだす！！
        l = QLabel(label_content, self)
        l.resize(self.font_size*len(label_content), int(self.font_size*1.3))
        return l



    # ファイル選択
    def open_original_movie(self):
        # pyqtのファイルサーチウィンドウ出してそこで出される値を取る
        fname = QFileDialog.getOpenFileName(self, "開く", os.getcwd())
        # そのデータから映像名とる
        self.original_movie_name = fname[0]
        # 出力jsonの名前を映像名.jsonにするの設定
        self.output_name = fname[0].split("/")[-1]
        self.output_name = self.output_name.split(".")[0]+".json"
        # 出力名見せる
        self.output_name_edit.setText(self.output_name)
        # 選んだ映像名を見せる
        self.original_movie_name_label.setText(self.original_movie_name)
        # 大きさ調整
        self.original_movie_name_label.resize(self.font_size*len(self.original_movie_name), self.font_size)
    


    # 背景色の選択
    def select_background_color(self):
        # カラーピッカーだす
        col = QColorDialog.getColor()
        # 有効な色家判断してそれを取得とサンプル表示
        if col.isValid():
            self.background_color = col
            self.sample_back_color_frame.setStyleSheet("QWidget { background-color : %s }" % self.background_color.name())



    # 変形実行ボタン
    def go_transform(self):
        # 出力名とる
        self.output_name = self.output_name_edit.text()
        # ウィンドウとじ
        self.close()
        # やるぞ！！！
        self.set_transform_movie()
    


    # 映像変形の指定？関数
    def set_transform_movie(self):
        # 必要な変数設定

        # 映像開く
        video = cv2.VideoCapture(self.original_movie_name)

        # 映像おおきさ
        # 幅
        movie_width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
        # 高さ
        movie_height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # モニター大きさ
        # 幅
        monitor_width = get_monitors()[0].width
        # 高さ
        monitor_height = get_monitors()[0].height
        # セット
        monitor_size = (monitor_width, monitor_height)

        # 初期は画面いっぱいに表示したいから映像とモニターの大きさ比
        rate = 1 if 1 <= monitor_width/movie_width else monitor_width/movie_width
        rate = rate if rate <= monitor_height/movie_height else monitor_height/movie_height

        # 座標関係
        # 元の画像大きさ保持
        # 左上
        p_up_left = [0, 0]
        # 右上
        p_up_right = [movie_width, 0]
        # 左下
        p_under_left = [0, movie_height]
        # 右下
        p_under_right = [movie_width, movie_height]
        # それらを辞書保存(出力楽にするためのもの)
        original_position = {}
        original_position["p_up_left"] = p_up_left
        original_position["p_up_right"] = p_up_right
        original_position["p_under_left"] = p_under_left
        original_position["p_under_right"] = p_under_right
        # 実際に扱えるように設定
        movie_original_position = np.float32([
            p_up_left, p_up_right, p_under_left, p_under_right
        ])

        # いじったりしたあと
        # 左上
        p_up_left = [0+self.click_circle_area, 0+self.click_circle_area]
        # 右上
        p_up_right = [int(movie_width*rate)-self.click_circle_area, 0+self.click_circle_area]
        # 左下
        p_under_left = [0+self.click_circle_area, int(movie_height*rate)-self.click_circle_area]
        # 右下
        p_under_right = [int(movie_width*rate)-self.click_circle_area, int(movie_height*rate)-self.click_circle_area]
        # 配列セット
        updated_position_array = [p_up_left, p_up_right, p_under_left, p_under_right]
        

        # クリック結果保存用
        click_params = {"clicked": True}
        # クリック舌箇所保存用フラグ
        now_select_area_flag = -1

        # opencv表示用ウィンドウ関係
        # ウィンド名
        winname = "transform"
        # 設定
        cv2.namedWindow(winname, cv2.WINDOW_NORMAL)
        # 全画面出す
        cv2.setWindowProperty(winname, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        
        # 背景色
        background_rgb = self.background_color.getRgb()

        # やったるで！！
        while True:
            # きーぼーど
            key = cv2.waitKey(1)&0xff
            # 映像から画像とフラグ取る
            ret, img = video.read()
            # 読み込みが終わっていたとき
            if not ret:
                # 最初から読めるようにする
                video.set(cv2.CAP_PROP_POS_FRAMES, 0)
                # さいしょからやろ
                continue
            
            if key == 13:
                # エンターキーで終了
                break
            elif key == ord('1'):
                # 左上いじる
                now_select_area_flag = 0
            elif key == ord('2'):
                # 右上いじる
                now_select_area_flag = 1
            elif key == ord('3'):
                # 左下いじる
                now_select_area_flag = 2
            elif key == ord('4'):
                # 右下いじる
                now_select_area_flag = 3
            else:
                # ボタンが押されてなかったら戻す
                now_select_area_flag = -1
            
            # 指定されたとこの座標カエル
            if now_select_area_flag != -1:
                updated_position_array[now_select_area_flag] = pyautogui.position()

            # 表示設定
            # 座標設定
            updated_movie_position = np.float32(updated_position_array)
            # 変換行列生成
            self.matrix = cv2.getPerspectiveTransform(movie_original_position, updated_movie_position)
            updated_img = cv2.warpPerspective(img, self.matrix, monitor_size, borderValue=(background_rgb[2], background_rgb[1], background_rgb[0]))
            # クリックできる範囲の丸書く
            for pos in updated_position_array:
                cv2.circle(updated_img, tuple(pos), self.click_circle_area, (0, 0, 255, 1))


            # 表示する
            self.show_img_fullscreen(updated_img, winname)
            

        # 映像閉じる
        video.release()


        # 結果をjsonで出力
        # 変更後の4墨
        updated_position = {}
        updated_position["p_up_left"] = updated_position_array[0]
        updated_position["p_up_right"] = updated_position_array[1]
        updated_position["p_under_left"] = updated_position_array[2]
        updated_position["p_under_right"] = updated_position_array[3]
        # 出力用連想配列
        result_json = {}
        result_json["original_name"] = self.original_movie_name.replace("\\n", "/").split("/")[-1]
        result_json["original_position"] = original_position
        result_json["updated_position"] = updated_position
        result_json["monitor_size"] = monitor_size
        result_json["background_color"] = background_rgb
        # 出力
        with open(self.output_name, 'w') as f:
            json.dump(result_json, f, indent=2)


    # 全画面表示
    def show_img_fullscreen(self, img, winname):
        cv2.namedWindow(winname, cv2.WINDOW_NORMAL)
        cv2.setWindowProperty(winname, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.imshow(winname, img)

    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_gui = MainGUI()
    sys.exit(app.exec_())