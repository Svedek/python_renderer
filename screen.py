import numpy as np
import pygame


class Screen:
    # Takes two integers as arguments: width and height.
    # These two arguments define the size and shape of the resulting image.
    def __init__(self, width: int, height: int):
        if width <= 0 or height <= 0:
            raise ValueError("Width or height is 0 or less!")
        self.width = width
        self.height = height

        pygame.init()
        self.display = pygame.display.set_mode([width, height])

    # Returns a float that is the ratio of the screen's width to height.
    # That is, if the screen width is 100px and the screen height is 50px, then this method would return 2.0.
    def ratio(self):
        return self.display.get_width() / self.display.get_height()

    #  Takes a buffer of color values. The buffer should be a 3-dimensional numpy array
    #  with shape (width, height, 3), where width and height are specified in the __init__ call.
    #  The value 3 is because there are three values for each color (red, blue, and green).
    #  An exception should be thrown if the incoming buffer is of a different shape.
    #  You should somehow transfer the values in the incoming buffer array to a pygame instance.
    def draw(self, buffer: np.ndarray):
        window_size = (self.display.get_width(), self.display.get_height(), 3)
        if window_size != buffer.shape:
            raise ValueError("Input buffer is of invalid shape!")

        buffer = np.fliplr(buffer)

        pygame.pixelcopy.array_to_surface(self.display, buffer)
        pygame.display.update()

    # enters the main event loop and prevents the window from closing right away.
    # The window should close when the pygame.QUIT event is triggered.
    def show(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

        pygame.quit()

    def save_screen(self, file_path):
        pygame.image.save(self.display, file_path)