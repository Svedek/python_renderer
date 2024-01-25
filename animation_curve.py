import math
from enum import Enum


class CurveType(Enum):
    LINEAR = 0
    EXPONENTIAL = 1  # curve_value is exponent power
    ROOT = 2  # curve_value is root power
    SINE = 3  # curve_value is number of cycles
    COSINE = 4  # curve_value is number of cycles
    HOLD = 5

    @staticmethod
    def apply_curve(value, curve_type, curve_value=2):
        if curve_type == CurveType.LINEAR:
            return CurveType._linear_interpolation(value)
        elif curve_type == CurveType.EXPONENTIAL:
            return CurveType._exponential_interpolation(value, curve_value)
        elif curve_type == CurveType.ROOT:
            return CurveType._root_interpolation(value, curve_value)
        elif curve_type == CurveType.SINE:
            return CurveType._sine_interpolation(value, curve_value)
        elif curve_type == CurveType.COSINE:
            return CurveType._cosine_interpolation(value, curve_value)
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
    def _sine_interpolation(value, cycles):
        return (math.sin(2*math.pi*cycles*value) + 1) / 2

    @staticmethod
    def _cosine_interpolation(value, cycles):
        return (math.cos(2*math.pi*cycles*value) + 1) / 2

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
