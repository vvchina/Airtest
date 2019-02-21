#!/usr/bin/env python
# -*- coding: utf-8 -*-

from template import find_template,find_template_in_predict_area
from sift import find_sift,find_sift_in_predict_area
import cv2

def image_show(img) :
    cv2.imshow("image", img)
    cv2.waitKey(0) 
    return

if __name__ == '__main__':
    method="pre_tpl"
    res=None
    if method == "tpl":      
        res=find_template(cv2.imread("test.jpg"),cv2.imread("test1.jpg"))
    elif method == "pre_tpl":
        res=find_template_in_predict_area(cv2.imread("test.jpg"),cv2.imread("test1.jpg"),(0.046,-0.041),(194,310))
    elif method == "pre_sift":
        res=find_sift_in_predict_area(cv2.imread("test.jpg"),cv2.imread("test1.jpg"),(0.046,-0.041),(194,310))
    elif method == "sift":
        res=find_sift(cv2.imread("test.jpg"),cv2.imread("test1.jpg"))

    print(res)
    #show="show"
    show=None

    if show != None:
        img=cv2.imread("test.jpg")
        cv2.rectangle(img, res['rectangle'][0], res['rectangle'][2], (0, 255, 0), 2)
        image_show(img)

