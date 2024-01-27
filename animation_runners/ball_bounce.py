import numpy as np
from screen import Screen
from camera import PerspectiveCamera, OrthoCamera
from light import PointLight
from mesh import Mesh
import animation_curve as curve
from renderer import Renderer, RenderAlgorithm
import animation_runner as animate


if __name__ == '__main__':
    screen = Screen(500,500)

    camera = PerspectiveCamera(-1.0, 1.0, -1.0, 1.0, 1.0, 10)
    camera.transform.set_position(0, -2.5, 1)

    mesh = Mesh.from_stl("../unit_sphere.stl", [1.0, 0.0, 1.0], [1.0, 1.0, 1.0], 0.05, 1.0, 0.5, 1000)
    x_curve = curve.Curve([[-5.0, 0.0, curve.CurveType.LINEAR, 2], #Bounce at (-3,3) (0,1) (3,-1)
                           [6.0, 5.5, curve.CurveType.HOLD, 2]])
    z_curve = curve.Curve([[7.5, 0.0, curve.CurveType.EXPONENTIAL, 3],
                           [3.5, 1.0, curve.CurveType.ROOT, 3],
                           [5.5, 1.5, curve.CurveType.EXPONENTIAL, 3],
                           [1.5, 2.5, curve.CurveType.ROOT, 3],
                           [3.5, 3.0, curve.CurveType.EXPONENTIAL, 3],
                           [-0.5, 4.0, curve.CurveType.ROOT, 3],
                           [1.5, 4.5, curve.CurveType.EXPONENTIAL, 3],
                           [-3.5, 5.5, curve.CurveType.HOLD, 3]])
    mesh.transform.set_position(x_curve, 2.5, z_curve)

    plat1 = Mesh.from_stl("../unit_cube.stl", np.array([1.0, 0.0, 0.0]),\
        np.array([1.0, 1.0, 1.0]),0.05,1.0,0.5,1000)
    plat1.transform.set_position(-3.0, 2.5, 2.0)

    plat2 = Mesh.from_stl("../unit_cube.stl", np.array([0.0, 1.0, 0.0]),\
        np.array([1.0, 1.0, 1.0]),0.05,1.0,0.5,1000)
    plat2.transform.set_position(0.0, 2.5, 0)

    plat3 = Mesh.from_stl("../unit_cube.stl", np.array([0.0, 0.0, 1.0]),\
        np.array([1.0, 1.0, 1.0]),0.05,1.0,0.5,1000)
    plat3.transform.set_position(3.0, 2.5, -2.0)

    light = PointLight(50.0, np.array([1, 1, 1]))
    light.transform.set_position(0, -5, 5)

    renderer = Renderer(screen, camera, [mesh, plat1, plat2, plat3], light)
    animate.run_animation(renderer, RenderAlgorithm.PHONG, [80,80,80], [0.4, 0.4, 0.4], 8, 5.5)

    screen.show()
