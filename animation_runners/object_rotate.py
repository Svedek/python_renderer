import numpy as np
from screen import Screen
from camera import PerspectiveCamera,OrthoCamera
from mesh import Mesh
from renderer import Renderer, RenderAlgorithm
from light import PointLight
import animation_curve as curve
import animation_runner as animate


if __name__ == '__main__':
    screen = Screen(500,500)

    camera = PerspectiveCamera(-1.0, 1.0, -1.0, 1.0, 1.0, 10)

    rot_z = curve.Curve([[0.0, 0.0, curve.CurveType.LINEAR, 2],
                         [360.0, 8.0, curve.CurveType.LINEAR, 2]])

    camera.transform.set_position(0, -2.5, 0)

    mesh = Mesh.from_stl("../unit_sphere.stl", np.array([1.0, 0.0, 1.0]),\
        np.array([1.0, 1.0, 1.0]),0.05,1.0,0.5,1000)
    mesh.transform.set_rotation(0.0, 0.0, rot_z)

    light = PointLight(50.0, np.array([1, 1, 1]))
    light.transform.set_position(0, -5, 5)

    renderer = Renderer(screen, camera, [mesh], light)
    animate.run_animation(renderer, RenderAlgorithm.PHONG, [80,80,80], [0.2, 0.2, 0.2], 8, 8)

    screen.show()
