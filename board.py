from collections import defaultdict
import pygame
import random


class Board:
    def __init__(
        self,
        window: pygame.display.set_mode,
        surface: pygame.Surface,
        blockade_size=5,
        blockades={},
        grid_size=4,
        cell_size=100,
    ) -> None:
        # Set up grid dimensions and spacing
        self.window = window
        self.surface = surface

        self.grid_size = grid_size
        self.cell_size = cell_size
        self.blockade_size = blockade_size
        self.grid_start_x = (
            self.surface.get_width() - self.grid_size * self.cell_size
        ) // 2
        self.grid_start_y = (
            self.surface.get_height() - self.grid_size * self.cell_size
        ) // 2

        self.set_starting_zone()
        self.set_starting_point()
        self.set_target_zone()
        self.set_target_point()
        self.set_bonus_zones()

        # Set blockades
        if len(blockades) > 0:
            self.blockades = blockades
        self.set_blockades()

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

    def hit_blockade(self, location):
        self.blockades[location] = True

    def get_blockade_size(self):
        return self.blockade_size

    def set_starting_zone(self):
        self.starting_zone = random.choice([1, 2, 3, 4, 5, 8, 9, 12, 13, 14, 15, 16])

    def get_starting_zone(self):
        return self.starting_zone

    def get_starting_point(self):
        return self.starting_point

    def get_starting_edge(self):
        starting_zone = self.starting_zone
        starting_side = None
        if starting_zone in [1, 4, 13, 16]:
            starting_side = random.choice(["top", "side"])

        return starting_zone, starting_side

    def set_starting_point(self) -> None:
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

        self.starting_point = starting_point

    def get_starting_angle(self):
        zone, side = self.get_starting_edge()

        if zone in [5, 9] or (zone in [1, 13] and side == "side"):
            angle = 0

        elif zone in [8, 12] or (zone in [4, 16] and side == "side"):
            angle = 180

        elif zone in [2, 3] or (zone in [1, 4] and side == "top"):
            angle = 90

        elif zone in [14, 15] or (zone in [13, 16] and side == "top"):
            angle = 270

        return angle

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

    def set_bonus_zones(self, bonus_zones: list = None) -> None:
        if bonus_zones is not None:
            self.bonus_zones = {k: False for k in bonus_zones}
        else:
            self.bonus_zones = {
                k: False for k in random.sample(range(1, 17), random.randint(1, 4))
            }

        return None

    def set_blockades(self) -> None:
        self.blockades = {}
        possible_blockades = [(k, "N") for k in range(5, 17)]
        possible_blockades += [(k, "E") for k in range(1, 17) if k % 4 != 0]
        possible_blockades += [(k, "S") for k in range(1, 13)]
        possible_blockades += [(k, "W") for k in range(1, 17) if k % 4 != 1]

        num_blockades = random.randint(1, 8)
        num_chosen = 0
        num_zone_blockades = defaultdict(int)

        while num_chosen < num_blockades:
            blockade = random.choice(possible_blockades)

            if blockade not in self.blockades.keys():
                if self.starting_zone == blockade[0]:
                    if num_zone_blockades[blockade[0]] < 2:
                        self.blockades[blockade] = False
                        num_zone_blockades[blockade[0]] += 1
                        num_chosen += 1
                else:
                    if num_zone_blockades[blockade[0]] < 3:
                        self.blockades[blockade] = False
                        num_zone_blockades[blockade[0]] += 1
                        num_chosen += 1

        return None

    def hit_bonus_zone(self, zone_number):
        self.bonus_zones[zone_number] = True

    def get_bonus_zones(self):
        return self.bonus_zones

    def draw_grid(self, font_size=18, color=(0, 0, 0)):
        bonus_zones = self.get_bonus_zones()
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                x = col * self.cell_size + self.grid_start_x
                y = row * self.cell_size + self.grid_start_y
                pygame.draw.rect(
                    self.surface,
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
                if zone_number in bonus_zones:
                    if bonus_zones[zone_number]:
                        pygame.draw.rect(
                            self.surface,
                            (50, 180, 65),
                            (x + 1, y + 1, self.cell_size - 1, self.cell_size - 1),
                        )
                    else:
                        pygame.draw.rect(
                            self.surface,
                            (53, 94, 59),
                            (x + 1, y + 1, self.cell_size - 1, self.cell_size - 1),
                        )

        return None

    # Function to draw blockades
    def draw_blockades(self):
        for location in self.blockades.keys():
            x = (location[0] - 1) % self.grid_size
            y = (location[0] - 1) // self.grid_size

            if location[1] == "N":
                start_point = (
                    x * self.cell_size + self.grid_start_x,
                    y * self.cell_size + self.grid_start_y,
                )
                end_point = (
                    (x + 1) * self.cell_size + self.grid_start_x,
                    y * self.cell_size + self.grid_start_y,
                )
            elif location[1] == "E":
                start_point = (
                    (x + 1) * self.cell_size + self.grid_start_x,
                    y * self.cell_size + self.grid_start_y,
                )
                end_point = (
                    (x + 1) * self.cell_size + self.grid_start_x,
                    (y + 1) * self.cell_size + self.grid_start_y,
                )
            elif location[1] == "S":
                start_point = (
                    (x + 1) * self.cell_size + self.grid_start_x,
                    (y + 1) * self.cell_size + self.grid_start_y,
                )
                end_point = (
                    x * self.cell_size + self.grid_start_x,
                    (y + 1) * self.cell_size + self.grid_start_y,
                )
            elif location[1] == "W":
                start_point = (
                    x * self.cell_size + self.grid_start_x,
                    (y + 1) * self.cell_size + self.grid_start_y,
                )
                end_point = (
                    x * self.cell_size + self.grid_start_x,
                    y * self.cell_size + self.grid_start_y,
                )

            if self.blockades[location]:
                pygame.draw.line(self.surface, (255, 0, 0), start_point, end_point, 5)
            else:
                pygame.draw.line(
                    self.surface, (202, 164, 114), start_point, end_point, 5
                )

        return None

    def draw(self) -> None:
        # Draw the grid and blockades directly onto the render_surface
        self.draw_grid()
        self.draw_blockades()

        return None
