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

    x_pos = curve.Curve([[2.5, 0.0, curve.CurveType.SINE, 1],
                         [-2.5, 8.0, curve.CurveType.HOLD, 0]])
    y_pos = curve.Curve([[2.5, 0.0, curve.CurveType.COSINE, 1],
                         [-2.5, 8.0, curve.CurveType.HOLD, 0]])
    z_rot = curve.Curve([[360.0, 0.0, curve.CurveType.LINEAR, 2],
                         [0.0, 8.0, curve.CurveType.LINEAR, 2]])


    # x_pos = curve.Curve([[0.0, 0.0, curve.CurveType.ROOT, 2],
    #                      [-2.5, 2.0, curve.CurveType.EXPONENTIAL, 2],
    #                      [0.0, 4.0, curve.CurveType.ROOT, 2],
    #                      [2.5, 6.0, curve.CurveType.EXPONENTIAL, 2],
    #                      [0.0, 8.0, curve.CurveType.ROOT, 2]])
    # y_pos = curve.Curve([[-2.5, 0.0, curve.CurveType.EXPONENTIAL, 2],
    #                      [0.0, 2.0, curve.CurveType.ROOT, 2],
    #                      [2.5, 4.0, curve.CurveType.EXPONENTIAL, 2],
    #                      [0.0, 6.0, curve.CurveType.ROOT, 2],
    #                      [-2.5, 8.0, curve.CurveType.EXPONENTIAL, 2]])


    camera.transform.set_position(x_pos, y_pos, 0)
    camera.transform.set_rotation(0, 0, z_rot)

    mesh = Mesh.from_stl("../unit_cube.stl", np.array([1.0, 0.0, 1.0]),\
        np.array([1.0, 1.0, 1.0]),0.05,1.0,0.5,1000)
    mesh.transform.set_rotation(15, 0, 200)

    light = PointLight(50.0, np.array([1, 1, 1]))
    light.transform.set_position(0, -5, 5)

    renderer = Renderer(screen, camera, [mesh], light)
    animate.run_animation(renderer, RenderAlgorithm.FLAT, [80,80,80], [0.2, 0.2, 0.2], 4, 8)

    screen.show()

    # for i in range(4*8+1):
    #     print(str(i/4) + " : " + str(x_pos.interpolate(i/4)) + " : " + str(y_pos.interpolate(i/4)) + " : " + str(z_rot.interpolate(i/4)))
