import os
import pygame

os.environ["SDL_VIDEODRIVER"] = "dummy"

# Initialize Pygame
pygame.init()

# Initialize the joystick module
pygame.joystick.init()

# Get the first joystick connected to the computer
joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
print(joysticks[0].get_id(), joysticks[0].get_guid(), joysticks[0].get_instance_id())
joystick = pygame.joystick.Joystick(0)
joystick.init()

# Main game loop
while True:
    # Check for Pygame events
    for event in pygame.event.get():
        # Check for joystick events
        if event.type == pygame.JOYAXISMOTION:
            # Read the values of the joystick axes
            x_axis = joystick.get_axis(0)
            y_axis = joystick.get_axis(1)
            print("X axis: ", x_axis)
            print("Y axis: ", y_axis)
        elif event.type == pygame.JOYBUTTONDOWN:
            # Read the index of the button that was pressed
            button_index = event.button
            print("Button ", button_index, " pressed")
        elif event.type == pygame.JOYBUTTONUP:
            # Read the index of the button that was released
            button_index = event.button
            print("Button ", button_index, " released")
