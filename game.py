import math
import time
import pygame
import random
import sys
from board import Board
from judge import Judge
from robot import Robot


# Set up colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
END_RUN_TEXT = None


class Game:
    def __init__(self) -> None:
        # Initialize Pygame
        pygame.init()

        # Set up fonts
        self.font = pygame.font.Font(None, 36)
        self.timer_font = pygame.font.Font(None, 24)
        self.score_font = pygame.font.Font(None, 24)

        # Main game loop
        self.clock = pygame.time.Clock()

        # Create robot instance
        self.robot = Robot()

        # Create the Pygame window
        self.window_width = 1000
        self.window_height = 1000
        self.window = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption("Robot Tour")

        # Create board instance
        self.grid_size = 4
        self.board = Board(self.window)

        # Highlight specified zones
        self.board.set_bonus_zones()

        self.set_up_robot()

        # Timer variables
        # Random target time between 50 and 75 seconds
        self.target_time = random.randint(50, 75) * 1000
        self.timer_running = False
        start_time = 0

        # Create judge
        self.judge = Judge(self.board, self.robot, start_time, self.target_time)

        # Start scoring
        self.zone_scores = {
            zone: False for zone in range(1, self.board.get_grid_size() ** 2 + 1)
        }

    def is_collision(self, x, y) -> int:
        """
        Determines if there is a collision between the robot and the board's border or blockades

        param board: Board object
        param robot: Robot object
        param x: hypothetical x-coordinate of the robot
        param y: hypothetical y-coordinate of the robot

        return: collision type - 0 for no collision, 1 for blockade, 2 for border or non-penalty blockade
        """

        cell_size = self.board.get_cell_size()
        grid_size = self.board.get_grid_size()
        grid_start_x, grid_start_y = self.board.get_grid_start()
        robot_size = self.robot.get_size()

        # Allow to robot to enter the grid
        if not self.robot.get_entered_grid() and (
            (x > grid_start_x)
            and (y > grid_start_y)
            and ((x + robot_size) < grid_start_x + cell_size * grid_size)
            and ((y + robot_size) < grid_start_y + cell_size * grid_size)
        ):
            self.robot.set_entered_grid()

        # Check if the robot is hitting a blockade
        for location in self.board.get_blockades().keys():
            bx = (location[0] - 1) % grid_size
            by = (location[0] - 1) // grid_size
            blockade_size = self.board.get_blockade_size()
            cardinality = location[1]

            collision = False

            if cardinality == "N":
                blockade_x_start = grid_start_x + bx * cell_size
                blockade_x_end = blockade_x_start + cell_size
                blockade_y_start = blockade_y_end = grid_start_y + by * cell_size

            elif cardinality == "E":
                blockade_x_start = blockade_x_end = grid_start_x + (bx + 1) * cell_size
                blockade_y_start = grid_start_y + by * cell_size
                blockade_y_end = blockade_y_start + cell_size

            elif cardinality == "S":
                blockade_x_start = grid_start_x + bx * cell_size
                blockade_x_end = blockade_x_start + cell_size
                blockade_y_start = blockade_y_end = grid_start_y + (by + 1) * cell_size

            elif cardinality == "W":
                blockade_x_start = blockade_x_end = grid_start_x + bx * cell_size
                blockade_y_start = grid_start_y + by * cell_size
                blockade_y_end = blockade_y_start + cell_size

            if (
                ((blockade_x_start - (x + robot_size)) < blockade_size)
                and ((x - blockade_x_end) < blockade_size)
                and ((blockade_y_start - (y + robot_size)) < blockade_size)
                and ((y - blockade_y_end) < blockade_size)
            ):
                collision = True

            if collision:
                if not self.board.get_blockades()[location]:
                    self.board.hit_blockade(location)
                    return 1
                else:
                    return 2

        # Check if the robot is outside the grid
        if self.robot.get_entered_grid() and (
            (x <= grid_start_x)
            or (y <= grid_start_y)
            or ((x + robot_size) >= (grid_start_x + cell_size * grid_size))
            or ((y + robot_size) >= (grid_start_y + cell_size * grid_size))
        ):
            return 2

        return 0

    def end_run(self):
        global END_RUN_TEXT
        # TODO: fix font and styling
        """
        Function to end the run and display the final score

        param board: Board object
        param judge: Judge object
        param target_time: Target time for the run
        param winner_text: Text to display when the run ends

        return: final score of the run
        """

        score = self.judge.get_final_score()

        # Display text and end the game
        if END_RUN_TEXT is None:
            END_RUN_TEXT = self.font.render("Run over", True, BLACK)
        self.board.window.blit(
            END_RUN_TEXT,
            (
                self.board.window.get_width() // 2 - 50,
                self.board.window.get_height() // 2 - 18,
            ),
        )

        # Display the target time and final score
        target_time_text2 = self.timer_font.render(
            f"Target Time: {round(self.target_time / 1000, 2)} seconds", True, BLACK
        )
        final_score_text = self.timer_font.render(
            f"Final Score: {max(score, 0)}", True, BLACK
        )

        self.board.window.blit(
            target_time_text2,
            (
                self.board.window.get_width() // 2 - 90,
                self.board.window.get_height() // 2 + 18,
            ),
        )
        self.board.window.blit(
            final_score_text,
            (
                self.board.window.get_width() // 2 - 80,
                self.board.window.get_height() // 2 + 48,
            ),
        )

        # Update the display before quitting
        pygame.display.flip()

        # Wait for 5 seconds (5000 milliseconds)
        pygame.time.wait(5000)

        # Quit the game
        pygame.quit()

        return score

    def set_up_robot(self):
        robot_start_x, robot_start_y = self.board.get_starting_point()
        self.robot.set_location(robot_start_x, robot_start_y)
        self.robot.set_angle(self.board.get_starting_angle())
        self.last_movement = time.time()

        return None

    def run(self):
        # Main game loop
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                # Check for key events to adjust speed
                if event.type == pygame.KEYDOWN:
                    # Increase speed when 's' key is pressed
                    if event.key == pygame.K_s:
                        self.robot.increase_speed()

                    # Decrease speed when 'd' key is pressed (minimum speed is 1)
                    elif event.key == pygame.K_d and self.robot.get_speed() > 1:
                        self.robot.decrease_speed()

                    # End run when 'r' key is pressed
                    elif event.key == pygame.K_r:
                        return self.end_run()

            # Check for arrow key presses
            keys = pygame.key.get_pressed()

            # Left and right control the robot angle
            if keys[pygame.K_LEFT]:
                if not self.timer_running:
                    self.timer_running = True
                    start_time = pygame.time.get_ticks()
                self.robot.decrease_angle()
            if keys[pygame.K_RIGHT]:
                if not self.timer_running:
                    self.timer_running = True
                    start_time = pygame.time.get_ticks()
                self.robot.increase_angle()

            # Up and down control the robot movement
            if keys[pygame.K_UP]:
                if not self.timer_running:
                    self.timer_running = True
                    start_time = pygame.time.get_ticks()

                # Calculate the movement based on the front angle
                new_x = robot_x + self.robot.get_speed() * math.cos(
                    math.radians(self.robot.get_angle())
                )
                new_y = robot_y + self.robot.get_speed() * math.sin(
                    math.radians(self.robot.get_angle())
                )

                collision = self.is_collision(new_x, new_y)

                if collision == 0:
                    self.robot.set_location(new_x, new_y)
                    self.last_movement = time.time()

                elif collision == 1:
                    self.judge.update_score(50)

            if keys[pygame.K_DOWN]:
                if not self.timer_running:
                    self.timer_running = True
                    start_time = pygame.time.get_ticks()

                # Calculate the movement based on the front angle
                new_x = robot_x - self.robot.get_speed() * math.cos(
                    math.radians(self.robot.get_angle())
                )
                new_y = robot_y - self.robot.get_speed() * math.sin(
                    math.radians(self.robot.get_angle())
                )

                collision = self.is_collision(new_x, new_y)

                if collision == 0:
                    self.robot.set_location(new_x, new_y)
                    self.last_movement = time.time()

                elif collision == 1:
                    self.judge.update_score(50)

            # Clear the screen
            self.board.window.fill(WHITE)

            # Draw the target endpoint
            pygame.draw.circle(self.board.window, RED, self.board.target_point, 10)

            # Draw the speed information
            speed_text = self.font.render(
                f"Speed: {self.robot.get_speed()}", True, BLACK
            )
            self.board.window.blit(speed_text, (10, 70))

            # Draw the speed information
            target_time_text = self.font.render(
                f"Target time: {self.target_time / 1000}", True, BLACK
            )
            self.board.window.blit(target_time_text, (10, 100))

            # Draw the board
            self.board.draw()

            # Get location of robot
            robot_location = self.robot.get_location()
            robot_x = robot_location[0]
            robot_y = robot_location[1]

            # Draw the robots
            rotated_robot = pygame.transform.rotate(self.robot.image, self.robot.angle)
            rotated_rect = rotated_robot.get_rect(
                center=(robot_x + self.robot.size / 2, robot_y + self.robot.size / 2)
            )
            self.board.window.blit(rotated_robot, rotated_rect.topleft)

            # Draw the front of the robot
            pygame.draw.line(
                self.board.window,
                RED,
                self.robot.get_front_location(),
                self.robot.get_dowel_location(),
                self.robot.get_dowel_width(),
            )

            self.target_point = self.board.get_target_point()

            # Check if the robot is in a highlighted zone and award points
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
                self.judge.update_score(-15)
                self.board.hit_bonus_zone(current_zone)

            # Draw the timer
            if self.timer_running:
                elapsed_time = pygame.time.get_ticks() - start_time
                elapsed_time_sec = elapsed_time // 1000
                elapsed_time_ms = elapsed_time % 1000
                timer_text = self.timer_font.render(
                    f"Time: {elapsed_time_sec}.{elapsed_time_ms} seconds", True, BLACK
                )
                self.board.window.blit(timer_text, (10, 10))

                # Draw the score
                score_text = self.score_font.render(
                    f"Score: {self.judge.get_score()}", True, BLACK
                )
                self.board.window.blit(score_text, (10, 40))

            # Update the display
            pygame.display.flip()

            # Control the frame rate
            self.clock.tick(60)
