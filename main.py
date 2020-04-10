import cv2
import numpy as np
from tqdm import tqdm
import os
import ctypes
import pyautogui
from screeninfo import get_monitors

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
    pass

def test():
    name = "a.mp4"
    video = cv2.VideoCapture(name)
    img_width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    img_height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    img_original = np.float32([
        [0, 0],
        [img_width, 0],
        [0, img_height],
        [img_width, img_height]
    ])
    back_size = (get_monitors()[0].width, get_monitors()[0].height)
    while True:
        ret, img = video.read()
        if not ret:
            video.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue
        key = cv2.waitKey(1)&0xff
        if key == ord('q'):
            break
        get_p = pyautogui.position()

        img_trans = np.float32([
            [0, 0],
            [img_width, 0],
            [0, img_height],
            #[img_width, img_height]
            get_p
        ])
        matrix = cv2.getPerspectiveTransform(img_original, img_trans)
        img = cv2.warpPerspective(img, matrix, back_size)

        imshow_fullscreen("test", img)


    video.release()

if __name__ != "__main__":
    main()
else:
    test()