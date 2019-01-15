# -*- coding: utf-8 -*-
"""
This module contains the Airtest Core APIs.
"""
import os
import time

from six.moves.urllib.parse import parse_qsl, urlparse
#from airtest.core.cv import Template
#, loop_find, try_log_screen
#from airtest.core.error import TargetNotFoundError
from airtest.core.helper import (G, delay_after_operation, import_device_cls,
                                 logwrap, set_logdir, using, log)
#from airtest.core.settings import Settings as ST
from airtest.utils.transform import TargetPos


"""
Device Setup APIs
"""


def init_device(platform="Android", uuid=None, **kwargs):
    """
    Initialize device if not yet, and set as current device.

    :param platform: Android, IOS or Windows
    :param uuid: uuid for target device, e.g. serialno for Android, handle for Windows, uuid for iOS
    :param kwargs: Optional platform specific keyword args, e.g. `cap_method=JAVACAP` for Android
    :return: device instance
    """
    writeScript("init_device")


def connect_device(uri):
    """
    Initialize device with uri, and set as current device.

    :param uri: an URI where to connect to device, e.g. `android://adbhost:adbport/serialno?param=value&param2=value2`
    :return: device instance
    :Example:
        * ``android:///`` # local adb device using default params
        * ``android://adbhost:adbport/1234566?cap_method=javacap&touch_method=adb``  # remote device using custom params
        * ``windows:///`` # local Windows application
        * ``ios:///`` # iOS device
    """
    d = urlparse(uri)
    platform = d.scheme
    host = d.netloc
    uuid = d.path.lstrip("/")
    params = dict(parse_qsl(d.query))
    if host:
        params["host"] = host.split(":")
    dev = init_device(platform, uuid, **params)
    return dev


def device():
    """
    Return the current active device.

    :return: current device instance
    """
    return G.DEVICE


def set_current(idx):
    """
    Set current active device.

    :param idx: uuid or index of initialized device instance
    :raise IndexError: raised when device idx is not found
    :return: None
    :platforms: Android, iOS, Windows
    """

    dev_dict = {dev.uuid: dev for dev in G.DEVICE_LIST}
    if idx in dev_dict:
        current_dev = dev_dict[idx]
    elif isinstance(idx, int) and idx < len(G.DEVICE_LIST):
        current_dev = G.DEVICE_LIST[idx]
    else:
        raise IndexError("device idx not found in: %s or %s" % (
            list(dev_dict.keys()), list(range(len(G.DEVICE_LIST)))))
    G.DEVICE = current_dev


def auto_setup(basedir=None, devices=None, logdir=None, project_root=None):
    """
    Auto setup running env and try connect android device if not device connected.
    """
    writeScript("auto_setup( '%s')" % basedir)


"""
Device Operations
"""


@logwrap
def shell(cmd):
    """
    Start remote shell in the target device and execute the command

    :param cmd: command to be run on device, e.g. "ls /data/local/tmp"
    :return: the output of the shell cmd
    :platforms: Android
    """
    writeScript("shell( '%s')" % cmd)


@logwrap
def start_app(package, activity=None):
    """
    Start the target application on device

    :param package: name of the package to be started, e.g. "com.netease.my"
    :param activity: the activity to start, default is None which means the main activity
    :return: None
    :platforms: Android, iOS
    """
    writeScript("start_app( '%s','%s')" % package, activity)


@logwrap
def stop_app(package):
    """
    Stop the target application on device

    :param package: name of the package to stop, see also `start_app`
    :return: None
    :platforms: Android, iOS
    """
    writeScript("stop_app( '%s')" % package)


@logwrap
def clear_app(package):
    """
    Clear data of the target application on device

    :param package: name of the package,  see also `start_app`
    :return: None
    :platforms: Android, iOS
    """
    writeScript("clear_app( '%s')" % package)


@logwrap
def install(filepath):
    """
    Install application on device

    :param filepath: the path to file to be installed on target device
    :return: None
    :platforms: Android, iOS
    """
    writeScript("install_app( '%s')" % filepath)


@logwrap
def uninstall(package):
    """
    Uninstall application on device

    :param package: name of the package, see also `start_app`
    :return: None
    :platforms: Android, iOS
    """
    writeScript("install_app( '%s')" % package)


@logwrap
def snapshot(filename=None, msg=""):
    """
    Take the screenshot of the target device and save it to the file.

    :param filename: name of the file where to save the screenshot. If the relative path is provided, the default
                     location is ``ST.LOG_DIR``
    :param msg: short description for screenshot, it will be recorded in the report
    :return: absolute path of the screenshot
    :platforms: Android, iOS, Windows
    """
    writeScript("snapshot( '%s')" % filename)


@logwrap
def wake():
    """
    Wake up and unlock the target device

    :return: None
    :platforms: Android, iOS

    .. note:: Might not work on some models
    """
    writeScript("wake( )" )


@logwrap
def home():
    """
    Return to the home screen of the target device.

    :return: None
    :platforms: Android, iOS
    """
    writeScript("home( )" )


@logwrap
def touch(v, times=1, **kwargs):
    """
    Perform the touch action on the device screen

    :param v: target to touch, either a Template instance or absolute coordinates (x, y)
    :param times: how many touches to be performed
    :param kwargs: platform specific `kwargs`, please refer to corresponding docs
    :return: finial position to be clicked
    :platforms: Android, Windows, iOS
    """
    record_x, record_y = v.record_pos
    res_x, res_y = v.resolution
    writeScript("touch({filename='%s',threshold=%f, target_pos=%d,rgb=%s,record_pos={%f,%f),resolution={%d,%d}},%d)" % v.filename,v.threshold,v.target_pos,v.rgb,record_x,record_y,res_x,res_y,times)

click = touch  # click is alias of touch


@logwrap
def double_click(v):
    writeScript("double_click({filename='%s',threshold=%f, target_pos=%d,rgb=%s,record_pos={%f,%f),resolution={%d,%d}})" % v.filename,v.threshold,v.target_pos,v.rgb,record_x,record_y,res_x,res_y)



@logwrap
def swipe(v1, v2=None, vector=None, **kwargs):
    """
    Perform the swipe action on the device screen.

    There are two ways of assigning the parameters
        * ``swipe(v1, v2=Template(...))``   # swipe from v1 to v2
        * ``swipe(v1, vector=(x, y))``      # swipe starts at v1 and moves along the vector.


    :param v1: the start point of swipe,
               either a Template instance or absolute coordinates (x, y)
    :param v2: the end point of swipe,
               either a Template instance or absolute coordinates (x, y)
    :param vector: a vector coordinates of swipe action, either absolute coordinates (x, y) or percentage of
                   screen e.g.(0.5, 0.5)
    :param **kwargs: platform specific `kwargs`, please refer to corresponding docs
    :raise Exception: general exception when not enough parameters to perform swap action have been provided
    :return: Origin position and target position
    :platforms: Android, Windows, iOS
    """
    v_x,v_y=vector
    writeScript("swipe({filename='%s',threshold=%f, target_pos=%d,rgb=%s,record_pos={%f,%f),resolution={%d,%d}},{%f,%f})" % v.filename,v.threshold,v.target_pos,v.rgb,record_x,record_y,res_x,res_y,v_x,v_y)



@logwrap
def pinch(in_or_out='in', center=None, percent=0.5):
    """
    Perform the pinch action on the device screen

    :param in_or_out: pinch in or pinch out, enum in ["in", "out"]
    :param center: center of pinch action, default as None which is the center of the screen
    :param percent: percentage of the screen of pinch action, default is 0.5
    :return: None
    :platforms: Android
    """


@logwrap
def keyevent(keyname, **kwargs):
    """
    Perform key event on the device

    :param keyname: platform specific key name
    :param **kwargs: platform specific `kwargs`, please refer to corresponding docs
    :return: None
    :platforms: Android, Windows, iOS
    """
    writeScript("keyevent('%s')" % keyname)


@logwrap
def text(text, enter=True):
    """
    Input text on the target device. Text input widget must be active first.

    :param text: text to input, unicode is supported
    :param enter: input `Enter` keyevent after text input, default is True
    :return: None
    :platforms: Android, Windows, iOS
    """
    writeScript("text('%s')" % text)


@logwrap
def sleep(secs=1.0):
    """
    Set the sleep interval. It will be recorded in the report

    :param secs: seconds to sleep
    :return: None
    :platforms: Android, Windows, iOS
    """
    writeScript("msleep(%d)" % secs*1000)


@logwrap
def wait(v, timeout=None, interval=0.5, intervalfunc=None):
    """
    Wait to match the Template on the device screen

    :param v: target object to wait for, Template instance
    :param timeout: time interval to wait for the match, default is None which is ``ST.FIND_TIMEOUT``
    :param interval: time interval in seconds to attempt to find a match
    :param intervalfunc: called after each unsuccessful attempt to find the corresponding match
    :raise TargetNotFoundError: raised if target is not found after the time limit expired
    :return: coordinates of the matched target
    :platforms: Android, Windows, iOS
    """
    timeout = timeout or ST.FIND_TIMEOUT
    writeScript("wait({filename='%s',threshold=%f, target_pos=%d,rgb=%s,record_pos={%f,%f),resolution={%d,%d}},%d,%d)" % v.filename,v.threshold,v.target_pos,v.rgb,record_x,record_y,res_x,res_y,timeout*1000,interval*1000)



@logwrap
def exists(v):
    """
    Check whether given target exists on device screen

    :param v: target to be checked
    :return: False if target is not found, otherwise returns the coordinates of the target
    :platforms: Android, Windows, iOS
    """
    writeScript("exists({filename='%s',threshold=%f, target_pos=%d,rgb=%s,record_pos={%f,%f),resolution={%d,%d}},%d)" % v.filename,v.threshold,v.target_pos,v.rgb,record_x,record_y,res_x,res_y,ST.FIND_TIMEOUT_TMP*1000)



@logwrap
def find_all(v):
    """
    Find all occurrences of the target on the device screen and return their coordinates

    :param v: target to find
    :return: list of coordinates, [(x, y), (x1, y1), ...]
    :platforms: Android, Windows, iOS
    """
    writeScript("find_all({filename='%s',threshold=%f, target_pos=%d,rgb=%s,record_pos={%f,%f),resolution={%d,%d}})" % v.filename,v.threshold,v.target_pos,v.rgb,record_x,record_y,res_x,res_y)



"""
Assertions
"""


@logwrap
def assert_exists(v, msg=""):
    """
    Assert target exists on device screen

    :param v: target to be checked
    :param msg: short description of assertion, it will be recorded in the report
    :raise AssertionError: if assertion fails
    :return: coordinates of the target
    :platforms: Android, Windows, iOS
    """
    writeScript("assert_exists({filename='%s',threshold=%f, target_pos=%d,rgb=%s,record_pos={%f,%f),resolution={%d,%d}},%d,%s)" % v.filename,v.threshold,v.target_pos,v.rgb,record_x,record_y,res_x,res_y,ST.FIND_TIMEOUT_TMP*1000,msg)



@logwrap
def assert_not_exists(v, msg=""):
    """
    Assert target does not exist on device screen

    :param v: target to be checked
    :param msg: short description of assertion, it will be recorded in the report
    :raise AssertionError: if assertion fails
    :return: None.
    :platforms: Android, Windows, iOS
    """
    writeScript("assert_not_exists({filename='%s',threshold=%f, target_pos=%d,rgb=%s,record_pos={%f,%f),resolution={%d,%d}},%d,%s)" % v.filename,v.threshold,v.target_pos,v.rgb,record_x,record_y,res_x,res_y,ST.FIND_TIMEOUT_TMP*1000,msg)



@logwrap
def assert_equal(first, second, msg=""):
    """
    Assert two values are equal

    :param first: first value
    :param second: second value
    :param msg: short description of assertion, it will be recorded in the report
    :raise AssertionError: if assertion fails
    :return: None
    :platforms: Android, Windows, iOS
    """


@logwrap
def assert_not_equal(first, second, msg=""):
    """
    Assert two values are not equal

    :param first: first value
    :param second: second value
    :param msg: short description of assertion, it will be recorded in the report
    :raise AssertionError: if assertion
    :return: None
    :platforms: Android, Windows, iOS
    """


def writeScript(str):
        print(str)

class Template(object):
    """
    picture as touch/swipe/wait/exists target and extra info for cv match
    filename: pic filename
    target_pos: ret which pos in the pic
    record_pos: pos in screen when recording
    resolution: screen resolution when recording
    rgb: 识别结果是否使用rgb三通道进行校验.
    """

    def __init__(self, filename, threshold=None, target_pos=TargetPos.MID, record_pos=None, resolution=(), rgb=False):
        self.filename = filename
        self._filepath = None
        self.threshold = threshold or ST.THRESHOLD
        self.target_pos = target_pos
        self.record_pos = record_pos
        self.resolution = resolution
        self.rgb = rgb

