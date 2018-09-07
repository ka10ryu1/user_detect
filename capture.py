#!/usr/bin/env python3
# -*-coding: utf-8 -*-
#
help = 'Webカメラから画像を取得する'
#

import logging
# basicConfig()は、 debug()やinfo()を最初に呼び出す"前"に呼び出すこと
level = logging.INFO
logging.basicConfig(format='%(message)s')
logging.getLogger('Tools').setLevel(level=level)

import cv2
import time
import argparse
import numpy as np

import Tools.func as F
from Lib.video import videoCap
from Lib.hc_sr04 import objectDetect


def command():
    parser = argparse.ArgumentParser(description=help)
    parser.add_argument('-c', '--channel', type=int, default=0,
                        help='使用するWebカメラのチャンネル [default: 0]')
    parser.add_argument('-o', '--out_path', default='./data/',
                        help='画像の保存先 (default: ./data/)')
    parser.add_argument('-i', '--interval_time', type=float, default=0.25,
                        help='インターバル撮影の間隔 [default: 0.25]')
    parser.add_argument('-s', '--stock_num', type=int, default=10,
                        help='インターバル撮影の画像保持数 [default: 10]')
    parser.add_argument('-d', '--diff_val', type=int, default=80,
                        help='超音波センサの判定差分値 [default: 80]')
    parser.add_argument('-p', '--serial_port',  default='/dev/ttyACM0',
                        help='使用するシリアルポート（$ dmesg | grep ttyACM0）')
    parser.add_argument('--lower', action='store_true',
                        help='select timeoutが発生する場合に画質を落とす')
    parser.add_argument('--demo', action='store_true',
                        help='DEMO用に見栄えを重視する')
    parser.add_argument('--debug', action='store_true',
                        help='debugモード')
    args = parser.parse_args()
    F.argsPrint(args)
    return args


def main(args):
    if args.lower:
        w, h, fps = 176, 144, 30
    else:
        w, h, fps = 640, 480, 30

    # 超音波センサの初期化
    dist = objectDetect(args.serial_port)
    # カメラの初期化
    cap = videoCap(args.channel, 1, w, h, fps,
                   args.stock_num, args.interval_time)

    val = args.diff_val
    oldval = args.diff_val
    diff = 0
    while(True):
        # カメラ画像の取得
        if cap.read() is False:
            print('camera read false ...')
            time.sleep(2)
            continue

        val = dist.read()
        diff = oldval - val

        # 画面の表示とキー入力の取得
        key = cv2.waitKey(20) & 0xff

        # キーに応じて制御
        if key == 27:  # Esc Key
            print('exit!')
            break
        elif key == 13 or key == 10 or diff > args.diff_val:  # Enter Key or Sensor detect
            bk = cap.writeBk4(args.out_path)
            fr = cap.writeFr4(args.out_path)
            print('capture:', bk)
            print('capture:', fr)
            if args.debug or args.debug:
                cv2.imshow('cap', np.vstack([bk, fr]))

        oldval = val
        if args.debug:
            cv2.imshow('all', cap.viewAll())
            print('key: {}, frame: {}'.format(key, cap.frame_shape))
            dist.view()
        elif args.demo:
            cv2.imshow('all', cap.viewAll(2))

    # 終了処理
    cap.release()
    dist.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    print('Key bindings')
    print('[Esc] Exit')
    print('[Ent] Capture')
    main(command())
