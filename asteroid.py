import pygame
from circleshape import CircleShape
import random
from constants import (
    ASTEROID_MIN_RADIUS, ASTEROID_SPLIT_ANGLE_MIN, ASTEROID_SPLIT_ANGLE_MAX, ASTEROID_SPLIT_SPEED_MULT,
    ASTEROID_LARGE_RADIUS, ASTEROID_MEDIUM_RADIUS, SCREEN_WIDTH, SCREEN_HEIGHT
)
import itertools

_id_gen = itertools.count(1)

class Asteroid(CircleShape):
    def __init__(self, x, y, radius, root_id=None, root_radius=None, parent_id=None, branch_id=None):
        super().__init__(x, y, radius)
        self.id = next(_id_gen)
        self._entered_screen = False
        
        # lineage
        self.parent_id = parent_id
        self.branch_id = branch_id  # None for not inside a branch

        # screen entering
        self._entered_screen = False

        # family roots for scoring/bonus
        if root_id is None:
            self.root_id = self.id
            self.root_radius = root_radius if root_radius is not None else radius
        else:
            self.root_id = root_id
            self.root_radius = root_radius if root_radius is not None else radius

        # visual state
        self.rotation = random.uniform(0, 360)
        self.spin = random.uniform(-25.0, 25.0)
        self._outline = self._generate_lumpy_outline()

    def _generate_lumpy_outline(self):
        # build polygons by sampling points around the circle
        # with jittered radius, points are relative to (0,0).

        # number of vertices
        n = random.randint(10, 16)

        # how lumpy it will be
        min_scale = 0.75   # inner “dents”
        max_scale = 1.00   # outer “bumps”

        # smoothing so it doesn’t look spiky
        smooth_strength = 0.35  # 0=no smooth, 1=very smooth

        # base equally spaced angles
        angles = [ (360.0 / n) * i for i in range(n) ]

        # raw jittered radii
        raw = [ self.radius * random.uniform(min_scale, max_scale) for _ in range(n) ]

        if smooth_strength > 0:
            smoothed = []
            for i in range(n):
                prev_r = raw[(i-1) % n]
                cur_r  = raw[i]
                next_r = raw[(i+1) % n]
                avg = (prev_r + cur_r + next_r) / 3.0
                r = (1.0 - smooth_strength) * cur_r + smooth_strength * avg
                smoothed.append(r)
            radii = smoothed
        else:
            radii = raw

        # build relative points around the center
        pts = []
        for ang in angles:
            # +Y for down, -Y for up -> then rotate.
            v = pygame.Vector2(0, -1).rotate(ang) * radii[len(pts)]
            pts.append(v)
        return pts

    def draw(self, screen):
        W, H = SCREEN_WIDTH, SCREEN_HEIGHT

        # do not render until it entered the playfield
        if not self._entered_screen and not self._is_inside_playfield():
            return

        if not hasattr(self, "_outline") or self._outline is None:
            self._outline = self._generate_lumpy_outline()

        # padding covers line width, pad to avoid edge clipping
        line_w = 2
        pad = line_w + 6
        r = self.radius
        size = int(r * 2) + pad * 2
        surf = pygame.Surface((size, size), pygame.SRCALPHA)

        cx = (size * 0.5)
        cy = (size * 0.5)

        # rotate into local coords (keep floats for aalines)
        pts_local = [pygame.Vector2(cx, cy) + p.rotate(self.rotation) for p in self._outline]
        # draw filled thin then an aa outline to close tiny gaps
        pygame.draw.polygon(surf, (255, 255, 255, 0), [(p.x, p.y) for p in pts_local], 0)  # no visible fill (alpha 0)
        pygame.draw.aalines(surf, (255, 255, 255), True, [(p.x, p.y) for p in pts_local], 1)
        pygame.draw.polygon(surf, "white", [(p.x, p.y) for p in pts_local], line_w)

        base_x = int(self.position.x - cx)
        base_y = int(self.position.y - cy)

        screen.blit(surf, (base_x, base_y))

    def _is_inside_playfield(self):
        return (0 <= self.position.x <= SCREEN_WIDTH and
                0 <= self.position.y <= SCREEN_HEIGHT)

    def update(self, dt):
        self.integrate(dt)
        if not self._entered_screen and self._is_inside_playfield():
            self._entered_screen = True

        # start wrapping after it has actually been once on the playfield
        if self._entered_screen:
            self.wrap_position()

        self.rotation = (self.rotation + self.spin * dt) % 360.0

    def split(self):
        # remove asteroid
        self.kill()

        # no split at minimum size
        if self.radius <= ASTEROID_MIN_RADIUS:
            return
        
        # fragments movement
        base_vel = self.velocity
        if base_vel.length_squared() < 1e-6:
            # random nudge if almost stationary
            angle = random.uniform(0, 360)
            base_vel = pygame.Vector2(1, 0).rotate(angle) * 5

        # random split angle and two diverging velocities
        random_angle = random.uniform(ASTEROID_SPLIT_ANGLE_MIN, ASTEROID_SPLIT_ANGLE_MAX)
        v1 = base_vel.rotate(+random_angle) * ASTEROID_SPLIT_SPEED_MULT 
        v2 = base_vel.rotate(-random_angle) * ASTEROID_SPLIT_SPEED_MULT

        # reduce radius for fragments
        new_radius = self.radius - ASTEROID_MIN_RADIUS

        # branch assignment for children
        if self.radius >= ASTEROID_LARGE_RADIUS and new_radius == ASTEROID_MEDIUM_RADIUS:
            # BIG -> MEDIUM: start two new branches, each medium is the head of its branch
            a1 = Asteroid(self.position.x, self.position.y, new_radius,
                          root_id=self.root_id, root_radius=self.root_radius,
                          parent_id=self.id, branch_id=None)  # temp None
            a1.branch_id = a1.id  # its own branch id
            a1.velocity = v1

            a2 = Asteroid(self.position.x, self.position.y, new_radius,
                          root_id=self.root_id, root_radius=self.root_radius,
                          parent_id=self.id, branch_id=None)
            a2.branch_id = a2.id
            a2.velocity = v2

        else:
            # MEDIUM -> SMALL: inherit branch from parent
            a1 = Asteroid(self.position.x, self.position.y, new_radius,
                          root_id=self.root_id, root_radius=self.root_radius,
                          parent_id=self.id, branch_id=self.branch_id)
            a1.velocity = v1

            a2 = Asteroid(self.position.x, self.position.y, new_radius,
                          root_id=self.root_id, root_radius=self.root_radius,
                          parent_id=self.id, branch_id=self.branch_id)
            a2.velocity = v2
