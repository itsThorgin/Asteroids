import pygame
import random
from asteroid import Asteroid
from constants import *


class AsteroidField(pygame.sprite.Sprite):
    # each entry - inward dir, spawn_position_fn(t, radius), -y up, +y down
    edges = [
        # spawn left side, off screen, going +- right
        (pygame.Vector2(1, 0),  lambda y, r: pygame.Vector2(-(r + ASTEROID_SPAWN_MARGIN), y * SCREEN_HEIGHT)),
        # spawn right side, off screen, going +- left
        (pygame.Vector2(-1, 0), lambda y, r: pygame.Vector2(SCREEN_WIDTH + (r + ASTEROID_SPAWN_MARGIN), y * SCREEN_HEIGHT)),
        # spawn top side, off screen, going +- down
        (pygame.Vector2(0, 1),  lambda x, r: pygame.Vector2(x * SCREEN_WIDTH, -(r + ASTEROID_SPAWN_MARGIN))),
        # spawn bottom side, off screen, going +- up
        (pygame.Vector2(0, -1), lambda x, r: pygame.Vector2(x * SCREEN_WIDTH, SCREEN_HEIGHT + (r + ASTEROID_SPAWN_MARGIN))),
    ]

    def __init__(self):
        if hasattr(self, "containers"):
            super().__init__(self.containers)
        else:
            super().__init__()
        self.spawn_timer = 0.0

    def spawn(self, radius, position, velocity):
        asteroid = Asteroid(position.x, position.y, radius, root_id=None, root_radius=radius)
        asteroid.velocity = velocity

    @staticmethod
    def _is_offscreen(pos, r):
        return (pos.x < -r) or (pos.x > SCREEN_WIDTH + r) or (pos.y < -r) or (pos.y > SCREEN_HEIGHT + r)

    def update(self, dt):
        self.spawn_timer += dt

        while self.spawn_timer > ASTEROID_SPAWN_RATE:
            self.spawn_timer -= ASTEROID_SPAWN_RATE

            # choose size for offscreen placement
            radius = random.choice(ASTEROID_SPAWN_RADII)

            # pick an edge & inward direction
            inward, pos_fn = random.choice(self.edges)

            # pick velocity mostly inward (+- jitter)
            speed = random.uniform(ASTEROID_SPAWN_SPEED_MIN, ASTEROID_SPAWN_SPEED_MAX)
            angle_jitter = random.uniform(-ASTEROID_SPAWN_ANGLE_JITTER, ASTEROID_SPAWN_ANGLE_JITTER)
            direction = inward.rotate(angle_jitter)
            velocity = direction * speed

            # position along that edge
            t = random.uniform(0.0, 1.0)
            position = pos_fn(t, radius)

            # guarantee for offscreen spawn
            if not self._is_offscreen(position, radius):
                # snap based on chosen edge
                if inward.x > 0.5:        # from LEFT
                    position.x = -(radius + ASTEROID_SPAWN_MARGIN)
                elif inward.x < -0.5:     # from RIGHT
                    position.x = SCREEN_WIDTH + (radius + ASTEROID_SPAWN_MARGIN)
                elif inward.y > 0.5:      # from TOP
                    position.y = -(radius + ASTEROID_SPAWN_MARGIN)
                else:                      # from BOTTOM
                    position.y = SCREEN_HEIGHT + (radius + ASTEROID_SPAWN_MARGIN)

            self.spawn(radius, position, velocity)