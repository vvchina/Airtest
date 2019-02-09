#!/usr/bin/env python
# -*- coding: utf-8 -*-

from template import find_template
import cv2

def image_show(img) :
    cv2.imshow("image", img)
    cv2.waitKey(0) 
    return

if __name__ == '__main__':
    res=find_template(cv2.imread("test.jpg"),cv2.imread("test1.jpg"))
    print(res)
    img=cv2.imread("test.jpg")
    cv2.rectangle(img, res['rectangle'][0], res['rectangle'][2], (0, 255, 0), 2)
    image_show(img)


