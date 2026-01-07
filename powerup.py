import random
import pygame
from circleshape import CircleShape
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    POWERUP_RADIUS, POWERUP_DESPAWN_TIME,
    POWERUP_SPAWN_INTERVAL_MIN, POWERUP_SPAWN_INTERVAL_MAX
)


class PowerUp(CircleShape):
    # kinds
    COLORS = {
        "bomb": (255, 235, 50),         # yellow
        "weapon": (255, 70, 70),        # red
        "control": (80, 230, 140),      # green
        "overcharge": (255, 255, 255),  # white outline
    }

    def __init__(self, x, y, kind: str):
        super().__init__(x, y, POWERUP_RADIUS)
        self.kind = kind
        self.ttl = POWERUP_DESPAWN_TIME

    def draw(self, screen):
        color = self.COLORS.get(self.kind, "white")
        pygame.draw.circle(screen, color, self.position, self.radius, 2)

        # simple icon per type
        if self.kind == "bomb":
            # nuclearish three wedges
            for ang in (0, 120, 240):
                start = self.position + pygame.Vector2(0, -4).rotate(ang)
                end = self.position + pygame.Vector2(0, -8).rotate(ang + 20)
                pygame.draw.line(screen, color, start, end, 2)
        elif self.kind == "weapon":
            pygame.draw.line(screen, color, self.position + (-6, 4), self.position + (0, -4), 2)
            pygame.draw.line(screen, color, self.position + (0, -4), self.position + (6, 4), 2)
        elif self.kind == "control":
            pygame.draw.rect(screen, color, pygame.Rect(self.position.x - 6, self.position.y - 3, 12, 6), 2)
        elif self.kind == "overcharge":
            pygame.draw.circle(screen, color, self.position, 6, 1)
            pygame.draw.circle(screen, color, self.position, 2, 0)

    def update(self, dt):
        self.ttl -= dt
        if self.ttl <= 0:
            self.kill()
        # wrap so it stays on screen if nudged
        self.wrap_position()


class PowerUpSpawner(pygame.sprite.Sprite):
    def __init__(self, powerup_group, player_ref=None):
        if hasattr(self, "containers"):
            super().__init__(self.containers)
        else:
            super().__init__()
        self.powerups = powerup_group
        self.player_ref = player_ref
        self.timer = random.uniform(POWERUP_SPAWN_INTERVAL_MIN, POWERUP_SPAWN_INTERVAL_MAX)

    def _random_position(self, radius):
        # bias spawn near player if available, but keep fully on screen
        if self.player_ref is not None:
            px, py = self.player_ref.position
            jitter = POWERUP_RADIUS * 12
            x = random.uniform(max(radius, px - jitter), min(SCREEN_WIDTH - radius, px + jitter))
            y = random.uniform(max(radius, py - jitter), min(SCREEN_HEIGHT - radius, py + jitter))
            return pygame.Vector2(x, y)
        else:
            return pygame.Vector2(
                random.uniform(radius, SCREEN_WIDTH - radius),
                random.uniform(radius, SCREEN_HEIGHT - radius)
            )

    def _next_spawn_time(self):
        return random.uniform(POWERUP_SPAWN_INTERVAL_MIN, POWERUP_SPAWN_INTERVAL_MAX)

    def update(self, dt):
        if len(self.powerups) > 0:
            return

        self.timer -= dt
        if self.timer > 0:
            return

        # spawn one power-up
        kind = random.choice(["bomb", "weapon", "control", "overcharge"])
        pos = self._random_position(POWERUP_RADIUS)
        PowerUp(pos.x, pos.y, kind)

        # reset timer
        self.timer = self._next_spawn_time()
