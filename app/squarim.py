import cv2 as cv
import numpy as np
from PIL import Image


class Squarim:
    def __init__(self, img):
        self.img = self.rotate(img)
        self.height, self.width, _ = self.img.shape

    def rotate(self, img):
        height, width, _ = img.shape
        if height >= width:
            self.rotated = False
            return img
        else:
            self.rotated = True
            return np.rot90(img, k=3)

    def stretch(self, left=0, right=0, mirror=False):
        if self.height > self.width:

            if mirror:
                return Image.fromarray(self._reflect(left, right))

            if left > 0 and right == 0:
                return Image.fromarray(self._stretch_left(left))

            if left == 0 and right > 0:
                return Image.fromarray(self._stretch_right(right))

            if left > 0 and right > 0:
                return Image.fromarray(self._stretch_both_sides(left=left, right=right))
        else:
            return Image.fromarray(self.img)

    def _stretch_left(self, left):
        padding = self.height - self.width

        left_side = self.img[:, 0:left, :]
        left_side_width = padding + left

        right_side = self.img[:, left:, :]

        left_side_resized = cv.resize(
            left_side, (left_side_width, self.height), interpolation=cv.INTER_AREA
        )
        resized_img = np.concatenate((left_side_resized, right_side), axis=1)
        return resized_img

    def _stretch_right(self, right):
        padding = self.height - self.width

        right_side = self.img[:, -right:, :]
        right_side_width = padding + right

        left_side = self.img[:, 0:-right, :]

        right_side_resized = cv.resize(
            right_side, (right_side_width, self.height), interpolation=cv.INTER_AREA
        )
        resized_img = np.concatenate((left_side, right_side_resized), axis=1)

        return resized_img

    def _stretch_both_sides(self, left, right):

        padding = (self.height - self.width) // 2

        left_side = self.img[:, 0:left, :]
        left_side_width = padding + left

        right_side = self.img[:, -right:, :]
        right_side_width = self.height - self.width - padding + right

        center = self.img[:, left:-right:, :]

        left_side_resized = cv.resize(
            left_side, (left_side_width, self.height), interpolation=cv.INTER_AREA
        )
        right_side_resized = cv.resize(
            right_side, (right_side_width, self.height), interpolation=cv.INTER_AREA
        )

        resized_img = np.concatenate(
            (left_side_resized, center, right_side_resized), axis=1
        )
        return resized_img

    def _reflect(self, left, right):
        if left > 0 and right > 0:
            padding = (self.height - self.width) // 2
            return cv.copyMakeBorder(
                self.img,
                0,
                0,
                padding,
                self.height - self.width - padding,
                cv.BORDER_REFLECT,
            )
        elif left > 0 and right == 0:
            return cv.copyMakeBorder(
                self.img, 0, 0, self.height - self.width, 0, cv.BORDER_REFLECT
            )
        elif left == 0 and right > 0:
            return cv.copyMakeBorder(
                self.img, 0, 0, self.height - self.width, 0, cv.BORDER_REFLECT
            )
