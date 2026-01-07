# Asteroids

Because recreating a classic arcade game is basically a rite of passage.

This is a **Python + Pygame** recreation of the legendary *Asteroids*. Featuring familiar chaos and a few of my own twists that make surviving space *slightly* less unfair.

---

## Gameplay Overview

You pilot a tiny spaceship in a universe filled with hostile rocks.

Destroy asteroids, chain kills for bonuses, collect power-ups that temporarily make you feel powerful, and chase high scores that will absolutely be lost to a single mistake.

---

## Scoring System

Not all asteroids are created equal:

- **Smaller asteroids = higher score**

- Big asteroids shatter into medium ones
- Medium asteroids shatter into small ones
- Small asteroids shatter into.. nah, it stops here

### Asteroid Family Bonus

If you destroy:
- **1 big asteroid**
- **2 medium asteroids**
- **4 small asteroids**

…all **within 10 seconds** you get:

- **Bonus score**
- **+1 shield charge**

wow.

---

## Shield System

- You can hold up to **3 shield charges**
- Shields can be earned via:
  - Asteroid family bonuses
  - Overcharge power-up (grants one if you have none)
- Each charge prevents one mistake

---

## Power-Ups

Power-ups prefer to spawn **near the player** and only **one can exist at a time**.

There are **4 power-ups**:

### Bomb
- Destroys **all asteroids within a radius**
- Goes boom...

### Weapon Upgrade
- Increases fire rate
- Adds **two angled side guns**
- Turns *pew pew* into *brrrrt*

### Movement Upgrade
- Disables drifting
- Movement becomes precise, controlled, and suspiciously comfortable

### Shield Overcharge
- Grants **temporary invulnerability**
- You can destroy asteroids just by touching them
- Each hit **slows you down**
- Grants one shield charge if you have none

---

## Controls

- WASD to move
- Space to shoot

---

## High Scores

- Stored locally in a `.json`

---

## License

Guess that if you take some code from this, mentioning the source would be nice.
