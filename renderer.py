import math

import numpy as np


class Renderer:
    def __init__(self, screen, camera, meshs, light):
        self.screen = screen
        self.camera = camera
        self.meshs = meshs
        self.light = light

    def render(self, shading: str, bg_color, ambient_light, time):
        shade = shading.lower()
        if shade == "none":
            self.screen.draw(self.no_shading(bg_color, time))
        elif shade == "flat":
            self.screen.draw(self.flat_shading(bg_color, ambient_light, time))
        elif shade == "barycentric":
            self.screen.draw(self.barycentric_shading(bg_color, ambient_light, time))
        elif shade == "depth":
            self.screen.draw(self.depth_shading(bg_color, ambient_light, time))
        elif shade == "phong-blinn":
            self.screen.draw(self.phong_shading(bg_color, ambient_light, time))

    def no_shading(self, bg_color, time):
        self.camera.set_time(time)
        render = np.full((self.screen.width, self.screen.height, 3), bg_color)
        for mesh in self.meshs:
            for face in mesh.faces:
                verts = np.array(
                    [self.camera.project_point(mesh.transform.apply_to_point(mesh.verts[face[0]], time)),
                     self.camera.project_point(mesh.transform.apply_to_point(mesh.verts[face[1]], time)),
                     self.camera.project_point(mesh.transform.apply_to_point(mesh.verts[face[2]], time))]
                )
                low = np.array(verts[0])
                high = np.array(verts[0])
                for vert in verts:
                    for i in range(3):
                        low[i] = min(low[i], vert[i])
                        high[i] = max(high[i], vert[i])

                dis_low = _screen_to_display(low, self.screen.width, self.screen.height)
                dis_high = _screen_to_display(high, self.screen.width, self.screen.height)
                dis_low[0] = max(0, dis_low[0])
                dis_low[2] = max(0, dis_low[2])
                dis_low[0] = min(self.screen.width-1, dis_low[0])
                dis_low[2] = min(self.screen.height-1, dis_low[2])
                dis_high[0] = max(0, dis_high[0])
                dis_high[2] = max(0, dis_high[2])
                dis_high[0] = min(self.screen.width-1, dis_high[0])
                dis_high[2] = min(self.screen.height-1, dis_high[2])

                # Iterate through displayed pixels
                for i in range(dis_high[0] - dis_low[0] + 1):
                    for j in range(dis_high[2] - dis_low[2] + 1):
                        p = np.array([dis_low[0]+i, dis_low[2]+j], dtype=int)

                        a = np.array([verts[0,0],verts[0,2]], dtype=float)
                        b = np.array([verts[1,0],verts[1,2]], dtype=float)
                        c = np.array([verts[2,0],verts[2,2]], dtype=float)
                        p2 = _display_to_screen_bc(p, self.screen.width, self.screen.height)

                        bc = _bc_coords(a, b, c, p2)
                        if _bary_in_range(bc[0], bc[1], bc[2]):
                            render[p[0], p[1]] = [0,0,0]
                # If going for performance, remove following line, else this is more fun to watch
                # self.screen.draw(render)
        return render

    def flat_shading(self, bg_color, ambient_light, time):
        self.camera.set_time(time)

        # Static color components
        light_world_pos = self.light.transform.apply_to_point(np.array([0.0, 0.0, 0.0]), time)
        camera_world_pos = self.camera.transform.apply_to_point(np.array([0.0, 0.0, 0.0]), time)

        render = np.full((self.screen.width, self.screen.height, 3), bg_color)
        z_buffer = np.full((self.screen.width, self.screen.height), 2.0)
        for mesh in self.meshs:
            for face, normal in zip(mesh.faces, mesh.normals):
                normal = mesh.transform.apply_to_normal(_normalize(normal), time)
                # Normal culling
                if np.dot(normal, self.camera.view_dir()) > 0:
                    continue

                # Calculate Per-Face color
                face_world_pos = mesh.transform.apply_to_point(mesh.verts[face[0]], time) + \
                                 mesh.transform.apply_to_point(mesh.verts[face[1]], time) + \
                                 mesh.transform.apply_to_point(mesh.verts[face[2]], time)
                face_world_pos = face_world_pos / 3.0
                l = (light_world_pos - face_world_pos).flatten()
                v = (camera_world_pos - face_world_pos).flatten()
                h = _normalize(l + v)
                cos = max(0, np.dot(_normalize(l), normal))

                irradiance = self.light.intensity * cos / pow(_magnitude(l), 2) * self.light.color
                diffuse = mesh.kd / math.pi * mesh.diffuse_color
                specular = mesh.ks * mesh.specular_color * math.pow(max(0, np.dot(normal, h)), mesh.ke)
                dynamic = np.array([(diffuse[0] + specular[0]) * irradiance[0],
                                    (diffuse[1] + specular[1]) * irradiance[1],
                                    (diffuse[2] + specular[2]) * irradiance[2]])
                color = dynamic + mesh.ka * np.array(ambient_light)
                color_int = np.array([int(color[0] * 255), int(color[1] * 255), int(color[2] * 255)])

                # Get verts in screen space
                verts = np.array(
                    [self.camera.project_point(mesh.transform.apply_to_point(mesh.verts[face[0]], time)),
                     self.camera.project_point(mesh.transform.apply_to_point(mesh.verts[face[1]], time)),
                     self.camera.project_point(mesh.transform.apply_to_point(mesh.verts[face[2]], time))]
                )

                # Get the bounds of the face in screen space
                low = np.array(verts[0])
                high = np.array(verts[0])
                for vert in verts:
                    for i in range(3):
                        low[i] = min(low[i], vert[i])
                        high[i] = max(high[i], vert[i])

                # Get the bounds in display space
                dis_low = _screen_to_display(low, self.screen.width, self.screen.height)
                dis_high = _screen_to_display(high, self.screen.width, self.screen.height)
                dis_low[0] = max(0, dis_low[0])
                dis_low[2] = max(0, dis_low[2])
                dis_low[0] = min(self.screen.width-1, dis_low[0])
                dis_low[2] = min(self.screen.height-1, dis_low[2])
                dis_high[0] = max(0, dis_high[0])
                dis_high[2] = max(0, dis_high[2])
                dis_high[0] = min(self.screen.width-1, dis_high[0])
                dis_high[2] = min(self.screen.height-1, dis_high[2])

                # Iterate through displayed pixels
                print(str(dis_high) + " ::: " + str(dis_low))
                for i in range(dis_high[0] - dis_low[0] + 1):
                    for j in range(dis_high[2] - dis_low[2] + 1):
                        # Get barycentric coordinates: bc = [alpha, beta, gamma]
                        p = np.array([dis_low[0] + i, dis_low[2] + j], dtype=int)
                        a = np.array([verts[0, 0], verts[0, 2]], dtype=float)
                        b = np.array([verts[1, 0], verts[1, 2]], dtype=float)
                        c = np.array([verts[2, 0], verts[2, 2]], dtype=float)
                        p2 = _display_to_screen_bc(p, self.screen.width, self.screen.height)
                        bc = _bc_coords(a, b, c, p2)

                        if not _bary_in_range(bc[0], bc[1], bc[2]):
                            continue

                        # Check y in screen space against z-buffer
                        py = bc[0] * verts[0, 1] + bc[1] * verts[1, 1] + bc[2] * verts[2, 1]
                        if -1 > py or py > 1 or z_buffer[p[0], p[1]] < py:
                            continue
                        z_buffer[p[0], p[1]] = py

                        # Add pixel to render buffer
                        render[p[0], p[1]] = color_int
                # If going for performance, remove following line, else this is more fun to watch
                # self.screen.draw(render)
        return render

    def phong_shading(self, bg_color, ambient_light, time):
        self.camera.set_time(time)

        # Static color components
        light_world_pos = self.light.transform.apply_to_point(np.array([0.0, 0.0, 0.0]), time)
        camera_world_pos = self.camera.transform.apply_to_point(np.array([0.0, 0.0, 0.0]), time)

        render = np.full((self.screen.width, self.screen.height, 3), bg_color)
        z_buffer = np.full((self.screen.width, self.screen.height), 2.0)
        for mesh in self.meshs:
            for face, normal in zip(mesh.faces, mesh.normals):
                normal = mesh.transform.apply_to_normal(_normalize(normal), time)
                # Normal culling
                if np.dot(normal, self.camera.view_dir()) > 0:
                    continue

                # Get verts in screen space
                verts = np.array(
                    [self.camera.project_point(mesh.transform.apply_to_point(mesh.verts[face[0]], time)),
                     self.camera.project_point(mesh.transform.apply_to_point(mesh.verts[face[1]], time)),
                     self.camera.project_point(mesh.transform.apply_to_point(mesh.verts[face[2]], time))]
                )
                vert_normals = np.array(
                    [mesh.transform.apply_to_normal(mesh.vertex_normals[face[0]], time),
                     mesh.transform.apply_to_normal(mesh.vertex_normals[face[1]], time),
                     mesh.transform.apply_to_normal(mesh.vertex_normals[face[2]], time)]
                )

                # Get the bounds of the face in screen space
                low = np.array(verts[0])
                high = np.array(verts[0])
                for vert in verts:
                    for i in range(3):
                        low[i] = min(low[i], vert[i])
                        high[i] = max(high[i], vert[i])

                # Get the bounds in display space
                dis_low = _screen_to_display(low, self.screen.width, self.screen.height)
                dis_high = _screen_to_display(high, self.screen.width, self.screen.height)
                dis_low[0] = max(0, dis_low[0])
                dis_low[2] = max(0, dis_low[2])
                dis_low[0] = min(self.screen.width-1, dis_low[0])
                dis_low[2] = min(self.screen.height-1, dis_low[2])
                dis_high[0] = max(0, dis_high[0])
                dis_high[2] = max(0, dis_high[2])
                dis_high[0] = min(self.screen.width-1, dis_high[0])
                dis_high[2] = min(self.screen.height-1, dis_high[2])

                # Iterate through displayed pixels
                for i in range(dis_high[0] - dis_low[0] + 1):
                    for j in range(dis_high[2] - dis_low[2] + 1):
                        # Get barycentric coordinates: bc = [alpha, beta, gamma]
                        p = np.array([dis_low[0] + i, dis_low[2] + j], dtype=int)
                        a = np.array([verts[0, 0], verts[0, 2]], dtype=float)
                        b = np.array([verts[1, 0], verts[1, 2]], dtype=float)
                        c = np.array([verts[2, 0], verts[2, 2]], dtype=float)
                        p2 = _display_to_screen_bc(p, self.screen.width, self.screen.height)
                        bc = _bc_coords(a, b, c, p2)

                        if not _bary_in_range(bc[0], bc[1], bc[2]):
                            continue

                        # Check y in screen space against z-buffer
                        py = bc[0] * verts[0, 1] + bc[1] * verts[1, 1] + bc[2] * verts[2, 1]
                        if -1 > py or py > 1 or z_buffer[p[0], p[1]] < py:
                            continue
                        z_buffer[p[0], p[1]] = py

                        # Calculate color
                        point_normal = _normalize(bc[0] * vert_normals[0] + bc[1] * vert_normals[1] + bc[2] * vert_normals[2])

                        # Calculate Per-Face color
                        point_world_pos = bc[0] * mesh.transform.apply_to_point(mesh.verts[face[0]], time) + \
                                          bc[1] * mesh.transform.apply_to_point(mesh.verts[face[1]], time) + \
                                          bc[2] * mesh.transform.apply_to_point(mesh.verts[face[2]], time)
                        point_world_pos = point_world_pos.flatten()
                        l = (light_world_pos - point_world_pos).flatten()
                        v = (camera_world_pos - point_world_pos).flatten()
                        l_mag = _magnitude(l)
                        l = _normalize(l)  # Not 100% sure these normalizations are nessesary
                        v = _normalize(v)
                        h = _normalize(l + v)
                        cos = max(0, np.dot(_normalize(l), point_normal))

                        irradiance = self.light.intensity * cos / pow(l_mag, 2) * self.light.color
                        diffuse = mesh.kd / math.pi * mesh.diffuse_color
                        specular = mesh.ks * mesh.specular_color * math.pow(max(0, np.dot(point_normal, h)), mesh.ke)
                        dynamic = np.array([(diffuse[0] + specular[0]) * irradiance[0],
                                            (diffuse[1] + specular[1]) * irradiance[1],
                                            (diffuse[2] + specular[2]) * irradiance[2]])
                        color = dynamic + mesh.ka * np.array(ambient_light)
                        color_int = np.array([int(color[0] * 255), int(color[1] * 255), int(color[2] * 255)])

                        # Add pixel to render buffer
                        render[p[0], p[1]] = color_int
                # If going for performance, remove following line, else this is more fun to watch
                # self.screen.draw(render)
        return render

    def barycentric_shading(self, bg_color, ambient_light, time):
        self.camera.set_time(time)

        render = np.full((self.screen.width, self.screen.height, 3), bg_color)
        z_buffer = np.full((self.screen.width, self.screen.height), 2.0)
        for mesh in self.meshs:
            for face, normal in zip(mesh.faces, mesh.normals):
                normal = mesh.transform.apply_to_normal(_normalize(normal), time)
                # Normal culling
                if np.dot(normal, self.camera.view_dir()) > 0:
                    continue

                # Get verts in screen space
                verts = np.array(
                    [self.camera.project_point(mesh.transform.apply_to_point(mesh.verts[face[0]], time)),
                     self.camera.project_point(mesh.transform.apply_to_point(mesh.verts[face[1]], time)),
                     self.camera.project_point(mesh.transform.apply_to_point(mesh.verts[face[2]], time))]
                )

                # Get the bounds of the face in screen space
                low = np.array(verts[0])
                high = np.array(verts[0])
                for vert in verts:
                    for i in range(3):
                        low[i] = min(low[i], vert[i])
                        high[i] = max(high[i], vert[i])

                # Get the bounds in display space
                dis_low = _screen_to_display(low, self.screen.width, self.screen.height)
                dis_high = _screen_to_display(high, self.screen.width, self.screen.height)
                dis_low[0] = max(0, dis_low[0])
                dis_low[2] = max(0, dis_low[2])
                dis_low[0] = min(self.screen.width-1, dis_low[0])
                dis_low[2] = min(self.screen.height-1, dis_low[2])
                dis_high[0] = max(0, dis_high[0])
                dis_high[2] = max(0, dis_high[2])
                dis_high[0] = min(self.screen.width-1, dis_high[0])
                dis_high[2] = min(self.screen.height-1, dis_high[2])

                # Iterate through displayed pixels
                for i in range(dis_high[0] - dis_low[0] + 1):
                    for j in range(dis_high[2] - dis_low[2] + 1):
                        # Get barycentric coordinates: bc = [alpha, beta, gamma]
                        p = np.array([dis_low[0]+i, dis_low[2]+j], dtype=int)
                        a = np.array([verts[0,0],verts[0,2]], dtype=float)
                        b = np.array([verts[1,0],verts[1,2]], dtype=float)
                        c = np.array([verts[2,0],verts[2,2]], dtype=float)
                        p2 = _display_to_screen_bc(p, self.screen.width, self.screen.height)
                        bc = _bc_coords(a, b, c, p2)

                        if _bary_in_range(bc[0], bc[1], bc[2]):
                            # Check y in screen space against z-buffer
                            py = bc[0]*verts[0,1] + bc[1]*verts[1,1] + bc[2]*verts[2,1]
                            if -1 > py or py > 1 or z_buffer[p[0], p[1]] < py:
                                continue
                            z_buffer[p[0], p[1]] = py

                            # Add pixel to render buffer
                            render[p[0], p[1]] = [int(bc[0] * 255), int(bc[1] * 255), int(bc[2] * 255)]
                # If going for performance, remove following line, else this is more fun to watch
                # self.screen.draw(render)
        return render

    def depth_shading(self, bg_color, ambient_light, time):
        self.camera.set_time(time)

        # Get shading scale
        depth = np.array([1.0,-1.0])
        for mesh in self.meshs:
            for face in mesh.faces:
                verts = np.array(
                    [self.camera.project_point(mesh.transform.apply_to_point(mesh.verts[face[0]], time)),
                     self.camera.project_point(mesh.transform.apply_to_point(mesh.verts[face[1]], time)),
                     self.camera.project_point(mesh.transform.apply_to_point(mesh.verts[face[2]], time))]
                )
                for vert in verts:
                    depth[0] = min(depth[0], vert[1])
                    depth[1] = max(depth[1], vert[1])
        delta_depth = depth[1] - depth[0]

        render = np.full((self.screen.width, self.screen.height, 3), bg_color)
        z_buffer = np.full((self.screen.width, self.screen.height), 2.0)
        for mesh in self.meshs:
            for face, normal in zip(mesh.faces, mesh.normals):
                normal = mesh.transform.apply_to_normal(_normalize(normal), time)
                # Normal culling
                if np.dot(normal, self.camera.view_dir()) > 0:
                    continue

                # Get verts in screen space
                verts = np.array(
                    [self.camera.project_point(mesh.transform.apply_to_point(mesh.verts[face[0]], time)),
                     self.camera.project_point(mesh.transform.apply_to_point(mesh.verts[face[1]], time)),
                     self.camera.project_point(mesh.transform.apply_to_point(mesh.verts[face[2]], time))]
                )

                # Get the bounds of the face in screen space
                low = np.array(verts[0])
                high = np.array(verts[0])
                for vert in verts:
                    for i in range(3):
                        low[i] = min(low[i], vert[i])
                        high[i] = max(high[i], vert[i])

                # Get the bounds in display space
                dis_low = _screen_to_display(low, self.screen.width, self.screen.height)
                dis_high = _screen_to_display(high, self.screen.width, self.screen.height)
                dis_low[0] = max(0, dis_low[0])
                dis_low[2] = max(0, dis_low[2])
                dis_low[0] = min(self.screen.width-1, dis_low[0])
                dis_low[2] = min(self.screen.height-1, dis_low[2])
                dis_high[0] = max(0, dis_high[0])
                dis_high[2] = max(0, dis_high[2])
                dis_high[0] = min(self.screen.width-1, dis_high[0])
                dis_high[2] = min(self.screen.height-1, dis_high[2])

                # Iterate through displayed pixels
                for i in range(dis_high[0] - dis_low[0] + 1):
                    for j in range(dis_high[2] - dis_low[2] + 1):
                        # Get barycentric coordinates: bc = [alpha, beta, gamma]
                        p = np.array([dis_low[0] + i, dis_low[2] + j], dtype=int)
                        a = np.array([verts[0, 0], verts[0, 2]], dtype=float)
                        b = np.array([verts[1, 0], verts[1, 2]], dtype=float)
                        c = np.array([verts[2, 0], verts[2, 2]], dtype=float)
                        p2 = _display_to_screen_bc(p, self.screen.width, self.screen.height)
                        bc = _bc_coords(a, b, c, p2)

                        if _bary_in_range(bc[0], bc[1], bc[2]):
                            # Check y in screen space against z-buffer
                            py = bc[0] * verts[0, 1] + bc[1] * verts[1, 1] + bc[2] * verts[2, 1]
                            if -1 > py or py > 1 or z_buffer[p[0], p[1]] < py:
                                continue
                            z_buffer[p[0], p[1]] = py

                            # Add pixel to render buffer
                            col = int((py - depth[0]) / delta_depth * 255)
                            render[p[0], p[1]] = [col, col, col]
                # If going for performance, remove following line, else this is more fun to watch
                # self.screen.draw(render)
        return render


# Returns [->a, ->b, ->c]
def _bc_coords(a, b, c, p):
    v0 = b-a
    v1 = c-a
    v2 = p-a
    d00 = np.dot(v0,v0)
    d01 = np.dot(v0,v1)
    d11 = np.dot(v1,v1)
    d20 = np.dot(v2,v0)
    d21 = np.dot(v2,v1)
    denom = d00 * d11 - d01 * d01
    v = (d11 * d20 - d01 * d21) / denom
    w = (d00 * d21 - d01 * d20) / denom
    u = 1.0-v-w
    return np.array([u, v, w])


def _screen_to_display(p, width, height):
    ret = np.zeros(3, dtype=int)
    ret[0] = int((p[0]/2 + 0.5) * width)
    ret[2] = int((p[2]/2 + 0.5) * height)
    return ret


def _display_to_screen(p, width, height):
    ret = np.zeros(3, dtype=float)
    ret[0] = (2.0 * p[0] / width) - 1.0
    ret[2] = (2.0 * p[2] / height) - 1.0
    return ret


def _display_to_screen_bc(p, width, height):
    ret = np.zeros(2, dtype=float)
    ret[0] = (2.0 * p[0] / width) - 1.0
    ret[1] = (2.0 * p[1] / height) - 1.0
    return ret


def _bary_in_range(alpha, beta, gamma):
    return (0 <= alpha <= 1) and (0 <= beta <= 1) and (0 <= gamma <= 1)


def _normalize(v):
    n = np.linalg.norm(v)
    if n == 0:
        return v
    return v / np.linalg.norm(v)


def _magnitude(v):
    sum = 0.0
    for axis in v:
        sum+= pow(axis,2)
    return math.sqrt(sum)
