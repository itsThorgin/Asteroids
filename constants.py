SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

ASTEROID_MIN_RADIUS = 20
ASTEROID_KINDS = 3
ASTEROID_MAX_RADIUS = ASTEROID_MIN_RADIUS * ASTEROID_KINDS

PLAYER_RADIUS = 20
PLAYER_TURN_SPEED = 300
PLAYER_SPEED = 200

SHOT_RADIUS = 5
PLAYER_SHOOT_SPEED = 500
PLAYER_SHOOT_COOLDOWN = 0.3

# offscreen spawning
ASTEROID_SPAWN_MARGIN = 40          # how far beyond the edge to spawn
ASTEROID_SPAWN_RATE = 1.5           # seconds
ASTEROID_SPAWN_SPEED_MIN = 40       # px/sec
ASTEROID_SPAWN_SPEED_MAX = 120      # px/sec

# sizes
ASTEROID_LARGE_RADIUS  = ASTEROID_MIN_RADIUS * 3    # 60
ASTEROID_MEDIUM_RADIUS = ASTEROID_MIN_RADIUS * 2    # 40
ASTEROID_SMALL_RADIUS  = ASTEROID_MIN_RADIUS * 1    # 20
ASTEROID_SPAWN_RADII   = (ASTEROID_LARGE_RADIUS, ASTEROID_MEDIUM_RADIUS, ASTEROID_SMALL_RADIUS)

# asteroid behavior
ASTEROID_SPLIT_ANGLE_MIN = 20      # min divergence when splitting in deg
ASTEROID_SPLIT_ANGLE_MAX = 50      # max divergence when splitting in deg
ASTEROID_SPLIT_SPEED_MULT = 1.2    # velocity multiplier for asteroid fragments
ASTEROID_SPAWN_ANGLE_JITTER = 30   # random angle variance for main spawned asteroids in deg


# scoring
POINTS_LARGE  = 15
POINTS_MEDIUM = 25
POINTS_SMALL  = 35
CHAIN_BONUS   = 50 # bonus when you destroy whole asteroid chain from bigest to smallest in 10 sec

# leaderboard & ui
HIGHSCORES_PATH = "highscores.json"
UI_FONT_NAME    = "Courier New"     # or None to use default
UI_FONT_SIZE    = 18

# shots
SHOT_LIFETIME = 2
DESPAWN_MARGIN = 50

# shields
SHIELD_RADIUS_OFFSET = 12       # extra px beyond PLAYER_RADIUS
SHIELD_COLOR = (100, 200, 255)  # light cyan?
SHIELD_LINE_WIDTH = 2           # px
SHIELD_DASH_LEN = 8             # px along the circle
SHIELD_GAP_LEN = 6              # px gap between dashes

# power-ups
POWERUP_RADIUS = 14
POWERUP_DESPAWN_TIME = 5.0              # seconds before disappearing
POWERUP_SPAWN_INTERVAL_MIN = 20.0       # sec
POWERUP_SPAWN_INTERVAL_MAX = 40.0       # sec
POWERUP_BOMB_RADIUS = 350
POWERUP_WEAPON_DURATION = 5.0           # boost in sec
POWERUP_WEAPON_COOLDOWN = 0.12          # faster fire rate
POWERUP_SPREAD_ANGLE = 14               # degrees left/right for extra shots
POWERUP_CONTROL_DURATION = 15.0         # driftless flight time in sec
POWERUP_OVERCHARGE_DURATION = 10.0      # invulnerable + smash asteroids in sec
POWERUP_OVERCHARGE_SLOW = 0.66          # speed multiplier per hit while overcharged
POWERUP_OVERCHARGE_RADIUS_MULT = 2.0    # how much bigger than normal shield radius
