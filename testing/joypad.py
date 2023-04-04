import os
import pygame

os.environ["SDL_VIDEODRIVER"] = "dummy"

# Initialize Pygame
pygame.init()


JOYSTICKS = dict()
"""
for js_idx in range(pygame.joystick.get_count()):
    joystick = pygame.joystick.Joystick(js_idx)
    joystick.init()
    print(joystick)
    JOYSTICKS[js_idx] = joystick
"""

# Main game loop
while True:
    # Check for Pygame events

    for event in pygame.event.get():
        # Check for joystick events
        joystick_count = pygame.joystick.get_count()
        if event.type == pygame.JOYDEVICEADDED:
            joystick = pygame.joystick.Joystick(event.device_index)
            print(f"Joystick {joystick.get_instance_id()} connected")
            JOYSTICKS[joystick.get_instance_id()] = joystick

        if event.type == pygame.JOYDEVICEREMOVED:
            print(f"Joystick {event.instance_id} disconnected")
            del JOYSTICKS[event.instance_id]

        if event.type == pygame.JOYAXISMOTION:
            # Read the values of the joystick axes
            x_axis = joystick.get_axis(0)
            y_axis = joystick.get_axis(1)
            print("X axis: ", x_axis)
            print("Y axis: ", y_axis)
        elif event.type == pygame.JOYBUTTONDOWN:
            # Read the index of the button that was pressed
            button_index = event.button
            print(f"Joystick {event.instance_id} Button {button_index} pressed")
            print(pygame.joystick.get_count())
        elif event.type == pygame.JOYBUTTONUP:
            # Read the index of the button that was released
            button_index = event.button
            print(f"Joystick {event.instance_id} Button {button_index} pressed")
            print(f"Joystick count: {joystick_count}")
