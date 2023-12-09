import math

import numpy as np


# axis = 1 for x, 2 for y, and 3 for z
def _create_rot_matrix(theta: float, axis: int):
    rot_mat = np.identity(3, dtype=float)
    for i in range(2):
        for j in range(2):
            if (i+j) % 2 == 0:
                rot_mat[(axis+i) % 3, (axis+j) % 3] = math.cos(math.radians(theta))
            else:
                rot_mat[(axis+i) % 3, (axis+j) % 3] = math.sin(math.radians(theta))
    rot_mat[axis % 3, (1+axis) % 3] *= -1

    return rot_mat


class Transform:

    def __init__(self):
        self.tf_matrix = np.identity(4, dtype=float)

    def transformation_matrix(self):
        return self.tf_matrix.copy()

    def set_position(self, x, y, z):
        self.tf_matrix[0, 3] = x
        self.tf_matrix[1, 3] = y
        self.tf_matrix[2, 3] = z

    def set_rotation(self, x, y, z):
        rot = np.matmul(_create_rot_matrix(x, 1), _create_rot_matrix(y, 2))
        rot = np.matmul(rot, _create_rot_matrix(z, 3))
        self.tf_matrix[0:3, 0:3] = rot

    def inverse_matrix(self):
        ret = np.identity(4, dtype=float)
        ret[:3, :3] = self.tf_matrix[:3, :3].T
        ret[:3, 3] = np.matmul(ret[:3, :3] * -1, self.tf_matrix[:3, 3])
        return ret

    def apply_to_point(self, p):
        ret = (np.matmul(self.tf_matrix[:3, :3], np.atleast_2d(np.array(p)).T)).T
        return ret + np.atleast_2d(self.tf_matrix[:3, 3]).flatten()

    def apply_inverse_to_point(self, p):
        ret = (np.atleast_2d(np.array(p)).T - np.atleast_2d(self.transformation_matrix()[:3, 3]).T)
        return np.matmul(self.inverse_matrix()[:3, :3], ret).flatten()

    def apply_to_normal(self, n):
        return np.matmul(self.tf_matrix[:3, :3], np.array(n).T)

    def set_axis_rotation(self, axis, rotation):
        rot = np.atleast_2d(axis) * math.radians(rotation)
        print(rot)
