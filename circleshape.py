import pygame
from constants import SCREEN_HEIGHT, SCREEN_WIDTH

# Base class for game objects
class CircleShape(pygame.sprite.Sprite):
    def __init__(self, x, y, radius):
        # subclasses auto-add to groups with use of containers
        if hasattr(self, "containers"):
            super().__init__(self.containers)
        else:
            super().__init__()

        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)
        self.radius = radius

    # helpers
    def integrate(self, dt: float) -> None:
        # euler integration
        self.position += self.velocity * dt

    def wrap_position(self) -> None:
        # wrap for like classical asteroids feel
        # only wrap when fully outside of screen

        # x axis
        if self.position.x < -self.radius:
            self.position.x = SCREEN_WIDTH + self.radius
        elif self.position.x > SCREEN_WIDTH + self.radius:
            self.position.x = -self.radius
        # y axis
        if self.position.y < -self.radius:
            self.position.y = SCREEN_HEIGHT + self.radius
        elif self.position.y > SCREEN_HEIGHT + self.radius:
            self.position.y = -self.radius

    # implemented by subclasses
    def draw(self, screen):
        # sub-classes must override
        pass

    def update(self, dt):
        # sub-classes must override
        pass

    # collisions
    def collides_with(self, other: "CircleShape") -> bool:
        # squared distance check (no sqrt for each  frame)
        delta = self.position - other.position
        r = self.radius + other.radius
        return delta.length_squared() <= (r * r)