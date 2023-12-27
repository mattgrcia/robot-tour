import math
import time
import pygame
import random
import sys
from board import Board
from judge import Judge
from robot import Robot

# Initialize Pygame
pygame.init()

# Set up colors
white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)

# set up fonts
font = pygame.font.Font(None, 36)
timer_font = pygame.font.Font(None, 24)
score_font = pygame.font.Font(None, 24)

# To store the "Winner!" text
winner_text = None

# Main game loop
clock = pygame.time.Clock()

# create robot instance
robot = Robot()

# Create the Pygame window
window_width = 1000
window_height = 1000
window = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("Robot Tour")

# create board instance
grid_size = 4
blockades = {
    (2, "A"): False,
    (5, "B"): False,
    (8, "C"): False,
    (11, "D"): False,
    (13, "A"): False,
    (14, "B"): False,
    (16, "C"): False,
    (3, "D"): False,
}

board = Board(window, blockades)

# Timer variables
# Random target time between 50 and 75 seconds
target_time = random.randint(50, 75) * 1000
timer_running = False
start_time = 0

# create judge
judge = Judge(board, robot, start_time, target_time)

# Start scoring
zone_scores = {zone: False for zone in range(1, board.get_grid_size() ** 2 + 1)}


def is_collision(board: Board, robot: Robot, x, y) -> int:
    """
    Determines if there is a collision between the robot and the board's border or blockades

    param board: Board object
    param robot: Robot object

    return: collision type - 1 for blockade, 2 for border, 0 for no collision
    """

    cell_size = board.get_cell_size()
    grid_size = board.get_grid_size()
    grid_start_x, grid_start_y = board.get_grid_start()
    starting_point_x, starting_point_y = board.get_starting_point()

    robot_size = robot.get_size()

    # Check if the robot is outside the grid
    if ((abs(x - starting_point_x) > 20) and abs((y - starting_point_y) > 20)) and (
        x < grid_start_x
        or x + robot_size > window_width - grid_start_x
        or y < grid_start_y
        or y + robot_size > window_height - grid_start_y
    ):
        return 2

    # Check if the robot is hitting a blockade
    for location in board.get_blockades().keys():
        bx = (location[0] - 1) % grid_size
        by = (location[0] - 1) // grid_size

        if (
            location[1] == "A"
            and x < (bx + 1) * cell_size + grid_start_x
            and x + robot_size > bx * cell_size + grid_start_x
            and y < by * cell_size + grid_start_y + 5
            and y + robot_size > by * cell_size + grid_start_y
        ):
            return 1
        elif (
            location[1] == "B"
            and x < (bx + 1) * cell_size + grid_start_x + 5
            and x + robot_size > (bx + 1) * cell_size + grid_start_x
            and y < (by + 1) * cell_size + grid_start_y
            and y + robot_size > by * cell_size + grid_start_y
        ):
            return 1
        elif (
            location[1] == "C"
            and x < bx * cell_size + grid_start_x
            and x + robot_size > (bx + 1) * cell_size + grid_start_x
            and y < (by + 1) * cell_size + grid_start_y
            and y + robot_size > (by + 1) * cell_size + grid_start_y
        ):
            return 1
        elif (
            location[1] == "D"
            and x < bx * cell_size + grid_start_x + 5
            and x + robot_size > bx * cell_size + grid_start_x
            and y < by * cell_size + grid_start_y + 5
            and y + robot_size > by * cell_size + grid_start_y
        ):
            return 1

    return 0


def end_run(board: Board, judge: Judge, target_time: int, winner_text: str):
    """
    Function to end the run and display the final score

    param board: Board object
    param judge: Judge object
    param target_time: Target time for the run
    param winner_text: Text to display when the run ends

    return: final score of the run
    """

    score = judge.get_final_score()

    # Display "Winner!" text and end the game
    if winner_text is None:
        winner_text = font.render("Run over", True, black)
    board.window.blit(
        winner_text,
        (board.window.get_width() // 2 - 50, board.window.get_height() // 2 - 18),
    )

    # Display the target time and final score
    target_time_text2 = timer_font.render(
        f"Target Time: {round(target_time / 1000, 2)} seconds", True, black
    )
    final_score_text = timer_font.render(f"Final Score: {max(score, 0)}", True, black)

    board.window.blit(
        target_time_text2,
        (board.window.get_width() // 2 - 90, board.window.get_height() // 2 + 18),
    )
    board.window.blit(
        final_score_text,
        (board.window.get_width() // 2 - 80, board.window.get_height() // 2 + 48),
    )

    # Update the display before quitting
    pygame.display.flip()

    # Wait for 5 seconds (5000 milliseconds)
    pygame.time.wait(5000)

    # Quit the game
    pygame.quit()

    # Print the final score
    print(score)

    return score


# robot setup
robot_start_x, robot_start_y = board.get_starting_point()
robot.set_location(robot_start_x, robot_start_y)
robot.set_angle(board.get_starting_angle())
last_movement = time.time()

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
                robot.increase_speed()

            # Decrease speed when 'd' key is pressed (minimum speed is 1)
            elif event.key == pygame.K_d and robot.get_speed() > 1:
                robot.decrease_speed()

            # End run when 'r' key is pressed
            elif event.key == pygame.K_r:
                end_run(board, judge, target_time, winner_text)

    # Check for arrow key presses
    keys = pygame.key.get_pressed()

    # Left and right control the robot angle
    if keys[pygame.K_LEFT]:
        if not timer_running:
            timer_running = True
            start_time = pygame.time.get_ticks()
        robot.decrease_angle()
    if keys[pygame.K_RIGHT]:
        if not timer_running:
            timer_running = True
            start_time = pygame.time.get_ticks()
        robot.increase_angle()

    # Up and down control the robot movement
    if keys[pygame.K_UP] or keys[pygame.K_DOWN]:
        if not timer_running:
            timer_running = True
            start_time = pygame.time.get_ticks()

        # Calculate the movement based on the front angle
        new_x = robot_x + robot.get_speed() * math.cos(math.radians(robot.get_angle()))
        new_y = robot_y + robot.get_speed() * math.sin(math.radians(robot.get_angle()))

        # TODO: check instead to see if the robot would collide with the blockade,
        # but don't actually move the robot
        # mark any hit blockades so that the contact penalty is not duplicated

        collision = is_collision(board, robot, new_x, new_y)

        if collision == 0:
            robot.set_location(new_x, new_y)
            last_movement = time.time()

        elif collision == 1:
            judge.update_score(50)

    # Clear the screen
    board.window.fill(white)

    # Draw the target endpoint
    pygame.draw.circle(board.window, red, board.target_point, 10)

    # Draw the speed information
    speed_text = font.render(f"Speed: {robot.get_speed()}", True, black)
    board.window.blit(speed_text, (10, 70))

    # Draw the speed information
    target_time_text = font.render(f"Target time: {target_time / 1000}", True, black)
    board.window.blit(target_time_text, (10, 100))

    # Highlight specified zones
    bonus_zones = [4, 10, 15]
    board.set_bonus_zones(bonus_zones)

    # Draw the board
    board.draw(blockades)

    # get location of robot
    robot_location = robot.get_location()
    robot_x = robot_location[0]
    robot_y = robot_location[1]

    # Draw the robot
    rotated_robot = pygame.transform.rotate(robot.image, robot.angle)
    rotated_rect = rotated_robot.get_rect(
        center=(robot_x + robot.size / 2, robot_y + robot.size / 2)
    )
    board.window.blit(rotated_robot, rotated_rect.topleft)

    # draw the front of the robot
    pygame.draw.line(
        board.window,
        red,
        robot.get_front_location(),
        robot.get_dowel_location(),
        robot.get_dowel_width(),
    )

    target_point = board.get_target_point()

    # Check if the robot is in a highlighted zone and award points
    current_zone = (
        (robot_x - board.grid_start_x) // board.cell_size
        + ((robot_y - board.grid_start_y) // board.cell_size) * board.grid_size
        + 1
    )

    if current_zone in bonus_zones and not zone_scores[current_zone]:
        judge.update_score(-15)
        zone_scores[current_zone] = True

    # Draw the timer
    if timer_running:
        elapsed_time = pygame.time.get_ticks() - start_time
        elapsed_time_sec = elapsed_time // 1000
        elapsed_time_ms = elapsed_time % 1000
        timer_text = timer_font.render(
            f"Time: {elapsed_time_sec}.{elapsed_time_ms} seconds", True, black
        )
        board.window.blit(timer_text, (10, 10))

        # Draw the score
        score_text = score_font.render(f"Score: {judge.get_score()}", True, black)
        board.window.blit(score_text, (10, 40))

    # Update the display
    pygame.display.flip()

    # Control the frame rate
    clock.tick(60)
