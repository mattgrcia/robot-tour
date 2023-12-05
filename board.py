import pygame
import random


class Board:
    def __init__(self, window, blockades, grid_size=4, cell_size=100) -> None:
        # Set up grid dimensions and spacing
        self.window = window
        self.blockades = blockades
        self.grid_size = grid_size
        self.cell_size = cell_size
        self.grid_start_x = (
            self.window.get_width() - self.grid_size * self.cell_size
        ) // 2
        self.grid_start_y = (
            self.window.get_height() - self.grid_size * self.cell_size
        ) // 2

        self.set_starting_zone()
        self.set_target_zone()
        self.set_target_point()
        self.set_bonus_zones()
        self.draw_grid()

    def get_grid_start(self):
        return self.grid_start_x, self.grid_start_y

    def get_cell_size(self):
        return self.cell_size

    def get_grid_size(self):
        return self.grid_size

    def get_target_point(self):
        return self.target_point

    def get_blockades(self):
        return self.blockades

    def set_starting_zone(self):
        self.starting_zone = random.choice([1, 2, 3, 4, 5, 8, 9, 12, 13, 14, 15, 16])

    def get_starting_zone(self):
        return self.starting_zone

    def get_starting_edge(self):
        starting_zone = self.starting_zone
        starting_side = None
        if starting_zone in [1, 4, 13, 16]:
            starting_side = random.choice(["top", "side"])

        return starting_zone, starting_side

    def get_starting_point(self):
        starting_zone, starting_side = self.get_starting_edge()

        if starting_zone in [5, 9] or (
            starting_zone in [1, 13] and starting_side == "side"
        ):
            starting_point = (
                self.grid_start_x,
                self.grid_start_y
                + (
                    self.cell_size * ((starting_zone - 1) % self.grid_size)
                    + self.cell_size / 2
                ),
            )

        elif starting_zone in [8, 12] or (
            starting_zone in [4, 16] and starting_side == "side"
        ):
            starting_point = (
                self.grid_start_x + self.grid_size * self.cell_size,
                self.grid_start_y
                + (
                    self.cell_size * ((starting_zone - 1) % self.grid_size)
                    + self.cell_size / 2
                ),
            )

        elif starting_zone in [2, 3] or (
            starting_zone in [1, 4] and starting_side == "top"
        ):
            starting_point = (
                self.grid_start_x
                + (
                    self.cell_size * ((starting_zone - 1) % self.grid_size)
                    + self.cell_size / 2
                ),
                self.grid_start_y,
            )

        elif starting_zone in [14, 15] or (
            starting_zone in [13, 16] and starting_side == "top"
        ):
            starting_point = (
                self.grid_start_x
                + (
                    self.cell_size * ((starting_zone - 1) % self.grid_size)
                    + self.cell_size / 2
                ),
                self.grid_start_y + self.grid_size * self.cell_size,
            )

        return starting_point

    def set_target_zone(self):
        self.target_zone = self.starting_zone
        while self.target_zone == self.starting_zone:
            self.target_zone = random.randint(1, 16)

    def set_target_point(self):
        target_point = (
            self.grid_start_x
            + self.cell_size * ((self.target_zone - 1) // self.grid_size)
            + self.cell_size / 2,
            self.grid_start_y
            + self.cell_size * ((self.target_zone - 1) // self.grid_size)
            + self.cell_size / 2,
        )

        self.target_point = target_point

    def set_bonus_zones(self, bonus_zones=None):
        if bonus_zones is not None:
            self.bonus_zones = bonus_zones
        else:
            self.bonus_zones = random.sample(range(1, 17), 8)

    def get_bonus_zones(self):
        return self.bonus_zones

    def draw_grid(self, font_size=18, color=(0, 0, 0)):
        zones = self.get_bonus_zones()
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                x = col * self.cell_size + self.grid_start_x
                y = row * self.cell_size + self.grid_start_y
                pygame.draw.rect(
                    self.window,
                    (0, 0, 255),
                    (x, y, self.cell_size, self.cell_size),
                    1,
                )
                zone_number = row * self.grid_size + col + 1
                # font = pygame.font.SysFont("Arial", font_size)
                # label = font.render(str(zone_number), True, color)
                # label_rect = label.get_rect(
                #    center=(x + self.cell_size // 2, y + self.cell_size // 2)
                # )
                # self.window.blit(label, label_rect)

                # Fill the highlighted zones with green
                if zone_number in zones:
                    pygame.draw.rect(
                        self.window,
                        (53, 94, 59),
                        (x + 1, y + 1, self.cell_size - 1, self.cell_size - 1),
                    )

        return None

    # Function to draw blockades
    def draw_blockades(self, blockade_locations):
        for location in blockade_locations:
            x = (location[0] - 1) % self.grid_size
            y = (location[0] - 1) // self.grid_size

            if location[1] == "A":
                start_point = (
                    x * self.cell_size + self.grid_start_x,
                    y * self.cell_size + self.grid_start_y,
                )
                end_point = (
                    (x + 1) * self.cell_size + self.grid_start_x,
                    y * self.cell_size + self.grid_start_y,
                )
            elif location[1] == "B":
                start_point = (
                    (x + 1) * self.cell_size + self.grid_start_x,
                    y * self.cell_size + self.grid_start_y,
                )
                end_point = (
                    (x + 1) * self.cell_size + self.grid_start_x,
                    (y + 1) * self.cell_size + self.grid_start_y,
                )
            elif location[1] == "C":
                start_point = (
                    (x + 1) * self.cell_size + self.grid_start_x,
                    (y + 1) * self.cell_size + self.grid_start_y,
                )
                end_point = (
                    x * self.cell_size + self.grid_start_x,
                    (y + 1) * self.cell_size + self.grid_start_y,
                )
            elif location[1] == "D":
                start_point = (
                    x * self.cell_size + self.grid_start_x,
                    (y + 1) * self.cell_size + self.grid_start_y,
                )
                end_point = (
                    x * self.cell_size + self.grid_start_x,
                    y * self.cell_size + self.grid_start_y,
                )

            pygame.draw.line(self.window, (202, 164, 114), start_point, end_point, 5)

        return None

    def draw(self, blockade_locations):
        self.draw_grid()
        self.draw_blockades(blockade_locations)
