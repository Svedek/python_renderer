from screen import Screen
from camera import PerspectiveCamera, OrthoCamera
from light import PointLight
from mesh import Mesh
import animation_curve as curve
from renderer import Renderer, RenderAlgorithm
import animation_runner as animate


if __name__ == '__main__':
    # Defines a 500 by 500 canvas for the image
    screen = Screen(500, 500)

    # A camera can be either an OrthoCamera (orthographic) or PerspectiveCamera, both use the same arguments
    # Defines a camera with the bounding box of (left, right, bottom, top, near, far)
    camera = PerspectiveCamera(-1.0, 1.0, -1.0, 1.0, 1.0, 10)
    camera.transform.set_position(0, -2.5, 1)

    # Defines a light with arguments (intensity, color[r, g, b] with values between 0 and 1)
    light = PointLight(50.0, [1, 1, 1])

    # Defines a mesh with arguments (filepath to stlfile, diffuse color, specular color, ambient componenet, diffuse component, specular componenet, phong exponent)
    mesh_1 = Mesh.from_stl("../unit_sphere.stl", [1.0, 0.0, 1.0], [1.0, 1.0, 1.0], 0.05, 1.0, 0.5, 100)
    mesh_2 = Mesh.from_stl("../unit_cube.stl", [0.0, 1.0, 0.0], [1.0, 1.0, 1.0], 0.05, 1.0, 0.5, 1000)


    # Setting the positions to a static, non-animated value
    camera.transform.set_position(0, -2.5, 1)
    mesh_2.transform.set_position(0.0, 2.5, 0)
    light.transform.set_position(0, -5, 5)

    # Define an animation curve each keyframe is defined as a list of arguments inside of a list:
    # ([[value_1, time_frame_begins_1, curve_interpolation_type_1, curve_interpolation_value_1],  # Keyframe 1
    #   [value_2, time_frame_begins_2, curve_interpolation_type_2, curve_interpolation_value_2]])  # Keyframe 2
    x_curve = curve.Curve([[-5.0, 0.0, curve.CurveType.LINEAR, 2],  # Start at -5 x
                           [5.0, 2.0, curve.CurveType.HOLD, 2]]) # Linear movement to 5 x over 2 seconds

    mesh_1.transform.set_position(x_curve, 2.5, 0)


    # Creating a render requires the scene objects (screen, camera, [meshs], light)
    renderer = Renderer(screen, camera, [mesh_1, mesh_2], light)

    # Running the animation requires a render style (enum value shown here) and other render and animation specifications
    # (renderer, shading type, background color [r, g, b] int from 0 to 255, ambient light value [r, g, b] float from 0 to 1, frames per second, animation time)
    animate.run_animation(renderer, RenderAlgorithm.PHONG, [80,80,80], [0.4, 0.4, 0.4], 8, 2)
