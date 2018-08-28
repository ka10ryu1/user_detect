#!/usr/bin/env python3
# -*-coding: utf-8 -*-
#
help = 'Webカメラの画像管理'
#

import cv2
import time
import numpy as np

import Tools.imgfunc as I


class videoCap(object):
    """
    USBカメラの処理をクラス化したもの
    """

    def __init__(self, usb_ch, img_ch=3, lower=False, cap_num=6, interval=0.5):
        self._cap = cv2.VideoCapture(usb_ch)
        # lowerがセットされた場合に、画像サイズとFPSを固定する
        if lower:
            self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, 200)
            self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 200)
            self._cap.set(cv2.CAP_PROP_FPS, 5)
            self.size = (144, 176, img_ch)
        else:
            self.size = (480, 640, img_ch)

        # 表示・保存用画像の格納先を確保
        self._frame = I.blank.black(self.size)
        self._data = [I.blank.black(self.size) for i in range(cap_num)]
        # 保存する画像のチャンネル数
        self.ch = self.size[2]
        # キャプチャ画像のサイズ情報
        self.frame_shape = self._frame.shape
        # インターバル撮影する間隔 [s]
        self.interval = interval
        # 保存用の連番
        self._num = 0
        # 最後に書き込んだ時間
        self._write_time = 0
        # タイマー起動
        self._start = time.time()

    def read(self):
        """
        USBカメラから画像を取得し、インターバルを確認する
        [out] 画像取得判定
        """

        # USBカメラから画像を取得する
        ret, frame = self._cap.read()
        if ret is False:
            return ret

        # フレーム情報の確保
        self._frame = frame
        self.frame_shape = frame.shape

        # インターバルが経過していれば、フレームを確保する
        if self._intervalCheck():
            self._update()

        return ret

    def frame(self, rate=1):
        """
        現在のフレームの取得
        [in]  rate: 画像の拡大率
        [out] 拡大率を変更した現在のフレーム
        """

        return I.cnv.resize(self._frame, rate)

    def _intervalCheck(self):
        """
        インターバル撮影の確認
        [out] Trueならインターバルの時間経過
        """

        tm = time.time() - self._start
        if tm > self.interval:
            return True
        else:
            return False

    def _update(self):
        """
        インターバル画像のアップデート
        """

        if self.ch == 1:
            img = cv2.cvtColor(self._frame, cv2.COLOR_RGB2GRAY)
        else:
            img = self._frame

        self._data.pop(0)
        self._data.append(img)
        # タイマーリセット
        self._start = time.time()

    def frame_sub(self, img1, img2, img3, th):
        """
        フレーム差分を計算し、画像を返す
        [in]  img1: 比較するイメージ差分その1
        [in]  img2: 比較するイメージ差分その2
        [in]  img3: 比較するイメージ差分その3
        [in]  th:   しきい値
        [out] 計算した画像
        """

        # フレームの絶対差分
        diff1 = cv2.absdiff(img1, img2)
        diff2 = cv2.absdiff(img2, img3)

        # 2つの差分画像の論理積
        diff = cv2.bitwise_and(diff1, diff2)

        # 二値化処理
        diff[diff < th] = 0
        diff[diff >= th] = 255

        # メディアンフィルタ処理（ゴマ塩ノイズ除去）
        return cv2.medianBlur(diff, 5)

    def viewAll(self, resize=0.5):
        """
        インターバル画像をすべて表示
        [in]  表示する拡大率
        [out] 現在のフレームと全インターバル画像を連結したもの
        """

        # 画像を積み重ねてリサイズする
        sub_img = I.cnv.resize(I.cnv.vhstack(self._data, (2, -1)), 0.5)
        # 画像をカラーに変換する
        sub_img = cv2.cvtColor(sub_img, cv2.COLOR_GRAY2RGB)

        # 一定時間経過して、なおかつ画像に変化があった場合、DETECTと表示する
        wt = time.time() - self._write_time
        if wt > 10:
            moment = cv2.countNonZero(
                self.frame_sub(
                    self._data[0], self._data[1], self._data[2], th=10)
            )

            if moment > 5000:
                print('DETECT', moment)

        # すべての画像を連結・リサイズして返す
        return I.cnv.resize(np.hstack([self._frame, sub_img]), resize)

    def view(self, imgs, size, resize):
        """
        任意の画像を任意の行列で結合し任意のサイズで出力
        [in]  imgs: 入力画像リスト
        [in]  size: 結合したい行列情報
        [in]  resize: リサイズの割合
        [out] 結合してリサイズした画像
        """

        self._write_time = time.time()
        return I.cnv.resize(I.cnv.vhstack(imgs, size), resize)

    def viewBk4(self, resize=0.5):
        """
        インターバル画像の後ろから4枚を表示
        [in]  表示するリサイズ率
        [out] 表示するインターバル画像を後ろから4枚連結したもの
        """

        return self.view(self._data[0:4], (2, 2), resize)

    def viewFr4(self, resize=0.5):
        """
        インターバル画像の前から4枚を表示
        ※基本的にはviewBk4()と同じなので省略
        """

        return self.view(self._data[-5:-1], (2, 2), resize)

    def writeBk4(self, out_path, resize=0.5):
        """
        インターバル画像の後ろから4枚を保存
        [in]  out_path: 保存先のフォルダ名
        [in]  resize:   画像のリサイズ率
        [out] 保存するパス
        """

        return I.io.write(out_path, 'cap-B-', self.viewBk4(resize))

    def writeFr4(self, out_path, resize=0.5):
        """
        インターバル画像の前から4枚を保存
        ※基本的にはwriteBk4()と同じなので省略
        """

        return I.io.write(out_path, 'cap-F-', self.viewFr4(resize))

    def release(self):
        """
        終了処理
        """

        self._cap.release()
