import pygame
import math
import random
import numpy as np


class Camera:
    """Advanced camera system using matrix transformations and linear interpolation"""

    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height


        self.position = np.array([0.0, 0.0])
        self.target_position = np.array([0.0, 0.0])


        self.zoom = 1.0
        self.target_zoom = 1.0
        self.shake_intensity = 0.0
        self.shake_timer = 0


        self.position_lerp_speed = 0.08
        self.zoom_lerp_speed = 0.05


        self.min_x = 0
        self.max_x = 2000


        self.view_matrix = MatrixMath.create_view_matrix(0, 0, 1)
        self.previous_matrix = self.view_matrix.copy()

    def set_target(self, target_x, target_y):
        """Set the camera target position"""

        self.target_position[0] = target_x - self.screen_width / 2
        self.target_position[1] = target_y - self.screen_height / 2


        self.target_position[0] = max(self.min_x, min(self.target_position[0], self.max_x))
        self.target_position[1] = max(-100, min(self.target_position[1], 100))

    def set_zoom_target(self, zoom):
        """Set target zoom level"""
        self.target_zoom = max(0.5, min(zoom, 2.0))

    def add_screen_shake(self, intensity, duration):
        """Add screen shake effect"""
        self.shake_intensity = intensity
        self.shake_timer = duration

    def update(self):
        """Update camera using linear interpolation and matrix transformations"""

        self.previous_matrix = self.view_matrix.copy()


        self.position[0] = MatrixMath.lerp(self.position[0], self.target_position[0], self.position_lerp_speed)
        self.position[1] = MatrixMath.lerp(self.position[1], self.target_position[1], self.position_lerp_speed)


        self.zoom = MatrixMath.lerp(self.zoom, self.target_zoom, self.zoom_lerp_speed)


        shake_offset_x = 0
        shake_offset_y = 0
        if self.shake_timer > 0:
            shake_offset_x = random.uniform(-self.shake_intensity, self.shake_intensity)
            shake_offset_y = random.uniform(-self.shake_intensity, self.shake_intensity)
            self.shake_timer -= 1
            if self.shake_timer <= 0:
                self.shake_intensity = 0


        final_x = self.position[0] + shake_offset_x
        final_y = self.position[1] + shake_offset_y

        self.view_matrix = MatrixMath.create_view_matrix(final_x, final_y, self.zoom)

    def world_to_screen(self, world_pos):
        """Transform world coordinates to screen coordinates using view matrix"""
        return MatrixMath.apply_transformation(self.view_matrix, world_pos)

    def screen_to_world(self, screen_pos):
        """Transform screen coordinates to world coordinates"""

        inv_translation = MatrixMath.create_translation_matrix(self.position[0], self.position[1])
        inv_scaling = MatrixMath.create_scale_matrix(1 / self.zoom, 1 / self.zoom)
        inverse_view = MatrixMath.combine_matrices(inv_translation, inv_scaling)
        return MatrixMath.apply_transformation(inverse_view, screen_pos)

    def get_interpolated_matrix(self, alpha):
        """Get interpolated matrix for smooth rendering between frames"""
        return MatrixMath.lerp_matrix(self.previous_matrix, self.view_matrix, alpha)




class MatrixMath:
    """Custom matrix mathematics class for transformations"""

    @staticmethod
    def create_translation_matrix(dx, dy):
        """Create a 2D translation matrix"""
        return np.array([
            [1, 0, dx],
            [0, 1, dy],
            [0, 0, 1]
        ], dtype=float)

    @staticmethod
    def create_scale_matrix(sx, sy):
        """Create a 2D scaling matrix"""
        return np.array([
            [sx, 0, 0],
            [0, sy, 0],
            [0, 0, 1]
        ], dtype=float)

    @staticmethod
    def create_rotation_matrix(angle):
        """Create a 2D rotation matrix (angle in radians)"""
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        return np.array([
            [cos_a, -sin_a, 0],
            [sin_a, cos_a, 0],
            [0, 0, 1]
        ], dtype=float)

    @staticmethod
    def apply_transformation(matrix, point):
        """Apply transformation matrix to a point"""
        homogeneous_point = np.array([point[0], point[1], 1])
        transformed = np.dot(matrix, homogeneous_point)
        return [transformed[0], transformed[1]]

    @staticmethod
    def combine_matrices(*matrices):
        """Combine multiple transformation matrices"""
        result = matrices[0]
        for matrix in matrices[1:]:
            result = np.dot(result, matrix)
        return result

    @staticmethod
    def lerp(start, end, t):
        """Linear interpolation between two values"""
        return start + t * (end - start)

    @staticmethod
    def lerp_matrix(matrix_a, matrix_b, t):
        """Linear interpolation between two matrices"""
        return matrix_a + t * (matrix_b - matrix_a)

    @staticmethod
    def create_view_matrix(camera_x, camera_y, zoom=1.0):
        """Create a view matrix for camera transformation"""

        translation = MatrixMath.create_translation_matrix(-camera_x, -camera_y)
        scaling = MatrixMath.create_scale_matrix(zoom, zoom)
        return MatrixMath.combine_matrices(scaling, translation)


class PowerUp:
    def __init__(self, x, y, power_type):
        self.x = x
        self.y = y
        self.power_type = power_type
        self.width = 20
        self.height = 20
        self.collected = False
        self.color = (255, 0, 255) if power_type == 'grow' else (0, 255, 255)

    def draw(self, screen):
        if not self.collected:
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

            if self.power_type == 'grow':
                pygame.draw.line(screen, (255, 255, 255),
                                 (self.x + 10, self.y + 5), (self.x + 10, self.y + 15), 2)
                pygame.draw.line(screen, (255, 255, 255),
                                 (self.x + 5, self.y + 10), (self.x + 15, self.y + 10), 2)
            else:
                pygame.draw.line(screen, (255, 255, 255),
                                 (self.x + 5, self.y + 10), (self.x + 15, self.y + 10), 2)


class Coin:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 10
        self.collected = False
        self.rotation = 0

    def update(self):
        self.rotation += 0.1

    def draw(self, screen):
        if not self.collected:

            angle = self.rotation
            vertices = []
            for i in range(8):
                vertex_angle = (i * math.pi * 2 / 8) + angle
                x = self.x + math.cos(vertex_angle) * self.radius
                y = self.y + math.sin(vertex_angle) * self.radius
                vertices.append((x, y))

            pygame.draw.polygon(screen, (255, 255, 0), vertices)
            pygame.draw.circle(screen, (255, 215, 0), (int(self.x), int(self.y)), self.radius - 3)


class Platform:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)

    def update(self):
        pass

    def draw(self, screen):
        pygame.draw.rect(screen, (0, 255, 0), self.rect)
        pygame.draw.rect(screen, (0, 200, 0), self.rect, 2)


class MovingPlatform(Platform):
    def __init__(self, x, y, width, height, move_type='horizontal', speed=2, distance=100):
        super().__init__(x, y, width, height)
        self.original_pos = [x, y]
        self.move_type = move_type
        self.speed = speed
        self.distance = distance
        self.time = 0
        self.velocity = [0, 0]


        self.center_x = x + width // 2
        self.center_y = y + height // 2
        self.radius = distance // 2

    def update(self):
        """Update platform position using matrix transformations"""
        self.time += 0.02

        old_pos = [self.x, self.y]

        if self.move_type == 'horizontal':

            offset = math.sin(self.time * self.speed) * self.distance
            new_x = self.original_pos[0] + offset
            new_y = self.original_pos[1]

        elif self.move_type == 'vertical':

            offset = math.sin(self.time * self.speed) * self.distance
            new_x = self.original_pos[0]
            new_y = self.original_pos[1] + offset

        elif self.move_type == 'circular':

            angle = self.time * self.speed
            rotation_matrix = MatrixMath.create_rotation_matrix(angle)


            relative_point = [self.radius, 0]
            rotated_point = MatrixMath.apply_transformation(rotation_matrix, relative_point)

            new_x = self.center_x + rotated_point[0] - self.width // 2
            new_y = self.center_y + rotated_point[1] - self.height // 2


        self.velocity[0] = new_x - self.x
        self.velocity[1] = new_y - self.y


        translation_matrix = MatrixMath.create_translation_matrix(new_x - self.x, new_y - self.y)
        transformed_pos = MatrixMath.apply_transformation(translation_matrix, [self.x, self.y])

        self.x = transformed_pos[0]
        self.y = transformed_pos[1]
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

    def draw(self, screen):

        pygame.draw.rect(screen, (255, 165, 0), self.rect)
        pygame.draw.rect(screen, (255, 140, 0), self.rect, 3)


        center_x = self.rect.centerx
        center_y = self.rect.centery

        if self.move_type == 'horizontal':

            pygame.draw.polygon(screen, (255, 255, 255), [
                (center_x - 10, center_y - 3), (center_x - 15, center_y), (center_x - 10, center_y + 3)
            ])
            pygame.draw.polygon(screen, (255, 255, 255), [
                (center_x + 10, center_y - 3), (center_x + 15, center_y), (center_x + 10, center_y + 3)
            ])
        elif self.move_type == 'vertical':

            pygame.draw.polygon(screen, (255, 255, 255), [
                (center_x - 3, center_y - 10), (center_x, center_y - 15), (center_x + 3, center_y - 10)
            ])
            pygame.draw.polygon(screen, (255, 255, 255), [
                (center_x - 3, center_y + 10), (center_x, center_y + 15), (center_x + 3, center_y + 10)
            ])
        elif self.move_type == 'circular':

            pygame.draw.circle(screen, (255, 255, 255), (center_x, center_y), 8, 2)
            pygame.draw.polygon(screen, (255, 255, 255), [
                (center_x + 6, center_y - 6), (center_x + 10, center_y - 3), (center_x + 8, center_y - 8)
            ])


class Flag:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.pole_height = 100
        self.flag_width = 60
        self.flag_height = 40
        self.wave_time = 0
        self.collected = False

    def update(self):
        self.wave_time += 0.1

    def draw(self, screen):

        pole_bottom = (int(self.x), int(self.y))
        pole_top = (int(self.x), int(self.y - self.pole_height))
        pygame.draw.line(screen, (139, 69, 19), pole_bottom, pole_top, 4)


        flag_points = []
        segments = 10

        for i in range(segments + 1):

            wave_offset = math.sin(self.wave_time + i * 0.5) * 5


            point_x = self.x + (i / segments) * self.flag_width + wave_offset
            point_y = self.y - self.pole_height
            flag_points.append([point_x, point_y])

        for i in range(segments, -1, -1):

            wave_offset = math.sin(self.wave_time + i * 0.5) * 3
            point_x = self.x + (i / segments) * self.flag_width + wave_offset
            point_y = self.y - self.pole_height + self.flag_height
            flag_points.append([point_x, point_y])


        if self.collected:
            pygame.draw.polygon(screen, (0, 255, 0), flag_points)
        else:
            pygame.draw.polygon(screen, (255, 0, 0), flag_points)


        if not self.collected:

            for i in range(3):
                stripe_y = self.y - self.pole_height + (i + 1) * 8
                start_wave = math.sin(self.wave_time) * 5
                end_wave = math.sin(self.wave_time + 2) * 5
                pygame.draw.line(screen, (255, 255, 255),
                                 (self.x + start_wave, stripe_y),
                                 (self.x + self.flag_width + end_wave, stripe_y), 2)


        pygame.draw.circle(screen, (255, 215, 0), pole_top, 3)


class Ball:
    def __init__(self, x, y):
        self.original_pos = [x, y]
        self.pos = [x, y]
        self.velocity = [0, 0]
        self.base_radius = 15
        self.radius = self.base_radius
        self.color = (255, 0, 0)
        self.on_ground = False
        self.scale_factor = 1.0
        self.scale_timer = 0
        self.rotation = 0
        self.lives = 2  # Start with 2 lives

        self.gravity = 0.5
        self.jump_force = -12
        self.move_speed = 5
        self.friction = 0.8

    def apply_powerup(self, power_type):
        """Apply scaling powerup using matrix transformation"""
        if power_type == 'grow':
            self.scale_factor = 2.0
            # Regenerate a life when growing
            if self.lives < 2:
                self.lives += 1
        else:
            self.scale_factor = 0.5
            # Lose a life when shrinking
            self.lives -= 1
        self.scale_timer = 300

    def update(self):

        if self.scale_timer > 0:
            self.scale_timer -= 1
            if self.scale_timer == 0:
                self.scale_factor = 1.0


        scale_matrix = MatrixMath.create_scale_matrix(self.scale_factor, self.scale_factor)
        scaled_radius_point = MatrixMath.apply_transformation(scale_matrix, [self.base_radius, 0])
        self.radius = abs(scaled_radius_point[0])


        if not self.on_ground:
            self.velocity[1] += self.gravity


        self.velocity[0] *= self.friction


        if abs(self.velocity[0]) > 0.1:
            self.rotation += self.velocity[0] * 0.1


        translation_matrix = MatrixMath.create_translation_matrix(self.velocity[0], self.velocity[1])
        self.pos = MatrixMath.apply_transformation(translation_matrix, self.pos)


        self.on_ground = False

    def move_left(self):
        self.velocity[0] = -self.move_speed

    def move_right(self):
        self.velocity[0] = self.move_speed

    def jump(self):
        if self.on_ground:
            self.velocity[1] = self.jump_force

    def handle_platform_collision(self, platforms):
        ball_rect = pygame.Rect(self.pos[0] - self.radius, self.pos[1] - self.radius,
                                self.radius * 2, self.radius * 2)

        # Store previous position for collision resolution
        prev_pos = self.pos.copy()

        for platform in platforms:
            if ball_rect.colliderect(platform.rect):
                # Calculate platform velocity for moving platforms
                platform_velocity = [0, 0]
                if isinstance(platform, MovingPlatform):
                    platform_velocity = platform.velocity

                # Calculate overlap in each direction
                overlap_left = (self.pos[0] + self.radius) - platform.rect.left
                overlap_right = platform.rect.right - (self.pos[0] - self.radius)
                overlap_top = (self.pos[1] + self.radius) - platform.rect.top
                overlap_bottom = platform.rect.bottom - (self.pos[1] - self.radius)

                # Find minimum overlap
                min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)

                # Handle collision based on minimum overlap
                if min_overlap == overlap_top and self.velocity[1] >= 0:
                    # Landing on top of platform
                    self.pos[1] = platform.rect.top - self.radius
                    self.velocity[1] = 0
                    self.on_ground = True

                    # Apply platform velocity
                    if isinstance(platform, MovingPlatform):
                        # Add platform velocity with reduced influence
                        self.velocity[0] += platform_velocity[0] * 0.8
                        self.velocity[1] += platform_velocity[1] * 0.8

                        # Ensure we stay on top of vertical moving platforms
                        if platform.move_type == 'vertical':
                            self.pos[1] = platform.rect.top - self.radius
                            self.velocity[1] = platform_velocity[1]

                elif min_overlap == overlap_bottom and self.velocity[1] <= 0:
                    # Hitting bottom of platform
                    self.pos[1] = platform.rect.bottom + self.radius
                    self.velocity[1] = 0

                    # Apply platform velocity
                    if isinstance(platform, MovingPlatform):
                        self.velocity[1] += platform_velocity[1] * 0.5

                elif min_overlap == overlap_left and self.velocity[0] >= 0:
                    # Hitting left side of platform
                    self.pos[0] = platform.rect.left - self.radius
                    self.velocity[0] = 0

                    # Apply platform velocity
                    if isinstance(platform, MovingPlatform):
                        self.velocity[0] += platform_velocity[0] * 0.3

                elif min_overlap == overlap_right and self.velocity[0] <= 0:
                    # Hitting right side of platform
                    self.pos[0] = platform.rect.right + self.radius
                    self.velocity[0] = 0

                    # Apply platform velocity
                    if isinstance(platform, MovingPlatform):
                        self.velocity[0] += platform_velocity[0] * 0.3

                # Update ball rect after position change
                ball_rect.x = self.pos[0] - self.radius
                ball_rect.y = self.pos[1] - self.radius

                # Additional check for fast-moving platforms
                if isinstance(platform, MovingPlatform) and (abs(platform_velocity[0]) > 5 or abs(platform_velocity[1]) > 5):
                    # Predict next position
                    next_pos = [self.pos[0] + self.velocity[0], self.pos[1] + self.velocity[1]]
                    next_rect = pygame.Rect(next_pos[0] - self.radius, next_pos[1] - self.radius,
                                          self.radius * 2, self.radius * 2)
                    
                    # If next position would also collide, adjust velocity
                    if next_rect.colliderect(platform.rect):
                        if platform.move_type == 'vertical':
                            self.velocity[1] = platform_velocity[1]
                        elif platform.move_type == 'horizontal':
                            self.velocity[0] = platform_velocity[0] * 0.8

    def draw(self, screen):

        center = (int(self.pos[0]), int(self.pos[1]))


        pygame.draw.circle(screen, self.color, center, int(self.radius))


        rotation_matrix = MatrixMath.create_rotation_matrix(self.rotation)
        edge_point = [self.radius * 0.7, 0]
        rotated_edge = MatrixMath.apply_transformation(rotation_matrix, edge_point)

        end_pos = (int(self.pos[0] + rotated_edge[0]), int(self.pos[1] + rotated_edge[1]))
        pygame.draw.line(screen, (150, 0, 0), center, end_pos, 3)


        if self.scale_timer > 0:
            color = (255, 0, 255) if self.scale_factor > 1 else (0, 255, 255)
            pygame.draw.circle(screen, color, center, int(self.radius + 5), 2)


class Game:
    def __init__(self):
        pygame.init()
        self.width = 1000
        self.height = 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Red Ball Game")
        self.clock = pygame.time.Clock()

        # Load flag image
        self.flag_image = pygame.Surface((60, 40))
        self.flag_image.fill((255, 0, 0))
        pygame.draw.rect(self.flag_image, (255, 255, 255), (0, 0, 60, 13))
        pygame.draw.rect(self.flag_image, (255, 255, 255), (0, 13, 60, 13))
        pygame.draw.rect(self.flag_image, (255, 255, 255), (0, 26, 60, 13))

        self.current_level = 1
        self.max_level = 3
        self.reset_level()

    def reset_level(self):
        """Reset the current level"""
        self.ball = Ball(100, 400)
        self.platforms = self.create_platforms()
        self.moving_platforms = self.create_moving_platforms()
        self.all_platforms = self.platforms + self.moving_platforms
        self.coins = self.create_coins()
        self.powerups = self.create_powerups()
        self.flag = Flag(1850, 450)
        self.camera = Camera(self.width, self.height)
        self.score = 0
        self.level_complete = False
        self.font = pygame.font.Font(None, 36)
        self.frame_alpha = 0.0

    def create_platforms(self):
        """Create platforms based on current level"""
        if self.current_level == 1:
            platforms = [
                Platform(0, 550, 200, 50),
                Platform(250, 450, 150, 20),
                Platform(450, 350, 100, 20),
                Platform(600, 250, 120, 20),
                Platform(1150, 200, 150, 20),
                Platform(1350, 350, 100, 20),
                Platform(1750, 500, 150, 50),
            ]
        elif self.current_level == 2:
            platforms = [
                Platform(0, 550, 200, 50),
                Platform(300, 450, 150, 20),
                # First narrow gap section
                Platform(500, 350, 60, 20),  # Left platform
                Platform(580, 350, 60, 20),  # Right platform (20px gap)
                Platform(700, 250, 120, 20),
                # Second narrow gap section
                Platform(900, 350, 50, 20),  # Left platform
                Platform(580, 350, 50, 20),  # Right platform (30px gap)
                Platform(1100, 450, 150, 20),
                # Third narrow gap section
                Platform(1300, 350, 40, 20),  # Left platform
                Platform(1360, 350, 40, 20),  # Right platform (20px gap)
                Platform(1500, 250, 120, 20),
                Platform(1700, 350, 100, 20),
                Platform(1850, 500, 150, 50),
            ]
        else:  # Level 3
            platforms = [
                Platform(0, 550, 200, 50),
                Platform(250, 450, 150, 20),
                Platform(450, 350, 100, 20),
                Platform(650, 250, 120, 20),
                Platform(850, 150, 100, 20),
                Platform(1050, 250, 120, 20),
                Platform(1250, 350, 100, 20),
                Platform(1450, 450, 150, 20),
                Platform(1650, 350, 100, 20),
                Platform(1850, 500, 150, 50),
            ]
        return platforms

    def create_moving_platforms(self):
        """Create moving platforms based on current level"""
        if self.current_level == 1:
            moving_platforms = [
                MovingPlatform(800, 400, 100, 20, 'horizontal', 1.5, 80),
                MovingPlatform(950, 300, 80, 20, 'vertical', 1.0, 60),
                MovingPlatform(1500, 300, 90, 20, 'circular', 0.8, 100),
                MovingPlatform(1600, 450, 100, 20, 'horizontal', 2.0, 120),
            ]
        elif self.current_level == 2:
            moving_platforms = [
                MovingPlatform(400, 400, 100, 20, 'vertical', 1.0, 80),
                MovingPlatform(600, 300, 80, 20, 'horizontal', 1.0, 60),
                MovingPlatform(800, 200, 90, 20, 'circular', 0.8, 100),
                MovingPlatform(1200, 400, 100, 20, 'vertical', 1.0, 120),
                MovingPlatform(1400, 300, 80, 20, 'horizontal', 1.0, 80),
            ]
        else:  # Level 3
            moving_platforms = [
                MovingPlatform(350, 400, 100, 20, 'circular', 1.5, 80),
                MovingPlatform(550, 300, 80, 20, 'vertical', 1.0, 60),
                MovingPlatform(750, 200, 90, 20, 'horizontal', 0.8, 100),
                MovingPlatform(1150, 300, 100, 20, 'circular', 2.0, 120),
                MovingPlatform(1350, 400, 80, 20, 'vertical', 1.5, 80),
                MovingPlatform(1550, 300, 90, 20, 'horizontal', 1.0, 60),
            ]
        return moving_platforms

    def create_coins(self):
        """Create coins based on current level"""
        if self.current_level == 1:
            coins = [
                Coin(320, 410),
                Coin(500, 310),
                Coin(660, 210),
                Coin(850, 360),
                Coin(950, 260),
                Coin(1220, 160),
                Coin(1400, 310),
                Coin(1550, 260),
                Coin(1820, 460),
            ]
        elif self.current_level == 2:
            coins = [
                Coin(350, 410),
                Coin(550, 310),
                Coin(750, 210),
                Coin(950, 310),
                Coin(1150, 410),
                Coin(1350, 310),
                Coin(1550, 210),
                Coin(1750, 310),
                Coin(1900, 460),
            ]
        else:  # Level 3
            coins = [
                Coin(300, 410),
                Coin(500, 310),
                Coin(700, 210),
                Coin(900, 110),
                Coin(1100, 210),
                Coin(1300, 310),
                Coin(1500, 410),
                Coin(1700, 310),
                Coin(1900, 460),
            ]
        return coins

    def create_powerups(self):
        """Create powerups based on current level"""
        if self.current_level == 1:
            powerups = [
                PowerUp(300, 430, 'shrink'),
                PowerUp(650, 230, 'grow'),
                PowerUp(900, 380, 'shrink'),
                PowerUp(1200, 180, 'grow'),
                PowerUp(1450, 330, 'shrink'),
            ]
        elif self.current_level == 2:
            powerups = [
                # Power-ups before each narrow gap
                PowerUp(450, 330, 'shrink'),  # Before first gap
                PowerUp(850, 330, 'shrink'),  # Before second gap
                PowerUp(1250, 330, 'shrink'),  # Before third gap
                # Additional power-ups for recovery
                PowerUp(1000, 430, 'grow'),
                PowerUp(1600, 430, 'grow'),
            ]
        else:  # Level 3
            powerups = [
                PowerUp(300, 430, 'grow'),
                PowerUp(600, 330, 'shrink'),
                PowerUp(900, 130, 'grow'),
                PowerUp(1200, 230, 'shrink'),
                PowerUp(1500, 430, 'grow'),
                PowerUp(1800, 330, 'shrink'),
            ]
        return powerups

    def update_camera(self):
        """Update camera using matrix-based linear interpolation"""

        self.camera.set_target(self.ball.pos[0], self.ball.pos[1])


        if self.ball.scale_factor > 1.0:
            self.camera.set_zoom_target(0.8)
        elif self.ball.scale_factor < 1.0:
            self.camera.set_zoom_target(1.3)
        else:
            self.camera.set_zoom_target(1.0)


        if self.ball.on_ground and abs(self.ball.velocity[1]) > 8:
            self.camera.add_screen_shake(3, 10)


        self.camera.update()

    def check_collisions(self):
        ball_rect = pygame.Rect(self.ball.pos[0] - self.ball.radius,
                                self.ball.pos[1] - self.ball.radius,
                                self.ball.radius * 2, self.ball.radius * 2)

        for coin in self.coins:
            if not coin.collected:
                coin_rect = pygame.Rect(coin.x - coin.radius, coin.y - coin.radius,
                                        coin.radius * 2, coin.radius * 2)
                if ball_rect.colliderect(coin_rect):
                    coin.collected = True
                    self.score += 10
                    self.camera.add_screen_shake(1, 5)

        for powerup in self.powerups:
            if not powerup.collected:
                powerup_rect = pygame.Rect(powerup.x, powerup.y, powerup.width, powerup.height)
                if ball_rect.colliderect(powerup_rect):
                    powerup.collected = True
                    self.ball.apply_powerup(powerup.power_type)
                    self.camera.add_screen_shake(2, 8)

        if not self.flag.collected:
            flag_rect = pygame.Rect(self.flag.x - 10, self.flag.y - self.flag.pole_height,
                                    self.flag.flag_width + 20, self.flag.pole_height + 20)
            if ball_rect.colliderect(flag_rect):
                self.flag.collected = True
                self.level_complete = True
                self.score += 100
                self.camera.add_screen_shake(5, 30)
                
                # Move to next level if available
                if self.current_level < self.max_level:
                    self.current_level += 1
                    self.reset_level()
                    self.level_complete = False
                    # Add a strong screen shake for level transition
                    self.camera.add_screen_shake(8, 45)  # Stronger and longer shake for level transition

    def draw_world_object(self, world_pos, draw_func, *args):
        """Helper function to draw world objects using camera transformation"""
        screen_pos = self.camera.world_to_screen(world_pos)
        return screen_pos

    def draw_ui(self):
        score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (10, 10))

        level_text = self.font.render(f"Level: {self.current_level}/{self.max_level}", True, (255, 255, 255))
        self.screen.blit(level_text, (10, 50))

        # Draw lives
        lives_text = self.font.render(f"Lives: {self.ball.lives}", True, (255, 255, 255))
        self.screen.blit(lives_text, (10, 90))

        coins_collected = sum(1 for coin in self.coins if coin.collected)
        coin_text = self.font.render(f"Coins: {coins_collected}/{len(self.coins)}", True, (255, 255, 255))
        self.screen.blit(coin_text, (10, 130))

        if self.ball.scale_timer > 0:
            power_type = "LARGE" if self.ball.scale_factor > 1 else "SMALL"
            power_text = self.font.render(f"Power: {power_type} ({self.ball.scale_timer // 60 + 1}s)",
                                          True, (255, 255, 0))
            self.screen.blit(power_text, (10, 170))

        cam_info = self.font.render(f"Zoom: {self.camera.zoom:.2f}x", True, (150, 150, 255))
        self.screen.blit(cam_info, (10, 210))

        if not self.level_complete:
            inst_text = pygame.font.Font(None, 24).render(
                "ARROWS/AD: move, SPACE: jump. Reach the flag to win!",
                True, (200, 200, 200))
            self.screen.blit(inst_text, (10, self.height - 50))

            zoom_text = pygame.font.Font(None, 20).render(
                "Orange platforms move! Camera uses matrix interpolation!",
                True, (180, 180, 180))
            self.screen.blit(zoom_text, (10, self.height - 25))

        if self.level_complete and self.current_level == self.max_level:
            complete_text = self.font.render("GAME COMPLETE! Press R to restart", True, (0, 255, 0))
            text_rect = complete_text.get_rect(center=(self.width // 2, self.height // 2))
            self.screen.blit(complete_text, text_rect)

    def run(self):
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r and self.level_complete and self.current_level == self.max_level:
                        self.current_level = 1
                        self.reset_level()
                    # Reset level if all lives are lost
                    elif self.ball.lives <= 0:
                        self.score = 0  # Reset score
                        self.reset_level()
                        self.camera.add_screen_shake(10, 60)  # Strong shake for life loss

            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.ball.move_left()
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.ball.move_right()
            if keys[pygame.K_SPACE] or keys[pygame.K_UP]:
                self.ball.jump()

            if not self.level_complete:
                self.ball.update()
                self.ball.handle_platform_collision(self.all_platforms)

                for platform in self.moving_platforms:
                    platform.update()

                for coin in self.coins:
                    coin.update()

                self.flag.update()
                self.check_collisions()
                self.update_camera()

                if self.ball.pos[1] > self.height + 100:
                    self.ball.pos = list(self.ball.original_pos)
                    self.ball.velocity = [0, 0]
                    self.ball.lives -= 1  # Lose a life when falling off
                    if self.ball.lives <= 0:
                        self.score = 0  # Reset score
                        self.reset_level()
                        self.camera.add_screen_shake(10, 60)  # Strong shake for life loss

            self.screen.fill((50, 50, 100))

            # Draw platforms
            for platform in self.platforms:
                corners = [
                    [platform.rect.x, platform.rect.y],
                    [platform.rect.x + platform.rect.width, platform.rect.y],
                    [platform.rect.x + platform.rect.width, platform.rect.y + platform.rect.height],
                    [platform.rect.x, platform.rect.y + platform.rect.height]
                ]

                screen_corners = []
                for corner in corners:
                    screen_pos = self.camera.world_to_screen(corner)
                    screen_corners.append(screen_pos)

                if any(-100 < pos[0] < self.width + 100 and -100 < pos[1] < self.height + 100
                       for pos in screen_corners):
                    pygame.draw.polygon(self.screen, (0, 255, 0), screen_corners)
                    pygame.draw.polygon(self.screen, (0, 200, 0), screen_corners, 2)

            # Draw moving platforms
            for platform in self.moving_platforms:
                corners = [
                    [platform.rect.x, platform.rect.y],
                    [platform.rect.x + platform.rect.width, platform.rect.y],
                    [platform.rect.x + platform.rect.width, platform.rect.y + platform.rect.height],
                    [platform.rect.x, platform.rect.y + platform.rect.height]
                ]

                screen_corners = []
                for corner in corners:
                    screen_pos = self.camera.world_to_screen(corner)
                    screen_corners.append(screen_pos)

                if any(-100 < pos[0] < self.width + 100 and -100 < pos[1] < self.height + 100
                       for pos in screen_corners):
                    pygame.draw.polygon(self.screen, (255, 165, 0), screen_corners)
                    pygame.draw.polygon(self.screen, (255, 140, 0), screen_corners, 3)

                    center_world = [platform.rect.centerx, platform.rect.centery]
                    center_screen = self.camera.world_to_screen(center_world)
                    center_x, center_y = int(center_screen[0]), int(center_screen[1])

                    if platform.move_type == 'horizontal':
                        arrow_size = 8 * self.camera.zoom
                        pygame.draw.polygon(self.screen, (255, 255, 255), [
                            (center_x - arrow_size, center_y - arrow_size // 2),
                            (center_x - arrow_size * 1.5, center_y),
                            (center_x - arrow_size, center_y + arrow_size // 2)
                        ])
                        pygame.draw.polygon(self.screen, (255, 255, 255), [
                            (center_x + arrow_size, center_y - arrow_size // 2),
                            (center_x + arrow_size * 1.5, center_y),
                            (center_x + arrow_size, center_y + arrow_size // 2)
                        ])
                    elif platform.move_type == 'vertical':
                        arrow_size = 8 * self.camera.zoom
                        pygame.draw.polygon(self.screen, (255, 255, 255), [
                            (center_x - arrow_size // 2, center_y - arrow_size),
                            (center_x, center_y - arrow_size * 1.5),
                            (center_x + arrow_size // 2, center_y - arrow_size)
                        ])
                        pygame.draw.polygon(self.screen, (255, 255, 255), [
                            (center_x - arrow_size // 2, center_y + arrow_size),
                            (center_x, center_y + arrow_size * 1.5),
                            (center_x + arrow_size // 2, center_y + arrow_size)
                        ])
                    elif platform.move_type == 'circular':
                        radius = 8 * self.camera.zoom
                        pygame.draw.circle(self.screen, (255, 255, 255), (center_x, center_y), int(radius), 2)
                        pygame.draw.polygon(self.screen, (255, 255, 255), [
                            (center_x + radius * 0.7, center_y - radius * 0.7),
                            (center_x + radius * 1.2, center_y - radius * 0.3),
                            (center_x + radius * 0.9, center_y - radius * 0.9)
                        ])

            # Draw coins
            for coin in self.coins:
                if not coin.collected:
                    screen_pos = self.camera.world_to_screen([coin.x, coin.y])
                    if -50 < screen_pos[0] < self.width + 50 and -50 < screen_pos[1] < self.height + 50:
                        vertices = []
                        for i in range(8):
                            vertex_angle = (i * math.pi * 2 / 8) + coin.rotation
                            world_x = coin.x + math.cos(vertex_angle) * coin.radius
                            world_y = coin.y + math.sin(vertex_angle) * coin.radius
                            vertex_screen = self.camera.world_to_screen([world_x, world_y])
                            vertices.append(vertex_screen)

                        pygame.draw.polygon(self.screen, (255, 255, 0), vertices)
                        inner_radius = coin.radius * self.camera.zoom * 0.7
                        pygame.draw.circle(self.screen, (255, 215, 0),
                                           (int(screen_pos[0]), int(screen_pos[1])), int(max(1, inner_radius)))

            # Draw powerups
            for powerup in self.powerups:
                if not powerup.collected:
                    screen_pos = self.camera.world_to_screen([powerup.x, powerup.y])
                    if -50 < screen_pos[0] < self.width + 50 and -50 < screen_pos[1] < self.height + 50:
                        scaled_width = powerup.width * self.camera.zoom
                        scaled_height = powerup.height * self.camera.zoom

                        powerup_rect = pygame.Rect(screen_pos[0], screen_pos[1],
                                                   scaled_width, scaled_height)
                        pygame.draw.rect(self.screen, powerup.color, powerup_rect)

                        if powerup.power_type == 'grow':
                            line_len = scaled_width * 0.3
                            center_x, center_y = screen_pos[0] + scaled_width / 2, screen_pos[1] + scaled_height / 2
                            pygame.draw.line(self.screen, (255, 255, 255),
                                             (center_x, center_y - line_len), (center_x, center_y + line_len), 2)
                            pygame.draw.line(self.screen, (255, 255, 255),
                                             (center_x - line_len, center_y), (center_x + line_len, center_y), 2)
                        else:
                            line_len = scaled_width * 0.3
                            center_x, center_y = screen_pos[0] + scaled_width / 2, screen_pos[1] + scaled_height / 2
                            pygame.draw.line(self.screen, (255, 255, 255),
                                             (center_x - line_len, center_y), (center_x + line_len, center_y), 2)

            # Draw flag
            if not self.flag.collected:
                screen_pos = self.camera.world_to_screen([self.flag.x, self.flag.y])
                if -100 < screen_pos[0] < self.width + 100 and -100 < screen_pos[1] < self.height + 100:
                    # Draw pole
                    pole_bottom = (int(screen_pos[0]), int(screen_pos[1]))
                    pole_top = (int(screen_pos[0]), int(screen_pos[1] - self.flag.pole_height * self.camera.zoom))
                    pygame.draw.line(self.screen, (139, 69, 19), pole_bottom, pole_top, int(4 * self.camera.zoom))

                    # Draw flag image
                    scaled_flag = pygame.transform.scale(self.flag_image, 
                        (int(self.flag.flag_width * self.camera.zoom), 
                         int(self.flag.flag_height * self.camera.zoom)))
                    self.screen.blit(scaled_flag, 
                        (int(screen_pos[0]), int(screen_pos[1] - self.flag.pole_height * self.camera.zoom)))

            # Draw ball
            ball_screen_pos = self.camera.world_to_screen(self.ball.pos)
            scaled_radius = self.ball.radius * self.camera.zoom

            if scaled_radius > 1:
                center = (int(ball_screen_pos[0]), int(ball_screen_pos[1]))
                pygame.draw.circle(self.screen, self.ball.color, center, int(scaled_radius))

                rotation_matrix = MatrixMath.create_rotation_matrix(self.ball.rotation)
                edge_point = [self.ball.radius * 0.7, 0]
                rotated_edge = MatrixMath.apply_transformation(rotation_matrix, edge_point)

                world_edge_pos = [self.ball.pos[0] + rotated_edge[0], self.ball.pos[1] + rotated_edge[1]]
                screen_edge_pos = self.camera.world_to_screen(world_edge_pos)

                pygame.draw.line(self.screen, (150, 0, 0), center,
                                 (int(screen_edge_pos[0]), int(screen_edge_pos[1])), 3)

                if self.ball.scale_timer > 0:
                    color = (255, 0, 255) if self.ball.scale_factor > 1 else (0, 255, 255)
                    pygame.draw.circle(self.screen, color, center, int(scaled_radius + 5 * self.camera.zoom), 2)

            self.draw_ui()
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()
