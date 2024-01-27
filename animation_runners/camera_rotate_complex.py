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

    x_pos = curve.Curve([[3.5, 0.0, curve.CurveType.SINE, 1],
                         [-3.5, 8.0, curve.CurveType.HOLD, 0]])
    y_pos = curve.Curve([[3.5, 0.0, curve.CurveType.COSINE, 1],
                         [-3.5, 8.0, curve.CurveType.HOLD, 0]])
    z_rot = curve.Curve([[360.0, 0.0, curve.CurveType.LINEAR, 2],
                         [0.0, 8.0, curve.CurveType.LINEAR, 2]])

    camera.transform.set_position(x_pos, y_pos, 0)
    camera.transform.set_rotation(0, 0, z_rot)

    mesh = Mesh.from_stl("../unit_cube.stl", np.array([1.0, 0.0, 1.0]),\
        np.array([1.0, 1.0, 1.0]),0.05,1.0,0.5,1000)
    mesh.transform.set_position(0, -.5, .5)
    mesh.transform.set_rotation(15, 0, 200)

    mesh2 = Mesh.from_stl("../unit_cube.stl", np.array([1.0, 0.0, 1.0]),\
        np.array([1.0, 1.0, 1.0]),0.05,1.0,0.5,1000)
    mesh2.transform.set_position(0, -.5, .5)
    mesh2.transform.set_rotation(0, 45, 60)

    mesh3 = Mesh.from_stl("../unit_sphere.stl", np.array([1.0, 0.0, 1.0]), \
                          np.array([1.0, 1.0, 1.0]), 0.05, 1.0, 0.5, 1000)
    mesh3.transform.set_position(.5, 0, -.5)

    light = PointLight(50.0, np.array([1, 1, 1]))
    light.transform.set_position(0, -5, 5)

    renderer = Renderer(screen, camera, [mesh, mesh2, mesh3], light)
    animate.run_animation(renderer, RenderAlgorithm.NONE, [80,80,80], [0.2, 0.2, 0.2], 8, 8)

    screen.show()
