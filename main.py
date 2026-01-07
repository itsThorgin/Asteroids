import pygame
from constants import *
from player import Player
from asteroid import Asteroid
from asteroidfield import AsteroidField
from shot import Shot
from score import ScoreManager, Leaderboard
from powerup import PowerUp, PowerUpSpawner

def init_round():
    # groups
    updatable = pygame.sprite.Group()
    drawable = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    shots = pygame.sprite.Group()
    powerups = pygame.sprite.Group()

    # containers
    Player.containers = (updatable, drawable)
    Asteroid.containers = (asteroids, updatable, drawable)
    AsteroidField.containers = (updatable,)
    Shot.containers = (shots, updatable, drawable)
    PowerUp.containers = (powerups, updatable, drawable)
    PowerUpSpawner.containers = (updatable,)

    # instances
    player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    field = AsteroidField()
    spawner = PowerUpSpawner(powerups, player_ref=player)

    # score for this round
    scorer = ScoreManager()

    return updatable, drawable, asteroids, shots, powerups, player, field, spawner, scorer

def prompt_name(screen, font):
    name = ""
    clock = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return name.strip() or "PLAYER"
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
                    if len(name) < 12 and event.unicode.isprintable():
                        name += event.unicode.upper()

        screen.fill((0, 0, 0))
        prompt = font.render("ENTER NAME:", False, "white")
        entry  = font.render(name + "_", False, "white")
        screen.blit(prompt, (SCREEN_WIDTH//2 - prompt.get_width()//2, SCREEN_HEIGHT//2 - 40))
        screen.blit(entry,  (SCREEN_WIDTH//2 - entry.get_width()//2,  SCREEN_HEIGHT//2))
        pygame.display.flip()
        clock.tick(30)

def game_over_menu(screen, font, leaderboard):
    # show leaderboard and wait for input.
    # returns "restart" or "exit".
    # keys: R / ENTER / SPACE = restart,  ESC / Q / window close = exit

    clock = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    return "exit"
                if event.key in (pygame.K_r, pygame.K_RETURN, pygame.K_SPACE):
                    return "restart"

        screen.fill((0, 0, 0))

        title = font.render("HIGH SCORES", False, "white")
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 40))

        y = 100
        for i, (n, s) in enumerate(leaderboard.top(10), start=1):
            line = font.render(f"{i:2d}. {n:<12} {s:>6}", False, "white")
            screen.blit(line, (SCREEN_WIDTH//2 - line.get_width()//2, y))
            y += 22

        hint = font.render("[ENTER/SPACE/R] Play Again   [ESC/Q] Exit", False, "white")
        screen.blit(hint, (SCREEN_WIDTH//2 - hint.get_width()//2, SCREEN_HEIGHT - 60))

        pygame.display.flip()
        clock.tick(30)

def segment_hits_circle(p0, p1, center, radius_sum_sq):
    # return True if segment (p0→p1) intersects a circle of given squared radius
    v = p1 - p0
    w = center - p0
    v_len2 = v.x * v.x + v.y * v.y
    if v_len2 == 0:
        return (w.x * w.x + w.y * w.y) <= radius_sum_sq
    t = max(0.0, min(1.0, (w.x * v.x + w.y * v.y) / v_len2))
    closest = p0 + v * t
    d = center - closest
    return (d.x * d.x + d.y * d.y) <= radius_sum_sq

def apply_bomb(player, asteroids, scorer, center=None):
    center = center if center is not None else player.position
    blast_r2 = POWERUP_BOMB_RADIUS * POWERUP_BOMB_RADIUS
    for asteroid in list(asteroids):
        if (asteroid.position - center).length_squared() <= blast_r2:
            asteroid.kill()  # gone, no splits
            family_cleared, from_big = scorer.asteroid_destroyed(asteroid, asteroids)
            if family_cleared and from_big:
                player.add_shield(1)

def handle_powerup_pickups(powerups, player, asteroids, scorer):
    for powerup in list(powerups):
        delta = powerup.position - player.position
        if delta.length_squared() <= (powerup.radius + player.radius) ** 2:
            kind = powerup.kind
            powerup.kill()
            if kind == "bomb":
                # delayed bomb: show ring, timed boom
                player.pending_bombs.append({"timer": 0.5, "pos": player.position.copy()})
            elif kind == "weapon":
                # faster fire rate
                player.activate_weapon_boost()
            elif kind == "control":
                # no drift
                player.activate_control_boost()
            elif kind == "overcharge":
                # shield overdrive
                player.activate_overcharge()

def update_pending_bombs(dt, player, asteroids, scorer, flashes):
    for bomb in list(player.pending_bombs):
        bomb["timer"] -= dt
        if bomb["timer"] <= 0:
            apply_bomb(player, asteroids, scorer, center=bomb["pos"])
            player.pending_bombs.remove(bomb)
            flashes.append({"pos": bomb["pos"], "timer": 0.2})

def draw_bomb_telegraphs(screen, pending_bombs):
    for bomb in pending_bombs:
        t = max(0.0, bomb["timer"])
        progress = 1.0 - min(1.0, t / 0.5)
        width = 1 + int(progress * 3)
        pygame.draw.circle(screen, (255, 235, 50), bomb["pos"], POWERUP_BOMB_RADIUS, width)

def draw_blast_flashes(screen, flashes):
    for flash in flashes:
        t = flash["timer"]
        if t <= 0:
            continue
        alpha = int(180 * (t / 0.2))
        r = POWERUP_BOMB_RADIUS
        size = int(r * 2 + 8)
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        center = (size * 0.5, size * 0.5)
        pygame.draw.circle(surf, (255, 235, 50, alpha), center, r, 2)
        pygame.draw.circle(surf, (255, 235, 50, max(0, alpha // 2)), center, max(0, r - 8), 0)
        base = (flash["pos"].x - size * 0.5, flash["pos"].y - size * 0.5)
        screen.blit(surf, base)

def main():
    pygame.init()

    font = pygame.font.SysFont(UI_FONT_NAME, UI_FONT_SIZE)
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    leaderboard = Leaderboard()

    while True:
        # start a fresh round
        updatable, drawable, asteroids, shots, powerups, player, field, spawner, scorer = init_round()
        bomb_flashes = []

        running = True
        while running:
            dt = clock.tick(60) / 1000
            dt = min(dt, 0.05) # no catch-up when on scoreboard

            # events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

            # update
            updatable.update(dt)
            handle_powerup_pickups(powerups, player, asteroids, scorer)
            update_pending_bombs(dt, player, asteroids, scorer, bomb_flashes)
            for flash in list(bomb_flashes):
                flash["timer"] -= dt
                if flash["timer"] <= 0:
                    bomb_flashes.remove(flash)

            # collisions: player vs asteroids -> end round (unless overcharged)
            for asteroid in list(asteroids):
                # distance check using shield radius when active
                delta = player.position - asteroid.position
                dist2 = delta.length_squared()

                # overcharge: smash asteroids, slow down a bit each hit
                if player.is_overcharged():
                    hit = dist2 <= (player.overcharge_radius() + asteroid.radius) ** 2
                    if hit:
                        asteroid.split()
                        player.overcharge_hit_slow()
                        family_cleared, from_big = scorer.asteroid_destroyed(asteroid, asteroids)
                        if family_cleared and from_big:
                            player.add_shield(1)
                        continue

                # 1) shield contact, only if shield is ready
                if player.has_shield() and player.shield_iframes <= 0:
                    sr = player.shield_radius()
                    if dist2 <= (sr + asteroid.radius) ** 2:
                        if player.consume_shield():
                            player.shield_iframes = 0.25  # about 15 frames @ 60fps
                            asteroid.split()
                            continue  # handled -> next asteroid

                # 2) hull contact (no shield)
                if dist2 <= (player.radius + asteroid.radius) ** 2:
                    running = False
                    break

            # collisions: shots vs asteroids -> split + score + shields on clear
            if running:
                for asteroid in list(asteroids):
                    for shot in list(shots):
                        r_sum = asteroid.radius + shot.radius
                        if segment_hits_circle(shot.prev_position, shot.position, asteroid.position, r_sum * r_sum):
                            hit = asteroid
                            asteroid.split()
                            shot.kill()

                            family_cleared, from_big = scorer.asteroid_destroyed(hit, asteroids)
                            if family_cleared and from_big:
                                player.add_shield(1)
                            break

            # draw
            screen.fill((0, 0, 0))
            draw_bomb_telegraphs(screen, player.pending_bombs)
            draw_blast_flashes(screen, bomb_flashes)
            score_surf = font.render(f"SCORE {scorer.score}", False, "white")
            screen.blit(score_surf, (10, 10))

            # shield charge
            pip_center_y = 36
            pip_spacing = 20
            pip_r = 6
            max_charges = 3
            for i in range(max_charges):
                cx = 12 + i * (2 * pip_r + pip_spacing) + pip_r
                cy = pip_center_y
                if i < player.shield_charges:
                    # filled
                    pygame.draw.circle(screen, (100, 200, 255), (cx, cy), pip_r, 0)
                else:
                    # outline
                    pygame.draw.circle(screen, (100, 200, 255), (cx, cy), pip_r, 2)

            # weapon boost indicator
            if player.weapon_boost_timer > 0:
                bar_w = 120
                bar_h = 10
                remaining = max(0.0, min(1.0, player.weapon_boost_timer / POWERUP_WEAPON_DURATION))
                filled_w = int(bar_w * remaining)
                x = 10
                y = 50
                pygame.draw.rect(screen, (60, 60, 60), pygame.Rect(x, y, bar_w, bar_h), 1)
                pygame.draw.rect(screen, (255, 180, 80), pygame.Rect(x + 1, y + 1, max(0, filled_w - 2), bar_h - 2))

            # control boost indicator
            if player.control_boost_timer > 0:
                bar_w = 120
                bar_h = 10
                remaining = max(0.0, min(1.0, player.control_boost_timer / POWERUP_CONTROL_DURATION))
                filled_w = int(bar_w * remaining)
                x = 10
                y = 66
                pygame.draw.rect(screen, (60, 60, 60), pygame.Rect(x, y, bar_w, bar_h), 1)
                pygame.draw.rect(screen, (120, 255, 150), pygame.Rect(x + 1, y + 1, max(0, filled_w - 2), bar_h - 2))

            # overcharge indicator
            if player.overcharge_timer > 0:
                bar_w = 120
                bar_h = 10
                remaining = max(0.0, min(1.0, player.overcharge_timer / POWERUP_OVERCHARGE_DURATION))
                filled_w = int(bar_w * remaining)
                x = 10
                y = 82
                pygame.draw.rect(screen, (60, 60, 60), pygame.Rect(x, y, bar_w, bar_h), 1)
                pygame.draw.rect(screen, (200, 200, 255), pygame.Rect(x + 1, y + 1, max(0, filled_w - 2), bar_h - 2))

            for obj in drawable:
                obj.draw(screen)
            pygame.display.flip()

        # round end - stop all spawners/objects
        for spr in list(updatable):
            spr.kill()
        shots.empty()

        # round ended: prompt name, save score, show menu
        name = prompt_name(screen, font)
        if name is not None:
            leaderboard.submit(name, scorer.score, overwrite=False)

        action = game_over_menu(screen, font, leaderboard)
        if action == "exit":
            pygame.quit()
            return
        # else "restart": loop continues and starts a new round


if __name__ == "__main__":
    main()
