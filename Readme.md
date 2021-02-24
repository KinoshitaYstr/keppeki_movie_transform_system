* python version : 3.7.2

# windows
## 実行ファイル作成
### 共通
* pip install -r requirements.txt
### CUI
* pyinstaller .\\cui\\1_cui.py --onefile --noconsole
* pyinstaller .\\cui\\2_cui.py --onefile --noconsole
### GUI
* pyinstaller .\\gui\\1_setting_transform.py --onefile --noconsole
* pyinstaller .\\gui\\2_transform.py --onefile --noconsole

# ↓いろんなことめも

### setup
* pip install -r requirements.txt

### usage
## unix?
* python main.py <input file name> <output file name>

## other?
* ffmpegいれろ
* 座標位置決めるプログラムと変形するプログラムを分ける？？
* 分けると位置決めるのだけ時間かけて、変形はプログラム動かすだけだから、変形時は寝れる？？神！！！

### setup in raspberry pi
* https://maskaravivek.medium.com/how-to-install-ffmpeg-and-ffserver-on-raspberry-pi-ed0eddf86f88
* https://symamone-tec.com/raspberrypi_pyqt5/
* https://stackoverflow.com/questions/38613316/how-to-upgrade-pip3
* https://stackoverflow.com/questions/53347759/importerror-libcblas-so-3-cannot-open-shared-object-file-no-such-file-or-dire
* https://github.com/evancohen/sonus/issues/54
* https://stackoverflow.com/questions/61509812/issue-glib-gobject-warning-cannot-register-existing-type-gdkdisplaymanager
