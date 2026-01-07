import pygame
from circleshape import CircleShape
from constants import SHOT_RADIUS, SCREEN_WIDTH, SCREEN_HEIGHT, DESPAWN_MARGIN, SHOT_LIFETIME

class Shot(CircleShape):
    def __init__(self, x, y):
        super().__init__(x, y, SHOT_RADIUS)
        self.age = 0.0
        self.prev_position = pygame.Vector2(x, y)

    def draw(self, screen):
        # pygame.draw.circle(surface, color, center, radius, width)
        pygame.draw.circle(screen, "white", self.position, self.radius, 2)

    def update(self, dt):
        self.age += dt
        self.prev_position.update(self.position)
        self.position += self.velocity * dt

        # bullet culling:
        # off-screen cull
        if (self.position.x < -DESPAWN_MARGIN or
            self.position.x > SCREEN_WIDTH + DESPAWN_MARGIN or
            self.position.y < -DESPAWN_MARGIN or
            self.position.y > SCREEN_HEIGHT + DESPAWN_MARGIN):
            self.kill()
            return
        
        # time to live
        if self.age >= SHOT_LIFETIME:
            self.kill()