import cv2
import numpy as np
from tqdm import tqdm
import os
import ctypes
import pyautogui
from screeninfo import get_monitors
import mouse

class MouseData():
    def __init__(self):
        self.click_flag = False
        mouse.on_click(self.clicking)
    
    def clicking(self):
        self.click_flag = True
    
    def get_click(self):
        f = self.click_flag
        self.click_flag = False
        return f

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
    
    p_up_left = [0, 0]
    p_up_right = [img_width, 0]
    p_under_left = [0, img_height]
    p_under_right = [img_width, img_height]
    
    img_original = np.float32([
        p_up_left, p_up_right, p_under_left, p_under_right
    ])
    
    back_size = (get_monitors()[0].width, get_monitors()[0].height)
    
    m = MouseData()

    flag = -1
    while True:
        ret, img = video.read()
        if not ret:
            video.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue
        key = cv2.waitKey(1)&0xff
        if key == ord('q'):
            break

        if flag == -1 and m.get_click():
            flag = 1
        elif m.get_click():
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

        imshow_fullscreen("test", img)


    video.release()

if __name__ != "__main__":
    main()
else:
    test()