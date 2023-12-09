import numpy as np
from transform import Transform


class PointLight:
    def __init__(self, intensity=1.0, color=np.array([1.0, 1.0, 1.0])):
        self.transform = Transform()
        self.intensity = intensity
        self.color = color
