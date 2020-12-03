# システム関係
import os
import sys
# 音声関係いじるもの
import moviepy.editor as mp

def main():
    # コマンドライン引数
    args = sys.argv
    # 付与先
    input_fname = args[1]
    if not os.path.exists(input_fname):
        print("ファイルが存在しません")
        return
    # 元の映像
    original_fname = args[2]
    if not os.path.exists(original_fname):
        print("ファイルが存在しません")
        return
    
    set_sound(input_fname, original_fname)


def set_sound(input_fname, original_fname):
    print("set_sound")
    # ダブりが大変だから一度名前変更
    os.rename(input_fname, ".tmp.mp4")

    # 音声抽出
    original_sound = mp.VideoFileClip(original_fname).subclip()
    original_sound.audio.write_audiofile(".tmp.mp3")
    
    # 音声付与
    output = mp.VideoFileClip(".tmp.mp4").subclip()
    output.write_videofile(input_fname, audio=".tmp.mp3")

    # 不要なもの消す
    os.remove(".tmp.mp3")
    os.remove(".tmp.mp4")

if __name__ == "__main__":
    main()