# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""[summary] 模板匹配对用户提供的调节参数:

[description]
    1. threshod: 筛选阈值，默认为0.8
    2. rgb: 彩色三通道,进行彩色权识别.
"""

import cv2
from utils import generate_result, check_source_larger_than_search, img_mat_rgb_2_gray
from cal_confidence import cal_rgb_confidence
from predict import Predictor
from copy import deepcopy
from utils import crop_image, generate_result, get_resolution

def find_template_in_predict_area(img_source, img_search, record_pos,resolution, threshold=0.8, rgb=False):
        if not record_pos:
            return None
        # calc predict area in screen
        image_wh, screen_resolution = get_resolution(img_search), get_resolution(img_source)
        print(image_wh)
        print(screen_resolution)
        xmin, ymin, xmax, ymax = Predictor.get_predict_area(record_pos, image_wh, resolution, screen_resolution)
        screen_w,screen_h=screen_resolution
        xmin,ymin,xmax,ymax=(int(round(xmin if xmin>0 else 0)),int(round(ymin if ymin>0 else 0)),int(round(xmax if xmax<screen_h else screen_h)),int(round(ymax if ymax<screen_h else screen_h)))
        print((xmin,ymin,xmax,ymax))
        # crop predict image from screen
        predict_area = crop_image(img_source, (xmin, ymin, xmax, ymax))
        if not predict_area.any():
            return None
        # find sift in that image
        ret_in_area = find_template(predict_area, img_search, threshold=threshold, rgb=rgb)
        # calc cv ret if found
        if not ret_in_area:
            return None
        ret = deepcopy(ret_in_area)
        if "rectangle" in ret:
            for idx, item in enumerate(ret["rectangle"]):
                ret["rectangle"][idx] = (item[0] + xmin, item[1] + ymin)
        ret["result"] = (ret_in_area["result"][0] + xmin, ret_in_area["result"][1] + ymin)
        return ret


def find_template(im_source, im_search, threshold=0.8, rgb=False):
    """函数功能：找到最优结果."""
    # 第一步：校验图像输入
    check_source_larger_than_search(im_source, im_search)
    # 第二步：计算模板匹配的结果矩阵res
    res = _get_template_result_matrix(im_source, im_search)
    # 第三步：依次获取匹配结果
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    h, w = im_search.shape[:2]
    # 求取可信度:
    confidence = _get_confidence_from_matrix(im_source, im_search, max_loc, max_val, w, h, rgb)
    # 求取识别位置: 目标中心 + 目标区域:
    middle_point, rectangle = _get_target_rectangle(max_loc, w, h)
    best_match = generate_result(middle_point, rectangle, confidence)
    return best_match if confidence >= threshold else None


def find_all_template(im_source, im_search, threshold=0.8, rgb=False, max_count=10):
    """根据输入图片和参数设置,返回所有的图像识别结果."""
    # 第一步：校验图像输入
    check_source_larger_than_search(im_source, im_search)

    # 第二步：计算模板匹配的结果矩阵res
    res = _get_template_result_matrix(im_source, im_search)

    # 第三步：依次获取匹配结果
    result = []
    h, w = im_search.shape[:2]

    while True:
        # 本次循环中,取出当前结果矩阵中的最优值
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        # 求取可信度:
        confidence = _get_confidence_from_matrix(im_source, im_search, max_loc, max_val, w, h, rgb)

        if confidence < threshold or len(result) > max_count:
            break

        # 求取识别位置: 目标中心 + 目标区域:
        middle_point, rectangle = _get_target_rectangle(max_loc, w, h)
        one_good_match = generate_result(middle_point, rectangle, confidence)

        result.append(one_good_match)

        # 屏蔽已经取出的最优结果,进入下轮循环继续寻找:
        # cv2.floodFill(res, None, max_loc, (-1000,), max(max_val, 0), flags=cv2.FLOODFILL_FIXED_RANGE)
        cv2.rectangle(res, (int(max_loc[0] - w / 2), int(max_loc[1] - h / 2)), (int(max_loc[0] + w / 2), int(max_loc[1] + h / 2)), (0, 0, 0), -1)

    return result if result else None


def _get_confidence_from_matrix(im_source, im_search, max_loc, max_val, w, h, rgb):
    """根据结果矩阵求出confidence."""
    # 求取可信度:
    if rgb:
        # 如果有颜色校验,对目标区域进行BGR三通道校验:
        img_crop = im_source[max_loc[1]:max_loc[1] + h, max_loc[0]: max_loc[0] + w]
        confidence = cal_rgb_confidence(img_crop, im_search)
    else:
        confidence = max_val

    return confidence


def _get_template_result_matrix(im_source, im_search):
    """求取模板匹配的结果矩阵."""
    # 灰度识别: cv2.matchTemplate( )只能处理灰度图片参数
    s_gray, i_gray = img_mat_rgb_2_gray(im_search), img_mat_rgb_2_gray(im_source)
    return cv2.matchTemplate(i_gray, s_gray, cv2.TM_CCOEFF_NORMED)


def _get_target_rectangle(left_top_pos, w, h):
    """根据左上角点和宽高求出目标区域."""
    x_min, y_min = left_top_pos
    # 中心位置的坐标:
    x_middle, y_middle = int(x_min + w / 2), int(y_min + h / 2)
    # 左下(min,max)->右下(max,max)->右上(max,min)
    left_bottom_pos, right_bottom_pos = (x_min, y_min + h), (x_min + w, y_min + h)
    right_top_pos = (x_min + w, y_min)
    # 点击位置:
    middle_point = (x_middle, y_middle)
    # 识别目标区域: 点序:左上->左下->右下->右上, 左上(min,min)右下(max,max)
    rectangle = [left_top_pos, left_bottom_pos, right_bottom_pos, right_top_pos]

    return middle_point, rectangle
