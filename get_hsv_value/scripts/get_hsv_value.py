from time import sleep
from math import sqrt
import cv2 as cv
import os
import sys
import json
import numpy as np
import argparse

# TODO:
# Construct the argument parser and parse the arguments
# get the hsv value from the camera
# get the hsv value from the video
# get hsv value with with circle cropped img and mouse callback
#

parser = argparse.ArgumentParser(add_help=True)
parser.add_argument("image_path", nargs='?',
                    help="path to the image")
parser.add_argument("-v", "--video", help="path to the video file")
parser.add_argument("-c", "--camera", help="camera index, default=0",
                    action="store", default=0, type=int)
parser.add_argument("-s", "--save", help="save the file to the specified path")
parser.add_argument(
    "-f", "--file", help="path to the file to be opened, default is the current directory", action="store", default=sys.path[0], type=str)
parser.add_argument("-b", "--bbox", help="initial bounding box")
parser.add_argument("--verbose", help="enable verbose mode",
                    action="store_true")
parser.add_argument("--radius", help="radius of the sample circle, default = 5",
                    action="store", default=5, type=int)
args = parser.parse_args()

# parser.print_help()
if args.verbose:
    print("verbose mode is on")
    print("path to the image:", args.image_path)
    print("video: ", args.video)
    print("camera: ", args.camera)
    print("save: ", args.save)
    print("file: ", args.file)
    print("bbox: ", args.bbox)


class GetColor:
    use_vid = False
    use_cam = False
    _delay = 1

    def __init__(self):
        global args
        self.args = args
        self.verbose = args.verbose
        if args.image_path is not None:
            os.chdir(sys.path[0])
            print("cwd : ", os.getcwd())
            print("image path : ", args.image_path)
            self.img = cv.imread(args.image_path)
            cv.imshow("img", self.img)
            cv.waitKey(500)

        elif args.video:
            self.use_vid = True
            self.cap = cv.VideoCapture(args.video)
            fps = self.cap.get(cv.CAP_PROP_FPS)
            self._delay = int(1000 / fps)
            if args.verbose:
                print("video : ",  args.video)
                print("video fps : ", fps)
            ret, self.img = self.cap.read()
            while not ret:
                print("ret : ", ret)
                ret, self.img = self.cap.read()
                sleep(0.5)
                print("waiting for camera")

        else:
            self.use_cam = True
            self.cap = cv.VideoCapture(args.camera)
            _, self.img = self.cap.read()
        # ret, self.img = self.cap.read()
        self.sample_range = args.radius
        # x,y = 3,2
        # [[[B, G, R], [B, G, R], []]
        #  [[B, G, R], [],        []]]
        # this colour range should sample colour 20x20 at least

        # self.color_range = []
        # for i in range(self.sample_range**2):
        #     self.color_range.append([])
        # self.counter = 0
        # self.samples = []
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
        if '.json' in self.args.file:
            lists = self.args.file.split('/')
            path = '/'.join(lists[:-1]) + '/'
        elif self.args.file[-1] != '/':
            path = self.args.file + '/'
        else:
            path = self.args.file

        with open(path+"color.json", "r") as f:
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

            # B, G, R = self.img[y, x]
            # H, S, V = self.hsv[y, x]
            # print("B : ", B, "G : ", G, "R : ", R)
            # print("H : ", H, "S : ", S, "V : ", V)
            # cv.setTrackbarPos("b upper", "hsv", H + 10 if H < 245 else 255)
            # cv.setTrackbarPos("g upper", "hsv", S + 10 if S < 245 else 255)
            # cv.setTrackbarPos("r upper", "hsv", V + 10 if V < 245 else 255)
            # cv.setTrackbarPos("b", "hsv", H - 10 if H > 10 else 0)
            # cv.setTrackbarPos("g", "hsv", S - 10 if S > 10 else 0)
            # cv.setTrackbarPos("r", "hsv", V - 10 if V > 10 else 0)

            red, green, blue, hue, saturation, value = [], [], [], [], [], []
            rad = self.sample_range
            for i in range(x-rad, x+rad):
                for j in range(y-rad, y+rad):
                    result = sqrt(abs(i-x)**2+abs(j-y)**2)
                    # if self.verbose:
                    #     print("i: {} j: {} res: {}".format(i, j, result))
                    if(result <= rad):
                        blue.append(self.img[j, i][0])
                        green.append(self.img[j, i][1])
                        red.append(self.img[j, i][2])
                        hue.append(self.hsv[j, i][0])
                        saturation.append(self.hsv[j, i][1])
                        value.append(self.hsv[j, i][2])
            if self.verbose:
                print("left button up")
                print("x : ", x, "y : ", y)
                # print("blue : ", blue)
                # print("green : ", green)
                # print("red : ", red)
            B_low, B_up = np.percentile(blue, [1, 99])
            G_low, G_up = np.percentile(green, [1, 99])
            R_low, R_up = np.percentile(red, [1, 99])
            H_low, H_up = np.percentile(hue, [1, 99])
            S_low, S_up = np.percentile(saturation, [1, 99])
            V_low, V_up = np.percentile(value, [1, 99])
            if self.verbose:
                print("B_low : ", B_low, "G_low : ", G_low, "R_low : ", R_low)
                print("B_up : ", B_up, "G_up : ", G_up, "R_up : ", R_up)
                print("H_low : ", H_low, "S_low : ", S_low, "V_low : ", V_low)
                print("H_up : ", H_up, "S_up : ", S_up, "V_up : ", V_up)

            cv.setTrackbarPos("b upper", "hsv", int(H_up))
            cv.setTrackbarPos("g upper", "hsv", int(S_up))
            cv.setTrackbarPos("r upper", "hsv", int(V_up))
            cv.setTrackbarPos("b", "hsv", int(H_low))
            cv.setTrackbarPos("g", "hsv", int(S_low))
            cv.setTrackbarPos("r", "hsv", int(V_low))

            # self.counter += 1
            # self.samples.append(self.color_range)
            # self.show_sample(self.counter - 1)
            # except:
            # print("gagal mengambil sampel warna")

    # def show_sample(self, i):
    #     cv.imshow("sample", self.samples[i])
    #     key = cv.waitKey(0)

    def get_color_from_ROI(self, bbox):
        x, y, w, h = bbox
        print("bbox : ", bbox)
        red, green, blue, hue, saturation, value = [], [], [], [], [], []
        for i in range(x, x + w):
            for j in range(y, y + h):
                blue.append(self.img[j, i][0])
                green.append(self.img[j, i][1])
                red.append(self.img[j, i][2])
                hue.append(self.hsv[j, i][0])
                saturation.append(self.hsv[j, i][1])
                value.append(self.hsv[j, i][2])

        B_low, B_up = np.percentile(blue, [1, 99])
        G_low, G_up = np.percentile(green, [1, 99])
        R_low, R_up = np.percentile(red, [1, 99])
        H_low, H_up = np.percentile(hue, [1, 99])
        S_low, S_up = np.percentile(saturation, [1, 99])
        V_low, V_up = np.percentile(value, [1, 99])

        print("B_low : ", B_low, "G_low : ", G_low, "R_low : ", R_low)
        print("B_up : ", B_up, "G_up : ", G_up, "R_up : ", R_up)
        print("H_low : ", H_low, "S_low : ", S_low, "V_low : ", V_low)
        print("H_up : ", H_up, "S_up : ", S_up, "V_up : ", V_up)

        cv.setTrackbarPos("b upper", "hsv", int(H_up))
        cv.setTrackbarPos("g upper", "hsv", int(S_up))
        cv.setTrackbarPos("r upper", "hsv", int(V_up))
        cv.setTrackbarPos("b", "hsv", int(H_low))
        cv.setTrackbarPos("g", "hsv", int(S_low))
        cv.setTrackbarPos("r", "hsv", int(V_low))

    def main(self):
        while True:
            if self.use_cam:
                _, self.img = self.cap.read()
            elif self.use_vid:
                ret, self.img = self.cap.read()
                if not ret:
                    self.cap.set(cv.CAP_PROP_POS_FRAMES, 0)
                    continue
            self.hsv = cv.cvtColor(self.img, cv.COLOR_BGR2HSV)
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
            timer = cv.getTickCount()
            fps = cv.getTickFrequency() / (cv.getTickCount() - timer)
            cv.putText(res, "FPS : " + str(int(fps)/1000), (10, 30),
                       cv.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)
            # print(mask)
            # print(type(mask))
            cv.imshow("img", self.img)
            cv.imshow("hsv", self.hsv)
            cv.imshow("mask", mask)
            cv.imshow("obj", res)

            key = cv.waitKey(self._delay) & 0xFF
            if key == ord("x"):
                print("x pressed, quiting ...")
                break
            elif key == ord('r'):
                print("r pressed, opening ROI selector ...")
                bbox = cv.selectROI(self.img, False)
                print("bbox : ", bbox)
                self.get_color_from_ROI(bbox)

            elif key == ord("s"):
                path = ""
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
                if self.args.save is not None:
                    path = self.args.save
                save_dict = {color_name: color_dict}
                if os.path.exists(path+"color.json"):
                    with open("color.json", "r+") as f:
                        dict_ = json.load(f)
                        dict_.update(save_dict)
                        f.seek(0)
                        json.dump(dict_, f, indent=4)
                else:
                    with open(path+"color.json", "w") as f:
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
