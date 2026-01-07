import json
import os
from constants import (POINTS_LARGE, POINTS_MEDIUM, POINTS_SMALL, CHAIN_BONUS,
                       HIGHSCORES_PATH, ASTEROID_MIN_RADIUS, ASTEROID_LARGE_RADIUS,
                       CHAIN_TIME_LIMIT)

class ScoreManager:
    def __init__(self):
        self.score = 0
        self.chain_started_at = {}

    def points_for_radius(self, radius):
        # infer size by how many steps of ASTEROID_MIN_RADIUS
        steps = int(round(radius / ASTEROID_MIN_RADIUS))
        if steps >= 3:  # large
            return POINTS_LARGE
        elif steps == 2:  # medium
            return POINTS_MEDIUM
        else:  # small
            return POINTS_SMALL

    def asteroid_destroyed(self, asteroid, asteroids_group, now):
        # record first kill in the family
        root = asteroid.root_id
        if root not in self.chain_started_at:
            self.chain_started_at[root] = now

        # base points
        self.score += self.points_for_radius(asteroid.radius)

        # chain bonus, family cleared when no asteroid with this root_id remains + timer
        family_left = any(a.root_id == root for a in asteroids_group)
        family_cleared = not family_left

        got_chain_bonus = False
        if family_cleared:
            start = self.chain_started_at.get(root, now)
            if (now - start) <= CHAIN_TIME_LIMIT:
                self.score += CHAIN_BONUS
                got_chain_bonus = True
            # cleanup timer
            self.chain_started_at.pop(root, None)

        # only BIG-origin families are eligible for shield
        from_big = getattr(asteroid, "root_radius", 0) >= ASTEROID_LARGE_RADIUS

        return family_cleared, from_big, got_chain_bonus


class Leaderboard:
    def __init__(self, path=HIGHSCORES_PATH):
        self.path = path
        self.scores = self._load()

    def _load(self):
        if not os.path.exists(self.path):
            return {}
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.scores, f, indent=2)

    def submit(self, name, score, overwrite=False):
        # overwrite=True  -> same name replaces previous score
        # overwrite=False -> keep the best
        
        if overwrite or name not in self.scores:
            self.scores[name] = score
        else:
            self.scores[name] = max(self.scores[name], score)
        self.save()

    def top(self, n=10):
        return sorted(self.scores.items(), key=lambda kv: kv[1], reverse=True)[:n]
