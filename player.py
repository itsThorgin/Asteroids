import pygame
from circleshape import CircleShape
from constants import (
    PLAYER_RADIUS, PLAYER_TURN_SPEED, PLAYER_SPEED, PLAYER_SHOOT_SPEED,
    PLAYER_SHOOT_COOLDOWN, SCREEN_WIDTH, SCREEN_HEIGHT,
    SHIELD_RADIUS_OFFSET, SHIELD_COLOR, SHIELD_LINE_WIDTH, SHIELD_DASH_LEN, SHIELD_GAP_LEN,
    POWERUP_WEAPON_DURATION, POWERUP_WEAPON_COOLDOWN, POWERUP_SPREAD_ANGLE,
    POWERUP_CONTROL_DURATION, POWERUP_OVERCHARGE_DURATION, POWERUP_OVERCHARGE_SLOW, POWERUP_OVERCHARGE_RADIUS_MULT
)
from shot import Shot
import math

class Player(CircleShape):
    def __init__(self, x: int, y: int):
        super().__init__(x, y, PLAYER_RADIUS)
        self.rotation = 0
        self.shoot_timer = 0
        self.velocity = pygame.Vector2(0, 0)
        self.shield_charges = 0
        self.shield_iframes = 0.0
        self.weapon_boost_timer = 0.0
        self.control_boost_timer = 0.0
        self.overcharge_timer = 0.0
        self.pending_bombs = []

    # shields
    def has_shield(self) -> bool:
        return self.shield_charges > 0

    def add_shield(self, n: int = 1) -> None:
        self.shield_charges = min(3, self.shield_charges + n)

    def consume_shield(self) -> bool:
        if self.shield_charges > 0:
            self.shield_charges -= 1
            return True
        return False

    def shield_radius(self) -> float:
        return self.radius + SHIELD_RADIUS_OFFSET

    def overcharge_radius(self) -> float:
        return self.shield_radius() * POWERUP_OVERCHARGE_RADIUS_MULT

    def collision_radius(self) -> float:
        return self.shield_radius() if self.has_shield() else self.radius

    def _draw_dashed_circle(self, screen, center, radius, dash_len, gap_len, width, color):
        # approx. circumference and draw visuals/dashes
        circumference = 2 * math.pi * radius
        # how many dashes fit around
        segment_len = max(1, dash_len + gap_len)
        # evenly split circle
        count = max(12, int(circumference / segment_len))
        angle_step = 2 * math.pi / count
        # shorter dash to avoid overlap, converting from linear dash to radians
        dash_angle = (dash_len / circumference) * 2 * math.pi
        dash_angle = min(dash_angle, angle_step * 0.9)

        rect = pygame.Rect(0, 0, radius * 2, radius * 2)
        rect.center = (center.x, center.y)

        for i in range(count):
            start_ang = i * angle_step
            end_ang = start_ang + dash_angle
            pygame.draw.arc(screen, color, rect, start_ang, end_ang, width)

    def triangle(self):
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        right = pygame.Vector2(0, 1).rotate(self.rotation + 90) * self.radius / 1.5
        a = self.position + forward * self.radius               # nose
        b = self.position - forward * self.radius - right       # left tail
        c = self.position - forward * self.radius + right       # right tail
        return [a, b, c]

    def draw(self, screen):
        # ship
        pygame.draw.polygon(screen, "white", self.triangle(), 2)
        # shields
        if self.has_shield():
            self._draw_dashed_circle(
                screen,
                self.position,
                self.shield_radius(),
                SHIELD_DASH_LEN,
                SHIELD_GAP_LEN,
                SHIELD_LINE_WIDTH,
                SHIELD_COLOR
            )
        # overcharge outer ring
        if self.is_overcharged():
            pygame.draw.circle(screen, (200, 220, 255), self.position, self.overcharge_radius(), 2)

    # weapon boost
    def is_weapon_boosted(self) -> bool:
        return self.weapon_boost_timer > 0

    def activate_weapon_boost(self):
        self.weapon_boost_timer = POWERUP_WEAPON_DURATION

    def is_control_boosted(self) -> bool:
        return self.control_boost_timer > 0

    def activate_control_boost(self):
        self.control_boost_timer = POWERUP_CONTROL_DURATION

    def is_overcharged(self) -> bool:
        return self.overcharge_timer > 0

    def activate_overcharge(self):
        self.overcharge_timer = POWERUP_OVERCHARGE_DURATION

    def overcharge_hit_slow(self):
        # slow ship a bit after smashing an asteroid
        self.velocity *= POWERUP_OVERCHARGE_SLOW

    def rotate(self, dt):
        self.rotation += PLAYER_TURN_SPEED * dt

    def update(self, dt):
        if self.shoot_timer > 0:
            self.shoot_timer -= dt
        if self.shield_iframes > 0:
            self.shield_iframes -= dt
        if self.weapon_boost_timer > 0:
            self.weapon_boost_timer -= dt
        if self.control_boost_timer > 0:
            self.control_boost_timer -= dt
        if self.overcharge_timer > 0:
            self.overcharge_timer -= dt

        keys = pygame.key.get_pressed()

        # rotation
        if keys[pygame.K_a]:
            self.rotate(-dt)

        if keys[pygame.K_d]:
            self.rotate(dt)

        # thrust
        # player_speed - thrust per second
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        thrust = pygame.Vector2(0, 0)

        if keys[pygame.K_w]:
            thrust += forward * PLAYER_SPEED

        if keys[pygame.K_s]:
            # lighter reverse
            thrust -= forward * (0.5 * PLAYER_SPEED)

        if self.is_control_boosted():
            # perfect control: no drift, velocity snaps to input
            if thrust.length_squared() > 0:
                self.velocity = thrust.normalize() * PLAYER_SPEED
            else:
                self.velocity.update(0, 0)
        else:
            # velocity with inertia
            self.velocity += thrust * dt

        # position
        self.position += self.velocity * dt

        # screen wrap
        self.wrap_position()

        # shooting
        if keys[pygame.K_SPACE]:
            self.shoot()

    def shoot(self):
        if self.shoot_timer > 0:
            return

        cooldown = POWERUP_WEAPON_COOLDOWN if self.is_weapon_boosted() else PLAYER_SHOOT_COOLDOWN
        spreads = [0]
        if self.is_weapon_boosted():
            spreads = [0, -POWERUP_SPREAD_ANGLE, POWERUP_SPREAD_ANGLE]

        # improving looks
        nose = self.triangle()[0]
        for ang in spreads:
            shot = Shot(nose.x, nose.y)
            shot.velocity = pygame.Vector2(0, 1).rotate(self.rotation + ang) * PLAYER_SHOOT_SPEED

        self.shoot_timer = cooldown
