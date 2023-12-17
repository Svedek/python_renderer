import numpy as np
import transform as tf


class OrthoCamera:
    def __init__(self,
                 l: float = -1.0,
                 r: float = 1.0,
                 b: float = -1.0,
                 t: float = 1.0,
                 n: float = 0.0,
                 f: float = 1.0):
        self.transform = tf.Transform()
        self.ortho_transform = np.identity(4, dtype=float)
        self.ortho_transform[:3, 3] = (-(r+l)/(r-l), -(f+n)/(f-n), -(t+b)/(t-b))
        self.ortho_transform[0, 0] = 2/(r-l)
        self.ortho_transform[1, 1] = 2/(f-n)
        self.ortho_transform[2, 2] = 2/(t-b)

        self.time = None

    def set_time(self, time):
        self.time = time

    def ratio(self):
        return abs(self.ortho_transform[2, 2] / self.ortho_transform[0, 0])

    def project_point(self, p):
        p2 = np.array([1.0, 1.0, 1.0, 1.0])
        p2[:3] = self.transform.apply_inverse_to_point(p, self.time)
        return np.matmul(self.ortho_transform, p2)[:3]

    def project_inverse_point(self, p):
        p2 = np.matmul(self._ortho_inverse_matrix(), np.array([p[0],p[1],p[2],1.0]))[:3]
        return self.transform.apply_to_point(p2, self.time).flatten()

    def view_dir(self):
        return self.transform.apply_to_normal(np.array([0.0, 1.0, 0.0]), self.time)

    def _ortho_inverse_matrix(self):
        ret = np.identity(4, dtype=float)
        for i in range(3):
            ret[i, i] = 1 / self.ortho_transform[i, i]
            ret[i, 3] = -ret[i, i] * self.ortho_transform[i, 3]
        return ret


class PerspectiveCamera:
    def __init__(self,
                 l: float = -1.0,
                 r: float = 1.0,
                 b: float = -1.0,
                 t: float = 1.0,
                 n: float = 0.0,
                 f: float = 1.0):
        self.transform = tf.Transform()

        self.ortho_transform = np.identity(4, dtype=float)
        self.ortho_transform[:3, 3] = (-(r+l)/(r-l), -(f+n)/(f-n), -(t+b)/(t-b))
        self.ortho_transform[0, 0] = 2/(r-l)
        self.ortho_transform[1, 1] = 2/(f-n)
        self.ortho_transform[2, 2] = 2/(t-b)

        self.persp_transform = np.zeros((4,4), dtype=float)
        self.persp_transform[0, 0] = n
        self.persp_transform[1, 1] = n+f
        self.persp_transform[2, 2] = n
        self.persp_transform[1, 3] = -n*f
        self.persp_transform[3, 1] = 1.0

        self.time = None

    def set_time(self, time):
        self.time = time

    def ratio(self):
        return abs(self.ortho_transform[2, 2] / self.ortho_transform[0, 0])

    def project_point(self, p):
        p2 = np.array([1.0, 1.0, 1.0, 1.0])
        p2[:3] = self.transform.apply_inverse_to_point(p, self.time)
        p2 = np.matmul(self.persp_transform, p2)
        p2 /= p2[3]
        p2 = np.matmul(self.ortho_transform, p2)
        return p2[:3]

    def project_inverse_point(self, p):
        p1 = np.matmul(self._ortho_inverse_matrix(), np.append(p,1.0))
        yc = -self.persp_transform[1, 3] / (self.persp_transform[1, 1] - p1[1])
        p2 = p1 * yc
        pc = np.matmul(self._persp_inverse_matrix(), p2)[:3]
        return self.transform.apply_to_point(pc, self.time)

    def view_dir(self):
        return self.transform.apply_to_normal(np.array([0.0, 1.0, 0.0]), self.time)

    def _ortho_inverse_matrix(self):
        ret = np.identity(4, dtype=float)
        for i in range(3):
            ret[i, i] = 1 / self.ortho_transform[i, i]
            ret[i, 3] = -ret[i, i] * self.ortho_transform[i, 3]
        return ret

    def _persp_inverse_matrix(self):
        ret = np.zeros((4,4), dtype=float)
        ret[0,0] = 1/self.persp_transform[0,0]
        ret[2,2] = 1/self.persp_transform[2,2]
        ret[1,3] = 1
        ret[3,1] = 1/self.persp_transform[1, 3]
        ret[3,3] = -(self.persp_transform[1, 1] / self.persp_transform[1, 3])
        return ret
