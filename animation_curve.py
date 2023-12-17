import math

import numpy as np
from enum import Enum


class CurveType(Enum):
    LINEAR = 0
    EXPONENTIAL = 1
    ROOT = 2
    HOLD = 3

    @staticmethod
    def apply_curve(value, curve_type, curve_power=2):
        if curve_type == CurveType.LINEAR:
            return CurveType._linear_interpolation(value)
        elif curve_type == CurveType.EXPONENTIAL:
            return CurveType._exponential_interpolation(value, curve_power)
        elif curve_type == CurveType.ROOT:
            return CurveType._root_interpolation(value, curve_power)
        elif curve_type == CurveType.HOLD:
            return CurveType._hold_interpolation(value)

    @staticmethod
    def _linear_interpolation(value):
        return value

    @staticmethod
    def _exponential_interpolation(value, curve_power):
        return math.pow(value, curve_power)

    @staticmethod
    def _root_interpolation(value, curve_power):
        return math.pow(value, 1/curve_power)

    @staticmethod
    def _hold_interpolation(value):
        return 0.0


class Curve:
    # args = list of [target_value, time_value [0.0,infinity], curve_type, curve_power (used in exponential and root, default is 2)]
    def __init__(self, curve):
        self.current_index = 0
        self.curve = curve

    def interpolate(self, time_value):
        # Ensure current_index points to the last element with a lower time_value or the last element in curve
        while self.current_index+1 < len(self.curve) and self.curve[self.current_index + 1][1] <= time_value:
            self.current_index += 1

        if self.current_index+1 == len(self.curve):
            return self.curve[self.current_index][0]

        # Get interpolation_value between current and next keyframe
        time_value -= self.curve[self.current_index][1]
        interpolation_value = time_value / (self.curve[self.current_index + 1][1] - self.curve[self.current_index][1])
        interpolation_value = CurveType.apply_curve(interpolation_value, self.curve[self.current_index][2], self.curve[self.current_index][3])

        return (1.0 - interpolation_value) * self.curve[self.current_index][0] + interpolation_value * self.curve[self.current_index + 1][0]


# curve = Curve([[np.array([0.0, 0.0]), 0.0, CurveType.LINEAR, 2],
#                [np.array([5.0, 1.0]), 1.0, CurveType.EXPONENTIAL, 2],
#                [np.array([1.0, 3.0]), 3.0, CurveType.HOLD, 2],
#                [np.array([9.0, 5.0]), 5.0, CurveType.ROOT, 2],
#                [np.array([0.0, 7.0]), 7.0, CurveType.HOLD, 2]])
#
# print("0.0: " + str(curve.interpolate(0.0)))
# print("0.6: " + str(curve.interpolate(0.6)))
# print("1.0: " + str(curve.interpolate(1.0)))
# print("2.0: " + str(curve.interpolate(2.0)))
# print("3.0: " + str(curve.interpolate(3.0)))
# print("4.0: " + str(curve.interpolate(4.0)))
# print("5.0: " + str(curve.interpolate(5.0)))
# print("6.0: " + str(curve.interpolate(6.0)))
# print("7.0: " + str(curve.interpolate(7.0)))
# print("8.0: " + str(curve.interpolate(8.0)))
