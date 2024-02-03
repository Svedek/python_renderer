import numpy as np
from transform import Transform
import stl


class Mesh:

    def __init__(self, diffuse_color, specular_color, ka, kd, ks, ke):
        self.transform = Transform()
        self.vertex_normals = []
        self.verts = []
        self.faces = []
        self.normals = np.array([])
        self.bounds = np.array([])
        self.diffuse_color = np.array(diffuse_color)
        self.specular_color = np.array(specular_color)
        self.ka = ka
        self.kd = kd
        self.ks = ks
        self.ke = ke

    @staticmethod
    def from_stl(stl_path, diffuse_color, specular_color, ka, kd, ks, ke):
        new_mesh = Mesh(diffuse_color, specular_color, ka, kd, ks, ke)
        stl_mesh = stl.Mesh.from_file(stl_path)

        new_mesh.normals = stl_mesh.normals
        new_mesh.bounds = (Vector3(stl_mesh.min_).get_tuple(), Vector3(stl_mesh.max_).get_tuple())

        vert_count = 0
        temp = np.zeros((stl_mesh.points.shape[0], 3))
        for i in range(stl_mesh.points.shape[0]):
            new_mesh.faces.append([-1, -1, -1])
            pts = [stl_mesh.v0[i],
                   stl_mesh.v1[i],
                   stl_mesh.v2[i]]
            vals = [True, True, True]
            for j in range(vert_count):
                for k in range(3):
                    if (temp[j] == pts[k]).all():  # if point k already exists in temp
                        new_mesh.faces[i][k] = j
                        vals[k] = False

                        new_mesh.vertex_normals[j] = new_mesh.vertex_normals[j] + new_mesh.normals[i]  #


            for k in range(3):
                if vals[k]:
                    temp[vert_count] = pts[k]
                    new_mesh.faces[i][k] = vert_count

                    new = [new_mesh.normals[i, 0], new_mesh.normals[i, 1], new_mesh.normals[i, 2]]
                    new_mesh.vertex_normals.append(new_mesh.normals[i])  #

                    vert_count += 1


        for i in range(vert_count):
            new_mesh.verts.append((temp[i, 0], temp[i, 1], temp[i, 2]))
            new_mesh.vertex_normals[i] = _normalize(np.array(new_mesh.vertex_normals[i]))  #

        return new_mesh


class Vector3:
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.__init__()
        self.x = x
        self.y = y
        self.z = z

    def __init__(self, xyz):
        self.x = xyz[0]
        self.y = xyz[1]
        self.z = xyz[2]

    def get_tuple(self):
        return (self.x, self.y, self.z)


def _normalize(v):
    n = np.linalg.norm(v)
    if n == 0:
        return v
    return v / np.linalg.norm(v)
