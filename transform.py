import math

import numpy as np
import animation_curve as curve


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
        self.last_interp = None
        self.last_tf_mat = None

        self.x_pos = 0.0
        self.y_pos = 0.0
        self.z_pos = 0.0

        self.x_rot = 0.0
        self.y_rot = 0.0
        self.z_rot = 0.0

    def transformation_matrix(self, interpolation=0.0):
        if self.last_interp == interpolation:
            return self.last_tf_mat

        tf_matrix = np.identity(4, dtype=float)

        # Set position
        tf_matrix[0, 3] = self.x_pos.interpolate(interpolation) if type(self.x_pos) == curve.Curve else self.x_pos
        tf_matrix[1, 3] = self.y_pos.interpolate(interpolation) if type(self.y_pos) == curve.Curve else self.y_pos
        tf_matrix[2, 3] = self.z_pos.interpolate(interpolation) if type(self.z_pos) == curve.Curve else self.z_pos

        # Set rotation
        x = self.x_rot.interpolate(interpolation) if type(self.x_rot) == curve.Curve else self.x_rot
        y = self.y_rot.interpolate(interpolation) if type(self.y_rot) == curve.Curve else self.y_rot
        z = self.z_rot.interpolate(interpolation) if type(self.z_rot) == curve.Curve else self.z_rot

        rot = np.matmul(_create_rot_matrix(x, 1), _create_rot_matrix(y, 2))
        rot = np.matmul(rot, _create_rot_matrix(z, 3))
        tf_matrix[0:3, 0:3] = rot

        self.last_interp = interpolation
        self.last_tf_mat = tf_matrix
        return tf_matrix

    def set_position(self, x, y, z):
        self.x_pos = x
        self.y_pos = y
        self.z_pos = z

    def set_rotation(self, x, y, z):
        self.x_rot = x
        self.y_rot = y
        self.z_rot = z

    def inverse_matrix(self, interpolation):  # =0.0):
        ret = np.identity(4, dtype=float)
        tf_mat = self.transformation_matrix(interpolation)
        ret[:3, :3] = tf_mat[:3, :3].T
        ret[:3, 3] = np.matmul(ret[:3, :3] * -1, tf_mat[:3, 3])
        return ret

    def apply_to_point(self, p, interpolation):  # =0.0):
        tf_mat = self.transformation_matrix(interpolation)
        ret = (np.matmul(tf_mat[:3, :3], np.atleast_2d(np.array(p)).T)).T
        return (ret + np.atleast_2d(tf_mat[:3, 3])).flatten()

    def apply_inverse_to_point(self, p, interpolation):  # =0.0):
        ret = (np.atleast_2d(np.array(p)).T - np.atleast_2d(self.transformation_matrix(interpolation)[:3, 3]).T)
        return np.matmul(self.inverse_matrix(interpolation)[:3, :3], ret).flatten()

    def apply_to_normal(self, n, interpolation):  # =0.0):
        return np.matmul(self.transformation_matrix(interpolation)[:3, :3], np.array(n).T)
