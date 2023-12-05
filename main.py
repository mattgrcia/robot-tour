import math
import pygame
import random
import sys
from board import Board
from robot import Robot

# Initialize Pygame
pygame.init()

# Set up colors
white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)
green = (53, 94, 59)
brown = (165, 42, 42)

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
blockades = [
    (2, "A"),
    (5, "B"),
    (8, "C"),
    (11, "D"),
    (13, "A"),
    (14, "B"),
    (16, "C"),
    (3, "D"),
]

board = Board(window, blockades)

# Start scoring
score = 100
zone_scores = {zone: False for zone in range(1, board.get_grid_size() ** 2 + 1)}
contact_penalty = False

# Timer variables
# Random target time between 50 and 75 seconds
target_time = random.randint(50, 75) * 1000
timer_running = False
start_time = 0


def is_collision(board: Board, robot: Robot):
    # Check if the new position collides with blockades or the outside of the grid

    cell_size = board.get_cell_size()
    grid_size = board.get_grid_size()
    grid_start_x, grid_start_y = board.get_grid_start()
    starting_point_x, starting_point_y = board.get_starting_point()

    robot_size = robot.get_size()
    x, y = robot.get_location()

    for location in board.get_blockades():
        bx = (location[0] - 1) % grid_size
        by = (location[0] - 1) // grid_size

        if (
            location[1] == "A"
            and x < (bx + 1) * cell_size + grid_start_x
            and x + robot_size > bx * cell_size + grid_start_x
            and y < by * cell_size + grid_start_y + 5
            and y + robot_size > by * cell_size + grid_start_y
        ):
            return ("blockade", location)
        elif (
            location[1] == "B"
            and x < (bx + 1) * cell_size + grid_start_x + 5
            and x + robot_size > (bx + 1) * cell_size + grid_start_x
            and y < (by + 1) * cell_size + grid_start_y
            and y + robot_size > by * cell_size + grid_start_y
        ):
            return ("blockade", location)
        elif (
            location[1] == "C"
            and x < bx * cell_size + grid_start_x
            and x + robot_size > (bx + 1) * cell_size + grid_start_x
            and y < (by + 1) * cell_size + grid_start_y
            and y + robot_size > (by + 1) * cell_size + grid_start_y
        ):
            return ("blockade", location)
        elif (
            location[1] == "D"
            and x < bx * cell_size + grid_start_x + 5
            and x + robot_size > bx * cell_size + grid_start_x
            and y < by * cell_size + grid_start_y + 5
            and y + robot_size > by * cell_size + grid_start_y
        ):
            return ("blockade", location)

    # Check if the new position is outside the grid
    if ((abs(x - starting_point_x) > 20) and abs((y - starting_point_y) > 20)) and (
        x < grid_start_x
        or x + robot_size > window_width - grid_start_x
        or y < grid_start_y
        or y + robot_size > window_height - grid_start_y
    ):
        return ("outside", None)

    return (None, None)


def set_starting_angle(board: Board, robot: Robot):
    zone, side = board.get_starting_edge()

    if zone in [5, 9] or (zone in [1, 13] and side == "side"):
        angle = 0

    elif zone in [8, 12] or (zone in [4, 16] and side == "side"):
        angle = 180

    elif zone in [2, 3] or (zone in [1, 4] and side == "top"):
        angle = 90

    elif zone in [14, 15] or (zone in [13, 16] and side == "top"):
        angle = 270

    robot.set_angle(angle)

    return None


def set_starting_point(board: Board, robot: Robot):
    zone, side = board.get_starting_edge()
    grid_size = board.grid_size
    cell_size = board.cell_size
    grid_start_x, grid_start_y = board.grid_start_x, board.grid_start_y

    if zone in [5, 9] or (zone in [1, 13] and side == "side"):
        starting_point = (
            grid_start_x,
            grid_start_y + (cell_size * ((zone - 1) % grid_size) + cell_size / 2),
        )

    elif zone in [8, 12] or (zone in [4, 16] and side == "side"):
        starting_point = (
            grid_start_x + grid_size * cell_size,
            grid_start_y + (cell_size * ((zone - 1) % grid_size) + cell_size / 2),
        )

    elif zone in [2, 3] or (zone in [1, 4] and side == "top"):
        starting_point = (
            grid_start_x + (cell_size * ((zone - 1) % grid_size) + cell_size / 2),
            grid_start_y,
        )

    elif zone in [14, 15] or (zone in [13, 16] and side == "top"):
        starting_point = (
            grid_start_x + (cell_size * ((zone - 1) % grid_size) + cell_size / 2),
            grid_start_y + grid_size * cell_size,
        )

    robot.set_location(starting_point[0], starting_point[1])

    return None


set_starting_angle(board, robot)
set_starting_point(board, robot)


# Main game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Check for key events to adjust speed
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                robot.increase_speed()  # Increase speed when 's' key is pressed
            elif event.key == pygame.K_d and robot.get_speed() > 1:
                robot.decrease_speed()  # Decrease speed when 'd' key is pressed (minimum speed is 1)

    # Check for arrow key presses
    keys = pygame.key.get_pressed()
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
    if keys[pygame.K_UP]:
        if not timer_running:
            timer_running = True
            start_time = pygame.time.get_ticks()

        # Calculate the movement based on the front angle
        new_x = robot_x + robot.get_speed() * math.cos(math.radians(robot.get_angle()))
        new_y = robot_y + robot.get_speed() * math.sin(math.radians(robot.get_angle()))
        collision_type, collision_location = is_collision(board, robot)
        robot.set_location(new_x, new_y)

        if collision_type is None:
            robot.set_location(new_x, new_y)
        elif collision_type == "blockade" and not contact_penalty:
            score += 50
            contact_penalty = True

    if keys[pygame.K_DOWN]:
        if not timer_running:
            timer_running = True
            start_time = pygame.time.get_ticks()

        # Calculate the movement based on the front angle (opposite direction)
        new_x = robot_x - robot.get_speed() * math.cos(math.radians(robot.get_angle()))
        new_y = robot_y - robot.get_speed() * math.sin(math.radians(robot.get_angle()))

        collision_type, collision_location = is_collision(board, robot)
        if collision_type is None:
            robot.set_location(new_x, new_y)
        elif collision_type == "blockade" and not contact_penalty:
            score += 50
            contact_penalty = True

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

    # Check if the robot has reached the target point
    if (
        robot_x < target_point[0] + robot.size
        and robot_x + robot.size > target_point[0]
        and robot_y < target_point[1] + robot.size
        and robot_y + robot.size > target_point[1]
    ):
        # Calculate the elapsed time
        elapsed_time = pygame.time.get_ticks() - start_time

        # Display "Winner!" text and end the game
        if winner_text is None:
            winner_text = font.render("Run over", True, black)
        board.window.blit(
            winner_text, (board.window_width // 2 - 50, board.window_height // 2 - 18)
        )

        # Calculate the score based on time difference
        if target_time > elapsed_time:
            score += ((target_time - elapsed_time) / 1000) * 2
        else:
            score += (elapsed_time - target_time) / 1000

        # Display the target time and final score
        target_time_text2 = timer_font.render(
            f"Target Time: {round(target_time / 1000, 2)} seconds", True, black
        )
        final_score_text = timer_font.render(
            f"Final Score: {max(score, 0)}", True, black
        )

        board.window.blit(
            target_time_text2,
            (board.window_width // 2 - 90, board.window_height // 2 + 18),
        )
        board.window.blit(
            final_score_text,
            (board.window_width // 2 - 80, board.window_height // 2 + 48),
        )

        pygame.display.flip()  # Update the display before quitting
        pygame.time.wait(5000)  # Wait for 5 seconds (5000 milliseconds)
        pygame.quit()
        sys.exit()

    # Check if the robot is in a highlighted zone and award points
    current_zone = (
        (robot_x - board.grid_start_x) // board.cell_size
        + ((robot_y - board.grid_start_y) // board.cell_size) * board.grid_size
        + 1
    )

    if current_zone in bonus_zones and not zone_scores[current_zone]:
        score -= 15
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
        score_text = score_font.render(f"Score: {score}", True, black)
        board.window.blit(score_text, (10, 40))

    # Check if the robot has hit a blockade
    for location in blockades:
        x = (location[0] - 1) % board.grid_size
        y = (location[0] - 1) // board.grid_size

        if (
            location[1] == "A"
            and robot_x < (x + 1) * board.cell_size + board.grid_start_x
            and robot_x + robot.size > x * board.cell_size + board.grid_start_x
            and robot_y < y * board.cell_size + board.grid_start_y + 5
            and robot_y + robot.size > y * board.cell_size + board.grid_start_y
            and not contact_penalty
        ):
            score += 50
            contact_penalty = True
        elif (
            location[1] == "B"
            and robot_x < (x + 1) * board.cell_size + board.grid_start_x + 5
            and robot_x + robot.size > (x + 1) * board.cell_size + board.grid_start_x
            and robot_y < (y + 1) * board.cell_size + board.grid_start_y
            and robot_y + robot.size > y * board.cell_size + board.grid_start_y
            and not contact_penalty
        ):
            score += 50
            contact_penalty = True
        elif (
            location[1] == "C"
            and robot_x < x * board.cell_size + board.grid_start_x
            and robot_x + robot.size > (x + 1) * board.cell_size + board.grid_start_x
            and robot_y < (y + 1) * board.cell_size + board.grid_start_y
            and robot_y + robot.size > (y + 1) * board.cell_size + board.grid_start_y
            and not contact_penalty
        ):
            score += 50
            contact_penalty = True
        elif (
            location[1] == "D"
            and robot_x < x * board.cell_size + board.grid_start_x + 5
            and robot_x + robot.size > x * board.cell_size + board.grid_start_x
            and robot_y < y * board.cell_size + board.grid_start_y + 5
            and robot_y + robot.size > y * board.cell_size + board.grid_start_y
            and not contact_penalty
        ):
            score += 50
            contact_penalty = True

    # Update the display
    pygame.display.flip()

    # Control the frame rate
    clock.tick(60)
