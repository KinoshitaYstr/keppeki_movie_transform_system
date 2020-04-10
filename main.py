import cv2
import numpy as np
from tqdm import tqdm
import os
import ctypes

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
    while True:
        ret, img = video.read()
        if not ret:
            break
        imshow_fullscreen("test", img)
        key = cv2.waitKey(1)&0xff
    video.release()

if __name__ != "__main__":
    main()
else:
    test()