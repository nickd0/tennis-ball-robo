# python colortrace.py  -l 13,0,0 -u 255,102,255 -i /Users/nick/Downloads/1AB-1562961740.jpg
# python colortrace.y -l 0,0,0 -u 255,106,255
from imutils.video import VideoStream
import numpy as np
import argparse
import cv2
import time
import random


def process(frame, _hsvlow, _hsvhigh, vs=None):
    if frame is None:
        return (False, None, None)

    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    # construct a mask for the tennis ball color, then perform
    # a series of dilations and erosions to remove any small
    # blobs left in the mask
    mask = cv2.inRange(hsv, _hsvlow, _hsvhigh)

    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)
    cv2.imshow("mask", mask)

    ## NEW 1/28/21 ##

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    rect = None
    for i, c in enumerate(contours):
        # cv2.drawContours(frame, contours, i, (255, 255, 0), 3)
        rect = cv2.boundingRect(c)
        x, y, w, h = rect
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 0), 5)
        break

    if rect:
        cropped = crop_rect(frame, rect)
        cv2.namedWindow('Ball view', cv2.WINDOW_KEEPRATIO)
        cv2.imshow('Ball view', cropped)
        cv2.resizeWindow('Ball view', (200, 200))

    cv2.putText(frame, '{} ball detected'.format(len(contours)), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255))

    return (True, frame, len(contours))

def crop_rect(img, rect):
    x, y, w, h = rect
    _img = img.copy()
    _img = _img[y:y + h, x:x + h]
    return _img

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("-v", "--video",
            help="path to the (optional) video file")
    ap.add_argument("-i", "--image",
            help="path to the (optional) image file")
    ap.add_argument("-w", "--webcam", dest='webcam', action='store_true',
            help="path to the (optional) image file")
    ap.add_argument("-l", "--hsvlow", type=str,
            help="HSV low values")
    ap.add_argument("-u", "--hsvhigh", type=str,
            help="HSV high values")
    ap.add_argument("--save", type=str,
            help="Save output")
    ap.add_argument("--print", dest='webcam', action='store_true',
            help="Print info on image")
    args = vars(ap.parse_args())

    hsvlow = (35, 0, 0)
    hsvhigh = (204, 109, 255)

    counter = 0

    if args.get("hsvlow", False):
        hsvlow = tuple([int(n) for n in args.get("hsvlow").split(',')])

    if args.get("hsvhigh", False):
        hsvhigh = tuple([int(n) for n in args.get("hsvhigh").split(',')])

    while 1:
        if counter > 0 and args.get("image", False):
            pass
        else:
            if args.get("image", False):
                frame = cv2.imread(args.get("image"))

            elif args.get("webcam", False):
                cam = cv2.VideoCapture(0)
                _, frame = cam.read()

            (ret, frameout, num) = process(frame, hsvlow, hsvhigh)
            if args.get("save", False) and args.get("image", False):
                out = args.get('save')
                base, ext = out.split('.')
                cv2.imwrite(out, frameout)
                # cv2.imwrite(base + '-MASKED.' + ext, masked)
                print(num)
                break
            else:
                cv2.imshow("Frame", frameout)

            counter += 1

        # if the 'q' key is pressed, stop the loop
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break

    if args.get("image", False): pass
    elif args.get("webcam", False):
        cam.release()
    elif args.get("video", False):
        cam.stop()

    cv2.destroyAllWindows()
