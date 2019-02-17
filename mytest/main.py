#!/usr/bin/env python
# -*- coding: utf-8 -*-

from template import find_template
from sift import find_sift,find_sift_in_predict_area
import cv2

def image_show(img) :
    cv2.imshow("image", img)
    cv2.waitKey(0) 
    return

if __name__ == '__main__':
    method="sift"
    if method == "tpl":      
        res=find_template(cv2.imread("test.jpg"),cv2.imread("test1.jpg"))
        print(res)
        img=cv2.imread("test.jpg")
        cv2.rectangle(img, res['rectangle'][0], res['rectangle'][2], (0, 255, 0), 2)
        image_show(img)
    elif method == "sift":
        res=find_sift_in_predict_area(cv2.imread("test.jpg"),cv2.imread("test1.jpg"),(0.046,-0.041),(194,310))
        #res=find_sift(cv2.imread("test.jpg"),cv2.imread("test1.jpg"))
        print(res)
        img=cv2.imread("test.jpg")
        cv2.rectangle(img, res['rectangle'][0], res['rectangle'][2], (0, 255, 0), 2)
        image_show(img)


