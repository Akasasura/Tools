import cv2 as cv
import os
import sys
import json
import numpy as np


class GetColor:
    def __init__(self, path="../img/test.png"):

        os.chdir(sys.path[0])
        print("cwd : ", os.getcwd())
        self.sample_range = 20
        self.img = cv.imread(path)
        self.hsv = cv.cvtColor(self.img, cv.COLOR_BGR2HSV)
        # x,y = 3,2
        # [[[B, G, R], [B, G, R], []]
        #  [[B, G, R], [],        []]]
        # this colour range should sample colour 20x20 at least
        self.color_range = []
        for i in range(self.sample_range**2):
            self.color_range.append([])
        self.counter = 0
        self.samples = []
        cv.namedWindow("img")
        cv.namedWindow("hsv")
        cv.setMouseCallback("img", self.mouse_callback)
        # create trackbar

        cv.createTrackbar("b", "hsv", 0, 255, self.on_change)
        cv.createTrackbar("g", "hsv", 0, 255, self.on_change)
        cv.createTrackbar("r", "hsv", 0, 255, self.on_change)
        cv.createTrackbar("b upper", "hsv", 0, 255, self.on_change)
        cv.createTrackbar("g upper", "hsv", 0, 255, self.on_change)
        cv.createTrackbar("r upper", "hsv", 0, 255, self.on_change)

    def load_Obj(self):
        with open("color.json", "r") as f:
            obj_dict = json.load(f)
        print("no   object")
        for i, obj in enumerate(obj_dict):
            print("{}   {}".format(i, obj))
        val = input("select object (name)")
        lower = obj_dict[val]["low"]
        upper = obj_dict[val]["up"]
        return lower, upper

    def on_change(self, val):
        print("val : ", val)

    def mouse_callback(self, event, x, y, *args):

        if cv.EVENT_LBUTTONUP == event:
            print("left button up")
            print("x : ", x, "y : ", y)
            B, G, R = self.img[y, x]
            H, S, V = self.hsv[y, x]
            print("B : ", B, "G : ", G, "R : ", R)
            print("H : ", H, "S : ", S, "V : ", V)
            cv.setTrackbarPos("b upper", "hsv", H + 10 if H < 245 else 255)
            cv.setTrackbarPos("g upper", "hsv", S + 10 if S < 245 else 255)
            cv.setTrackbarPos("r upper", "hsv", V + 10 if V < 245 else 255)
            cv.setTrackbarPos("b", "hsv", H - 10 if H > 10 else 0)
            cv.setTrackbarPos("g", "hsv", S - 10 if S > 10 else 0)
            cv.setTrackbarPos("r", "hsv", V - 10 if V > 10 else 0)

            # try:
            # for i in range(self.sample_range):
            #     for j in range(self.sample_range):
            #         self.color_range[i, j] = self.img[
            #             x - self.sample_range // 2 + i, x - self.sample_range // 2 + j
            #         ]
            # self.counter += 1
            # self.samples.append(self.color_range)
            # self.show_sample(self.counter - 1)
            # except:
            # print("gagal mengambil sampel warna")

    def show_sample(self, i):
        cv.imshow("sample", self.samples[i])
        key = cv.waitKey(0)

    def main(self):
        while True:
            # update slider
            b_low = cv.getTrackbarPos("b", "hsv")
            g_low = cv.getTrackbarPos("g", "hsv")
            r_low = cv.getTrackbarPos("r", "hsv")
            b_up = cv.getTrackbarPos("b upper", "hsv")
            g_up = cv.getTrackbarPos("g upper", "hsv")
            r_up = cv.getTrackbarPos("r upper", "hsv")
            lower_range = np.array([b_low, g_low, r_low])
            upper_range = np.array([b_up, g_up, r_up])
            mask = cv.inRange(self.hsv, lower_range, upper_range)
            mask2 = mask.copy()
            element = cv.getStructuringElement(cv.MORPH_RECT, (3, 3))
            mask2 = cv.erode(mask2, element, iterations=1)
            mask2 = cv.dilate(mask2, element, iterations=1)
            mask2 = cv.erode(mask2, element)
            res = cv.bitwise_and(self.img, self.img, mask=mask2)
            # print(mask)
            # print(type(mask))
            cv.imshow("img", self.img)
            cv.imshow("hsv", self.hsv)
            cv.imshow("mask", mask)
            cv.imshow("obj", res)

            key = cv.waitKey(1) & 0xFF
            if key == ord("x"):
                print("x pressed, quiting ...")
                break
            elif key == ord("s"):
                print("saving color")
                color_name = input("input color name : ")
                color_dict = {
                    "low": [
                        b_low,
                        g_low,
                        r_low,
                    ],
                    "up": [b_up, g_up, r_up],
                }
                save_dict = {color_name: color_dict}
                if os.path.exists("color.json"):
                    with open("color.json", "r+") as f:
                        dict_ = json.load(f)
                        dict_.update(save_dict)
                        f.seek(0)
                        json.dump(dict_, f, indent=4)
                else:
                    with open("color.json", "w") as f:
                        json.dump(save_dict, f, indent=4)
                print("finish saving color")
            elif key == ord("o"):
                print("load obj")
                lower, upper = self.load_Obj()
                cv.setTrackbarPos("b", "hsv", lower[0])
                cv.setTrackbarPos("g", "hsv", lower[1])
                cv.setTrackbarPos("r", "hsv", lower[2])
                cv.setTrackbarPos("b upper", "hsv", upper[0])
                cv.setTrackbarPos("g upper", "hsv", upper[1])
                cv.setTrackbarPos("r upper", "hsv", upper[2])
        self.exit_()

    def exit_(self):
        print("exit")
        cv.destroyAllWindows()
        exit()


if __name__ == "__main__":
    c = GetColor()
    try:
        c.main()
    except KeyboardInterrupt:
        c.exit_()
