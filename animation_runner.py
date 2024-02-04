import os
import glob
import contextlib
from PIL import Image


def run_animation(renderer, shading, bg_color, ambient_light, fps, time):
    frames = int(fps * time)
    filenamelist = [0] * frames

    path = "animations/"
    if not os.path.exists(path):
        os.mkdir(path)

    for i in range(frames):
        frame_time = i / fps
        print("Frame: " + str(i) + " at time: " + str(frame_time))
        frame = renderer.render(shading, bg_color, ambient_light, frame_time)

        filenamelist[i] = path + "frame_" + f"{i:03}" + ".png"
        renderer.screen.save_screen(filenamelist[i])


    # filepaths
    fp_in = path + "frame_*.png"
    fp_out = path + "image.gif"

    dur = max(int(1000/fps), 1)

    # use exit stack to automatically close opened images
    with contextlib.ExitStack() as stack:

        imgs = (stack.enter_context(Image.open(f))
                for f in sorted(glob.glob(fp_in)))

        img = next(imgs)

        img.save(fp=fp_out, format='GIF', append_images=imgs,
                 save_all=True, duration=dur, loop=0)

    for frame in filenamelist:
        os.remove(frame)

    print("\nAnimation saved to: " + os.getcwd() + "\\" + fp_out.replace("/", "\\"))
