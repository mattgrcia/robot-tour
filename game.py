import math
import random
import sys
import time
import numpy as np
import pygame
from torchvision import transforms
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

        # Create the Pygame window
        self.window_width = 1000
        self.window_height = 1000
        self.window = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption("Robot Tour")

        # Create a surface for drawing
        self.surface = pygame.Surface((self.window_width, self.window_height))

        # Create board
        self.grid_size = 4
        self.board = Board(self.window, self.surface)
        self.target_point = self.board.get_target_point()

        # Create robot
        self.robot = Robot(self.surface)
        self.robot.set_location(self.board.get_starting_point())
        self.robot.set_angle(self.board.get_starting_angle())

        # Timer variables - random target time between 50 and 75 seconds
        self.target_time = random.randint(50, 75) * 1000
        self.timer_running = True
        self.last_movement = pygame.time.get_ticks()

        # Create judge
        self.judge = Judge(self.board, self.robot, self.target_time)

        self.game_over = False

    def is_over(self) -> bool:
        return self.game_over

    @staticmethod
    def preprocess_image(surface, output_size=(64, 64), normalize=True):
        # Convert Pygame surface to a NumPy array
        image = np.array(pygame.surfarray.pixels3d(surface))

        # Define transformation pipeline
        transform_pipeline = transforms.Compose(
            [
                transforms.ToPILImage(),  # Convert array to PIL image
                transforms.Resize(output_size),  # Resize to the desired size
                # Uncomment the next line if you want to convert to grayscale
                # transforms.Grayscale(),
                transforms.ToTensor(),  # Convert to PyTorch tensor
            ]
        )

        if normalize:
            # Normalize the image to [0, 1]
            transform_pipeline.transforms.append(
                transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
            )

        # Apply transformations
        image = transform_pipeline(image)

        return image

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

    def end_run(self) -> float:
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
        self.surface.blit(
            END_RUN_TEXT,
            (
                self.surface.get_width() // 2 - 50,
                self.surface.get_height() // 2 - 18,
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
                self.surface.get_width() // 2 - 90,
                self.surface.get_height() // 2 + 18,
            ),
        )
        self.board.window.blit(
            final_score_text,
            (
                self.surface.get_width() // 2 - 80,
                self.surface.get_height() // 2 + 48,
            ),
        )

        # Update the display before quitting
        pygame.display.flip()

        # Wait for 5 seconds (5000 milliseconds)
        pygame.time.wait(5000)

        # Quit the game
        pygame.quit()

        self.game_over = True

        return score

    def get_state(self) -> dict:
        time_to_target = np.array(pygame.time.get_ticks() - self.target_time)
        board_image = self.preprocess_image(self.surface)

        return {
            "board_image": board_image,
            "time": time_to_target,
        }

    def render(self) -> None:
        # Clear the screen
        self.surface.fill(WHITE)

        # Draw the target endpoint
        pygame.draw.circle(self.surface, RED, self.board.target_point, 10)

        # Draw the speed information
        speed_text = self.font.render(f"Speed: {self.robot.get_speed()}", True, BLACK)
        self.window.blit(speed_text, (10, 70))

        # Draw the time information
        target_time_text = self.font.render(
            f"Target time: {self.target_time / 1000}", True, BLACK
        )
        self.window.blit(target_time_text, (10, 100))

        self.judge.check_bonus_zones()

        # Draw the board and robot
        self.board.draw()
        self.robot.draw()

        # Blit the render_surface onto the main window
        self.window.blit(self.surface, (0, 0))
        pygame.display.flip()  # Update the entire display

        # Draw the timer
        if self.timer_running:
            elapsed_time = pygame.time.get_ticks()
            # End the run if the robot has not entered the grid after 10 seconds
            if (not self.robot.get_entered_grid()) and ((elapsed_time // 1000) > 10):
                return self.end_run()

            # End the run if the robot does not move forward or backward for three seconds
            if ((pygame.time.get_ticks() - self.last_movement) // 1000) > 3:
                return self.end_run()

            elapsed_time_sec = elapsed_time // 1000
            elapsed_time_ms = elapsed_time % 1000
            timer_text = self.timer_font.render(
                f"Time: {elapsed_time_sec}.{elapsed_time_ms} seconds", True, BLACK
            )
            self.window.blit(timer_text, (10, 10))

            # Draw the score
            score_text = self.score_font.render(
                f"Score: {self.judge.get_score()}", True, BLACK
            )
            self.window.blit(score_text, (10, 40))

        # Update the display
        pygame.display.flip()

        # Control the frame rate
        self.clock.tick(60)

    def move_forward(self) -> None:
        robot_location = self.robot.get_location()
        robot_x = robot_location[0]
        robot_y = robot_location[1]

        # Calculate the movement based on the front angle
        new_x = robot_x + self.robot.get_speed() * math.cos(
            math.radians(self.robot.get_angle())
        )
        new_y = robot_y + self.robot.get_speed() * math.sin(
            math.radians(self.robot.get_angle())
        )

        collision = self.is_collision(new_x, new_y)

        if collision == 0:
            self.robot.set_location((new_x, new_y))
            self.last_movement = pygame.time.get_ticks()

        elif collision == 1:
            self.judge.update_score(50)

        return None

    def move_backward(self) -> None:
        robot_location = self.robot.get_location()
        robot_x = robot_location[0]
        robot_y = robot_location[1]

        # Calculate the movement based on the front angle
        new_x = robot_x - self.robot.get_speed() * math.cos(
            math.radians(self.robot.get_angle())
        )
        new_y = robot_y - self.robot.get_speed() * math.sin(
            math.radians(self.robot.get_angle())
        )

        collision = self.is_collision(new_x, new_y)

        if collision == 0:
            self.robot.set_location((new_x, new_y))
            self.last_movement = pygame.time.get_ticks()

        elif collision == 1:
            self.judge.update_score(50)

        return None

    def increase_angle(self) -> None:
        self.run_timer()
        self.robot.increase_angle()

        return None

    def decrease_angle(self) -> None:
        self.run_timer()
        self.robot.decrease_angle()

        return None

    def run(self, mode="human") -> None:
        if mode == "human":
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
                    self.decrease_angle()
                if keys[pygame.K_RIGHT]:
                    self.increase_angle()

                # Up and down control the robot movement
                if keys[pygame.K_UP]:
                    self.move_forward()
                if keys[pygame.K_DOWN]:
                    self.move_backward()

                # Check if the robot is in a bonus zone
                self.judge.check_bonus_zones()

                self.render()

                return None

        else:
            self.judge.check_bonus_zones()
            self.render()

            return None
