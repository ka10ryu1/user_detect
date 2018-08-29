#!/usr/bin/env python
# -*- coding: utf-8 -*-
help = 'HC-SR04を使用して距離を測定する'
#

import time
import serial
import datetime
import numpy as np


class objectDetect(object):
    """
    ARDUINOに接続された超音波センサから
    シリアル通信で距離情報を取得する
    """

    def __init__(self, serial_port, data_num=10, interval=0.2):
        # シリアル通信の設定
        self._serial = serial.Serial(serial_port, 9600, timeout=1)
        print('serial port open: {}'.format(self._serial.portstr))
        # 距離情報(生値)を格納する
        self._data = np.zeros(10)
        self._sn = 20
        # ARDUINOとの接続が確立されるまで数秒かかるので待つ
        time.sleep(3)
        # タイマー起動
        self._start = time.time()
        # タイマーインターバル設定 [s]
        self._interval = interval

    def _str2float(self, line):
        line = line.decode()  # byte -> string
        di = line.rstrip()  # 行終端コード削除
        try:
            fdi = float(di)
        except:
            fdi = 0

        return fdi

    def _queue(self, a):
        dst = np.roll(self._data, -1)
        dst[-1] = a
        return dst

    def _calcSN(self):
        ave = np.average(self._data)
        sigma = np.std(self._data)
        return self._sn * np.log10(ave/sigma)

    def read(self):
        tm = time.time() - self._start
        if tm > self._interval:
            line = self._str2float(self._serial.readline())
            self._data = self._queue(line)
            self._start = time.time()

        return self._data[-1]

    def view(self):
        print('TIME: {}'.format(datetime.datetime.today()))
        print('DIST(S/N): {0:6.2f}[cm]({1:5.2f}[dB])'.format(
            self._data[-1], self._calcSN())
        )

    def release(self):
        print('serial port close: {}'.format(self._serial.portstr))
        self._serial.close()
