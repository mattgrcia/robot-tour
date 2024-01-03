import math
import pygame
from board import Board
from robot import Robot


class Judge:
    def __init__(self, board: Board, robot: Robot, target_time):
        self.board = board
        self.robot = robot
        self.target_time = target_time
        self.score = 100

    def update_score(self, value):
        self.score += value

    def get_score(self):
        return self.score

    def get_final_score(self):
        return (
            self.score + self.calculate_time_score() + self.calculate_distance_score()
        )

    def calculate_distance_score(self):
        target_point = self.board.get_target_point()
        dowel_location = self.robot.get_dowel_location()
        score = math.sqrt(
            (dowel_location[0] - target_point[0]) ** 2
            + (dowel_location[1] - target_point[1]) ** 2
        )

        return score

    def calculate_elapsed_time(self):
        return pygame.time.get_ticks()

    # Calculate the score based on time difference
    def calculate_time_score(self):
        elapsed_time = self.calculate_elapsed_time()

        if self.target_time > elapsed_time:
            score = ((self.target_time - elapsed_time) / 1000) * 2
        else:
            score = (elapsed_time - self.target_time) / 1000

        return score

    def check_bonus_zones(self):
        # Check if the robot is in a highlighted zone and award points

        robot_location = self.robot.get_location()
        robot_x = robot_location[0]
        robot_y = robot_location[1]

        current_zone = (
            (robot_x - self.board.grid_start_x) // self.board.cell_size
            + ((robot_y - self.board.grid_start_y) // self.board.cell_size)
            * self.board.grid_size
            + 1
        )

        if (
            current_zone in self.board.get_bonus_zones()
            and not self.board.get_bonus_zones()[current_zone]
        ):
            self.score -= -15
            self.board.hit_bonus_zone(current_zone)
