import math
import pygame


class Robot:
    def __init__(self, starting_angle=0, size=30) -> None:
        self.size = size
        self.image = pygame.image.load("robot.png")
        self.image = pygame.transform.scale(self.image, (self.size, self.size))
        self.rect = self.image.get_rect()
        self.dowel_length = 20
        self.dowel_width = 2
        self.speed = 1
        self.angle = starting_angle
        self.entered_grid = False

    def get_size(self) -> int:
        return self.size

    def set_angle(self, angle) -> None:
        self.angle = angle

    def get_angle(self) -> int:
        return self.angle

    def increase_angle(self, interval=None) -> None:
        if interval is None:
            self.angle += 1

        else:
            self.angle += interval

    def decrease_angle(self, interval=None) -> None:
        if interval is None:
            self.angle -= 1

        else:
            self.angle -= interval

    def get_entered_grid(self) -> bool:
        return self.entered_grid

    def set_entered_grid(self) -> None:
        self.entered_grid = True

    def get_location(self) -> (int, int):
        return (self.x, self.y)

    def set_location(self, x, y) -> None:
        self.x, self.y = x, y

    def get_speed(self) -> int:
        return self.speed

    def increase_speed(self, interval=None) -> None:
        if interval is None:
            self.speed += 1

        else:
            self.speed += interval

    def decrease_speed(self, interval=None) -> None:
        if interval is None:
            self.speed -= 1

        else:
            self.speed -= interval

    def get_front_location(self) -> (int, int):
        front_x = self.x + self.size / 2
        front_y = self.y + self.size / 2

        return (front_x, front_y)

    def get_dowel_location(self) -> (int, int):
        front_x, front_y = self.get_front_location()
        front_end_x = front_x + self.dowel_length * math.cos(math.radians(self.angle))
        front_end_y = front_y + self.dowel_length * math.sin(math.radians(self.angle))

        return (front_end_x, front_end_y)

    def get_dowel_width(self) -> int:
        return self.dowel_width
