
import pygame
import random
import math

# --- 1. Game Configuration (Data-Driven aspect) ---
# Screen settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (100, 100, 100)
DARK_GREEN = (0, 100, 0)
ORANGE = (255, 165, 0)
LIGHT_BLUE = (173, 216, 230) # For player
DARK_RED = (139, 0, 0) # For bots

# Game Rules
GAME_RULES = {
    "player_speed": 5,
    "bot_speed": 3,
    "player_health": 100,
    "bot_health": 50,
    "start_bots": 8, # Simplified, not 60-100
    "zone_start_radius": 350,
    "zone_shrink_speed": 0.05, # pixels per frame
    "zone_damage_interval": 60, # frames
    "zone_damage": 5,
    "loot_spawn_count": 10,
    "initial_weapon": "Pistol"
}

# Weapon Data (Modular Weapon Handling)
WEAPON_DATA = {
    "Pistol": {
        "damage": 10,
        "fire_rate": 20, # frames between shots (60 frames = 1 second)
        "bullet_speed": 10,
        "bullet_size": 5,
        "color": GRAY,
        "spread": 0,
        "num_pellets": 1
    },
    "Assault Rifle": {
        "damage": 15,
        "fire_rate": 8,
        "bullet_speed": 15,
        "bullet_size": 7,
        "color": ORANGE,
        "spread": 0,
        "num_pellets": 1
    },
    "Shotgun": {
        "damage": 15, # Damage per pellet
        "fire_rate": 40,
        "bullet_speed": 8,
        "bullet_size": 6,
        "color": RED,
        "spread": 25, # Angle of spread in degrees
        "num_pellets": 5 # Number of pellets
    }
}

# Item Data (Modular Item System)
ITEM_DATA = {
    "Med Kit": {
        "type": "heal",
        "amount": 50,
        "color": GREEN,
        "radius": 10,
        "item_name": "Med Kit"
    },
    "Assault Rifle": {
        "type": "weapon",
        "color": ORANGE,
        "radius": 10,
        "item_name": "Assault Rifle"
    },
    "Shotgun": {
        "type": "weapon",
        "color": RED,
        "radius": 10,
        "item_name": "Shotgun"
    }
}

# --- 2. Game Classes (Modularity) ---

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(LIGHT_BLUE)
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.health = GAME_RULES["player_health"]
        self.speed = GAME_RULES["player_speed"]
        self.equipped_weapon = GAME_RULES["initial_weapon"]
        self.last_shot_time = 0

    def move(self, dx, dy):
        if dx != 0 and dy != 0: # Normalize diagonal movement
            magnitude = math.sqrt(dx**2 + dy**2)
            dx /= magnitude
            dy /= magnitude
        
        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed
        
        # Keep player on screen
        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(SCREEN_WIDTH, self.rect.right)
        self.rect.top = max(0, self.rect.top)
        self.rect.bottom = min(SCREEN_HEIGHT, self.rect.bottom)

    def shoot(self, target_pos, current_time):
        weapon_config = WEAPON_DATA[self.equipped_weapon]
        if current_time - self.last_shot_time > weapon_config["fire_rate"]:
            self.last_shot_time = current_time
            
            bullets_fired = []
            num_pellets = weapon_config.get("num_pellets", 1)
            spread = weapon_config.get("spread", 0)

            for _ in range(num_pellets):
                bullets_fired.append(Bullet(self.rect.center, target_pos, weapon_config["bullet_speed"], 
                                            weapon_config["bullet_size"], weapon_config["damage"], 
                                            weapon_config["color"], self, spread))
            return bullets_fired
        return [] # Return empty list if not shooting

    def take_damage(self, amount):
        self.health -= amount
        if self.health < 0:
            self.health = 0

    def heal(self, amount):
        self.health += amount
        if self.health > GAME_RULES["player_health"]:
            self.health = GAME_RULES["player_health"]

    def pick_up_item(self, item_name):
        item_config = ITEM_DATA.get(item_name)
        if item_config:
            if item_config["type"] == "weapon":
                self.equipped_weapon = item_name
                print(f"Player picked up {item_name}. Equipped {self.equipped_weapon}")
            elif item_config["type"] == "heal":
                self.heal(item_config["amount"])
                print(f"Player used {item_name} and healed {item_config['amount']} HP.")


class Bot(pygame.sprite.Sprite):
    def __init__(self, player_ref):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(DARK_RED)
        # Spawn bots randomly within screen bounds but not too close to player initially
        while True:
            pos_x = random.randint(0, SCREEN_WIDTH)
            pos_y = random.randint(0, SCREEN_HEIGHT)
            if math.hypot(pos_x - player_ref.rect.centerx, pos_y - player_ref.rect.centery) > 200:
                self.rect = self.image.get_rect(center=(pos_x, pos_y))
                break

        self.health = GAME_RULES["bot_health"]
        self.speed = GAME_RULES["bot_speed"]
        self.player_ref = player_ref
        self.last_shot_time = 0
        self.equipped_weapon = "Pistol" # Bots use basic pistol for simplicity

    def update(self, current_time):
        # Simple AI: Move towards player and shoot
        if self.health <= 0:
            self.kill()
            return []

        target_x, target_y = self.player_ref.rect.center
        dx = target_x - self.rect.centerx
        dy = target_y - self.rect.centery
        distance = math.sqrt(dx**2 + dy**2)

        if distance > 150: # Move closer if too far
            if distance != 0:
                self.rect.x += int(dx / distance * self.speed)
                self.rect.y += int(dy / distance * self.speed)
        else: # Shoot if close enough
            return self.shoot(self.player_ref.rect.center, current_time)
        return []

    def shoot(self, target_pos, current_time):
        weapon_config = WEAPON_DATA[self.equipped_weapon]
        if current_time - self.last_shot_time > weapon_config["fire_rate"] * 2: # Bots shoot slower
            self.last_shot_time = current_time
            return [Bullet(self.rect.center, target_pos, weapon_config["bullet_speed"], 
                            weapon_config["bullet_size"], weapon_config["damage"], 
                            weapon_config["color"], self)]
        return []

    def take_damage(self, amount):
        self.health -= amount
        if self.health < 0:
            self.health = 0


class Bullet(pygame.sprite.Sprite):
    def __init__(self, start_pos, target_pos, speed, size, damage, color, owner, spread=0):
        super().__init__()
        self.image = pygame.Surface((size, size))
        self.image.fill(color)
        self.rect = self.image.get_rect(center=start_pos)
        self.speed = speed
        self.damage = damage
        self.owner = owner # Reference to the entity that fired it

        # Calculate direction vector
        dx = target_pos[0] - start_pos[0]
        dy = target_pos[1] - start_pos[1]
        
        # Apply spread for shotguns
        if spread > 0:
            angle = math.atan2(dy, dx)
            spread_angle = random.uniform(-math.radians(spread), math.radians(spread))
            # Recalculate dx, dy with spread angle
            dx = math.cos(angle + spread_angle)
            dy = math.sin(angle + spread_angle)
            
        dist = math.sqrt(dx**2 + dy**2)
        if dist == 0:
            self.vel_x, self.vel_y = 0, 0
        else:
            self.vel_x = (dx / dist) * self.speed
            self.vel_y = (dy / dist) * self.speed
            

    def update(self):
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        # Remove bullet if it goes off screen
        if not (0 <= self.rect.x <= SCREEN_WIDTH and 0 <= self.rect.y <= SCREEN_HEIGHT):
            self.kill()


class Item(pygame.sprite.Sprite):
    def __init__(self, name):
        super().__init__()
        self.name = name
        config = ITEM_DATA[name]
        self.image = pygame.Surface((config["radius"] * 2, config["radius"] * 2))
        self.image.fill(config["color"])
        self.rect = self.image.get_rect(center=(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT)))


class ApexZone:
    def __init__(self):
        self.center_x = SCREEN_WIDTH // 2
        self.center_y = SCREEN_HEIGHT // 2
        self.radius = GAME_RULES["zone_start_radius"]
        self.shrink_speed = GAME_RULES["zone_shrink_speed"]
        self.damage_counter = 0

    def update(self):
        if self.radius > 50: # Don't shrink indefinitely, leave a small safe zone
            self.radius -= self.shrink_speed
        else:
            self.radius = 50 # Minimum radius

    def draw(self, screen):
        # Draw outer edge of the zone (red circle)
        pygame.draw.circle(screen, RED, (int(self.center_x), int(self.center_y)), int(self.radius), 5)

    def is_inside(self, entity_pos):
        distance = math.sqrt((entity_pos[0] - self.center_x)**2 + (entity_pos[1] - self.center_y)**2)
        return distance <= self.radius

    def apply_damage(self, player_obj):
        if not self.is_inside(player_obj.rect.center):
            self.damage_counter += 1
            if self.damage_counter >= GAME_RULES["zone_damage_interval"]:
                player_obj.take_damage(GAME_RULES["zone_damage"])
                self.damage_counter = 0


# --- 3. Game Initialization ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Apex Zone: Pygame Edition")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

# --- 4. Game State Management ---
GAME_STATE_START = 0
GAME_STATE_PLAYING = 1
GAME_STATE_GAME_OVER = 2
GAME_STATE_WIN = 3

current_game_state = GAME_STATE_START

def reset_game():
    global player, all_sprites, bots, bullets, items, apex_zone, current_game_state
    
    player = Player()
    
    all_sprites = pygame.sprite.Group()
    bots = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    items = pygame.sprite.Group()
    
    all_sprites.add(player)
    
    for _ in range(GAME_RULES["start_bots"]):
        bot = Bot(player)
        all_sprites.add(bot)
        bots.add(bot)

    # Spawn some random loot
    available_item_names = list(ITEM_DATA.keys())
    for _ in range(GAME_RULES["loot_spawn_count"]):
        item_name = random.choice(available_item_names)
        item = Item(item_name)
        all_sprites.add(item)
        items.add(item)

    apex_zone = ApexZone()
    current_game_state = GAME_STATE_PLAYING

# Initial game setup
reset_game()
current_game_state = GAME_STATE_START # Start at the title screen

running = True

# --- 5. Game Loop ---
while running:
    current_time = pygame.time.get_ticks() # Milliseconds since pygame.init()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if current_game_state == GAME_STATE_START and event.key == pygame.K_SPACE:
                reset_game()
            elif (current_game_state == GAME_STATE_GAME_OVER or current_game_state == GAME_STATE_WIN) and event.key == pygame.K_r:
                reset_game()

    if current_game_state == GAME_STATE_PLAYING:
        # Player movement
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = 1
        player.move(dx, dy)

        # Player shooting
        if pygame.mouse.get_pressed()[0]: # Left mouse button
            mouse_pos = pygame.mouse.get_pos()
            new_bullets = player.shoot(mouse_pos, current_time)
            for bullet in new_bullets:
                all_sprites.add(bullet)
                bullets.add(bullet)

        # Update all sprites (bullets, bots)
        # Note: Bots' update method can also return bullets, so iterate separately
        for sprite in all_sprites:
            if isinstance(sprite, Bot):
                bot_bullets = sprite.update(current_time)
                for bullet in bot_bullets:
                    all_sprites.add(bullet)
                    bullets.add(bullet)
            elif isinstance(sprite, Bullet):
                sprite.update()
        
        # Player update (for consistency, though its internal state changes via input)
        player.update() 

        # Apex Zone updates
        apex_zone.update()
        apex_zone.apply_damage(player)

        # Collision Detection
        # Player-Item collision
        player_item_hits = pygame.sprite.spritecollide(player, items, True)
        for item in player_item_hits:
            player.pick_up_item(item.name)

        # Bullet-entity collision
        # Iterate over a copy to safely remove bullets
        for bullet in list(bullets): 
            if bullet.owner == player:
                # Player's bullet, check collision with bots
                hits = pygame.sprite.spritecollide(bullet, bots, False) 
                for bot_hit in hits:
                    bot_hit.take_damage(bullet.damage)
                    if bullet in bullets: # Ensure bullet hasn't already been removed
                        bullet.kill() # Bullet disappears after hitting one bot (or one pellet)
                        break # Prevent one pellet from hitting multiple bots (shotgun)
            else: # Must be a bot's bullet (in this simple setup)
                # Bot's bullet, check collision with player
                if pygame.sprite.collide_rect(bullet, player):
                    player.take_damage(bullet.damage)
                    bullet.kill()

        # Check for game over or win conditions
        if player.health <= 0:
            current_game_state = GAME_STATE_GAME_OVER
        elif len(bots) == 0:
            current_game_state = GAME_STATE_WIN

    # Drawing
    screen.fill(DARK_GREEN) # Background for the map

    if current_game_state == GAME_STATE_START:
        start_text = font.render("APEX ZONE (Pygame Edition)", True, WHITE)
        start_text_rect = start_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        screen.blit(start_text, start_text_rect)

        press_space_text = font.render("Press SPACE to Start", True, WHITE)
        press_space_text_rect = press_space_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        screen.blit(press_space_text, press_space_text_rect)

    elif current_game_state == GAME_STATE_PLAYING:
        all_sprites.draw(screen)
        apex_zone.draw(screen)

        # Draw UI
        health_text = font.render(f"HP: {player.health}/{GAME_RULES['player_health']}", True, WHITE)
        screen.blit(health_text, (10, 10))

        weapon_text = font.render(f"Weapon: {player.equipped_weapon}", True, WHITE)
        screen.blit(weapon_text, (10, 50))

        bots_left_text = font.render(f"Bots Left: {len(bots)}", True, WHITE)
        screen.blit(bots_left_text, (SCREEN_WIDTH - bots_left_text.get_width() - 10, 10))

    elif current_game_state == GAME_STATE_GAME_OVER:
        game_over_text = font.render("GAME OVER!", True, RED)
        game_over_text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        screen.blit(game_over_text, game_over_text_rect)

        restart_text = font.render("Press 'R' to Restart", True, WHITE)
        restart_text_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        screen.blit(restart_text, restart_text_rect)

    elif current_game_state == GAME_STATE_WIN:
        win_text = font.render("YOU WIN! Last player standing!", True, GREEN)
        win_text_rect = win_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        screen.blit(win_text, win_text_rect)

        restart_text = font.render("Press 'R' to Play Again", True, WHITE)
        restart_text_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        screen.blit(restart_text, restart_text_rect)

    # Update display
    pygame.display.flip()

    # Cap frame rate
    clock.tick(FPS)

pygame.quit()
