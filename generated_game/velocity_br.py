import pygame
import random
import math
import time

# --- CONSTANTS & CONFIG ---
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
MAP_SIZE = 4000  # 4km simulated
TILE_SIZE = 100
PLAYER_SIZE = 32
VIEW_DISTANCE = 800

# Colors
COLOR_BG = (30, 30, 35)
COLOR_PLAYER = (50, 150, 255)
COLOR_BOT = (255, 100, 100)
COLOR_SHARD = (200, 255, 100)
COLOR_ZONE = (100, 100, 255, 100)
COLOR_WALL = (60, 60, 70)

# Weapon Types (Core Frames)
WEAPON_FRAMES = {
    "AR_FRAME": {"fire_rate": 0.15, "damage": 20, "velocity": 15, "spread": 0.05, "name": "Rifle Frame"},
    "SNIPER_FRAME": {"fire_rate": 1.2, "damage": 80, "velocity": 30, "spread": 0.01, "name": "Precision Frame"},
    "SMG_FRAME": {"fire_rate": 0.08, "damage": 12, "velocity": 12, "spread": 0.1, "name": "Rapid Frame"}
}

# Function Modules (Attachments)
FUNCTION_MODULES = {
    "BURST_MOD": {"rate_mult": 0.5, "dmg_mult": 1.1, "burst": 3, "name": "Burst Module"},
    "MEDIC_MOD": {"dmg_mult": -0.5, "heal": 10, "name": "Medic Module"},
    "STABILIZER_MOD": {"spread_mult": 0.3, "name": "Stabilizer"}
}

# --- ECS CORE ---

class Entity:
    def __init__(self, id):
        self.id = id

class Component:
    pass

class Transform(Component):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0

class Movement(Component):
    def __init__(self):
        self.vx = 0
        self.vy = 0
        self.speed = 5
        self.sprint_mult = 1.6
        self.stance = "STAND"  # STAND, CROUCH, PRONE
        self.is_sprinting = False

class Combat(Component):
    def __init__(self, frame_key):
        self.health = 100
        self.max_health = 100
        self.shield = 50
        self.frame = WEAPON_FRAMES[frame_key].copy()
        self.modules = []
        self.last_shot_time = 0
        self.ammo = 30
        self.reloading = False

class AI(Component):
    def __init__(self):
        self.target_pos = None
        self.state = "WANDER"
        self.timer = 0

class LootItem(Component):
    def __init__(self, type, data, name):
        self.type = type # "FRAME", "MODULE", "SHARD"
        self.data = data
        self.name = name

# --- GAME ENGINE SYSTEMS ---

class GameEngine:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Project: Velocity BR - Modular Mobile Architecture")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 18)
        self.large_font = pygame.font.SysFont("Arial", 32, bold=True)
        
        self.running = True
        self.entities = {}
        self.next_entity_id = 0
        
        # Camera
        self.camera_x = 0
        self.camera_y = 0
        
        # Zone
        self.zone_radius = MAP_SIZE // 1.5
        self.zone_center = (MAP_SIZE // 2, MAP_SIZE // 2)
        
        # Player reference
        self.player_id = self.create_player(MAP_SIZE // 2, MAP_SIZE // 2)
        
        # Environment
        self.walls = []
        self.generate_world()
        
        # Projectiles
        self.projectiles = []
        
        # UI State
        self.proximity_loot = []
        self.shards = 0

    def create_entity(self):
        eid = self.next_entity_id
        self.entities[eid] = {}
        self.next_entity_id += 1
        return eid

    def create_player(self, x, y):
        eid = self.create_entity()
        self.entities[eid]['transform'] = Transform(x, y)
        self.entities[eid]['movement'] = Movement()
        self.entities[eid]['combat'] = Combat("AR_FRAME")
        return eid

    def create_bot(self, x, y):
        eid = self.create_entity()
        self.entities[eid]['transform'] = Transform(x, y)
        self.entities[eid]['movement'] = Movement()
        self.entities[eid]['combat'] = Combat(random.choice(list(WEAPON_FRAMES.keys())))
        self.entities[eid]['ai'] = AI()
        return eid

    def create_loot(self, x, y, type, key):
        eid = self.create_entity()
        self.entities[eid]['transform'] = Transform(x, y)
        if type == "FRAME":
            self.entities[eid]['loot'] = LootItem(type, key, WEAPON_FRAMES[key]['name'])
        elif type == "MODULE":
            self.entities[eid]['loot'] = LootItem(type, key, FUNCTION_MODULES[key]['name'])
        elif type == "SHARD":
            self.entities[eid]['loot'] = LootItem(type, 10, "Aethel-Shard")
        return eid

    def generate_world(self):
        # Create some random walls (buildings)
        for _ in range(100):
            w = random.randint(100, 300)
            h = random.randint(100, 300)
            x = random.randint(0, MAP_SIZE - w)
            y = random.randint(0, MAP_SIZE - h)
            self.walls.append(pygame.Rect(x, y, w, h))
            
        # Create initial loot
        for _ in range(50):
            x, y = random.randint(100, MAP_SIZE-100), random.randint(100, MAP_SIZE-100)
            self.create_loot(x, y, "FRAME", random.choice(list(WEAPON_FRAMES.keys())))
            
        for _ in range(80):
            x, y = random.randint(100, MAP_SIZE-100), random.randint(100, MAP_SIZE-100)
            self.create_loot(x, y, "MODULE", random.choice(list(FUNCTION_MODULES.keys())))

        for _ in range(150):
            x, y = random.randint(100, MAP_SIZE-100), random.randint(100, MAP_SIZE-100)
            self.create_loot(x, y, "SHARD", None)

        # Create bots
        for _ in range(20):
            self.create_bot(random.randint(100, MAP_SIZE-100), random.randint(100, MAP_SIZE-100))

    def handle_input(self):
        keys = pygame.key.get_pressed()
        p_move = self.entities[self.player_id]['movement']
        p_trans = self.entities[self.player_id]['transform']
        
        p_move.vx, p_move.vy = 0, 0
        if keys[pygame.K_w]: p_move.vy = -1
        if keys[pygame.K_s]: p_move.vy = 1
        if keys[pygame.K_a]: p_move.vx = -1
        if keys[pygame.K_d]: p_move.vx = 1
        
        p_move.is_sprinting = keys[pygame.K_LSHIFT]
        
        # Stance logic
        if keys[pygame.K_c]: p_move.stance = "CROUCH"
        elif keys[pygame.K_z]: p_move.stance = "PRONE"
        else: p_move.stance = "STAND"

        # Rotation
        m_pos = pygame.mouse.get_pos()
        rel_x = m_pos[0] - (SCREEN_WIDTH // 2)
        rel_y = m_pos[1] - (SCREEN_HEIGHT // 2)
        p_trans.angle = math.degrees(math.atan2(rel_y, rel_x))

        # Shooting
        if pygame.mouse.get_pressed()[0]:
            self.shoot(self.player_id)
            
        # Looting
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    self.try_loot()

    def try_loot(self):
        p_trans = self.entities[self.player_id]['transform']
        p_combat = self.entities[self.player_id]['combat']
        
        for eid, comps in list(self.entities.items()):
            if 'loot' in comps:
                l_trans = comps['transform']
                dist = math.hypot(p_trans.x - l_trans.x, p_trans.y - l_trans.y)
                if dist < 60:
                    loot = comps['loot']
                    if loot.type == "FRAME":
                        p_combat.frame = WEAPON_FRAMES[loot.data].copy()
                        p_combat.modules = [] # Reset modules on frame swap
                    elif loot.type == "MODULE":
                        if loot.data not in p_combat.modules and len(p_combat.modules) < 3:
                            p_combat.modules.append(loot.data)
                    elif loot.type == "SHARD":
                        self.shards += 10
                    
                    del self.entities[eid]
                    break

    def shoot(self, eid):
        combat = self.entities[eid]['combat']
        trans = self.entities[eid]['transform']
        now = time.time()
        
        # Apply module modifiers
        fire_rate = combat.frame['fire_rate']
        for mod_id in combat.modules:
            mod = FUNCTION_MODULES[mod_id]
            if "rate_mult" in mod: fire_rate *= mod.rate_mult

        if now - combat.last_shot_time > fire_rate:
            combat.last_shot_time = now
            
            # Simple Projectile creation
            angle = math.radians(trans.angle)
            # Add spread
            spread = combat.frame['spread']
            for mod_id in combat.modules:
                if "spread_mult" in mod_id: spread *= FUNCTION_MODULES[mod_id]['spread_mult']
            
            angle += random.uniform(-spread, spread)
            
            self.projectiles.append({
                'x': trans.x,
                'y': trans.y,
                'vx': math.cos(angle) * combat.frame['velocity'],
                'vy': math.sin(angle) * combat.frame['velocity'],
                'owner': eid,
                'damage': combat.frame['damage'],
                'life': 60 # frames
            })

    def update(self):
        # 1. Update Zone
        self.zone_radius -= 0.05
        if self.zone_radius < 50: self.zone_radius = 50
        
        # 2. Movement & AI System
        for eid, comps in self.entities.items():
            if 'transform' in comps and 'movement' in comps:
                trans = comps['transform']
                move = comps['movement']
                
                # AI Logic (Simplified Tier 2/3 Simulation)
                if 'ai' in comps:
                    ai = comps['ai']
                    ai.timer -= 1
                    if ai.timer <= 0:
                        ai.target_pos = (random.randint(0, MAP_SIZE), random.randint(0, MAP_SIZE))
                        ai.timer = random.randint(60, 200)
                    
                    # Move towards target
                    dx = ai.target_pos[0] - trans.x
                    dy = ai.target_pos[1] - trans.y
                    dist = math.hypot(dx, dy)
                    if dist > 5:
                        move.vx, move.vy = dx/dist, dy/dist
                        trans.angle = math.degrees(math.atan2(dy, dx))
                    
                    # Randomly shoot at player if close
                    p_trans = self.entities[self.player_id]['transform']
                    if math.hypot(p_trans.x - trans.x, p_trans.y - trans.y) < 400:
                        trans.angle = math.degrees(math.atan2(p_trans.y - trans.y, p_trans.x - trans.x))
                        self.shoot(eid)

                # Velocity calculation
                speed = move.speed
                if move.stance == "CROUCH": speed *= 0.6
                if move.stance == "PRONE": speed *= 0.3
                if move.is_sprinting and move.stance == "STAND": speed *= move.sprint_mult
                
                new_x = trans.x + move.vx * speed
                new_y = trans.y + move.vy * speed
                
                # Collision with walls
                player_rect = pygame.Rect(new_x - PLAYER_SIZE//2, new_y - PLAYER_SIZE//2, PLAYER_SIZE, PLAYER_SIZE)
                collision = False
                for wall in self.walls:
                    if player_rect.colliderect(wall):
                        collision = True
                        break
                
                if not collision:
                    trans.x, trans.y = new_x, new_y
                
                # Zone Damage
                dist_to_center = math.hypot(trans.x - self.zone_center[0], trans.y - self.zone_center[1])
                if dist_to_center > self.zone_radius:
                    if 'combat' in comps:
                        comps['combat'].health -= 0.1

        # 3. Projectile System
        for p in self.projectiles[:]:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['life'] -= 1
            
            # Hit detection
            hit = False
            for eid, comps in self.entities.items():
                if 'transform' in comps and 'combat' in comps and eid != p['owner']:
                    t = comps['transform']
                    if math.hypot(p['x'] - t.x, p['y'] - t.y) < 20:
                        # Damage calc
                        combat = comps['combat']
                        damage = p['damage']
                        if combat.shield > 0:
                            combat.shield -= damage
                            if combat.shield < 0: combat.shield = 0
                        else:
                            combat.health -= damage
                        hit = True
                        break
            
            # Wall hit
            for wall in self.walls:
                if wall.collidepoint(p['x'], p['y']):
                    hit = True
                    break

            if hit or p['life'] <= 0:
                self.projectiles.remove(p)

        # 4. Clean up dead entities
        dead = []
        for eid, comps in self.entities.items():
            if 'combat' in comps and comps['combat'].health <= 0:
                dead.append(eid)
        for eid in dead:
            if eid == self.player_id:
                self.running = False # Game Over
            else:
                # Drop loot on death
                t = self.entities[eid]['transform']
                self.create_loot(t.x, t.y, "SHARD", None)
                del self.entities[eid]

        # Camera follow
        p_trans = self.entities[self.player_id]['transform']
        self.camera_x += (p_trans.x - SCREEN_WIDTH // 2 - self.camera_x) * 0.1
        self.camera_y += (p_trans.y - SCREEN_HEIGHT // 2 - self.camera_y) * 0.1

    def draw(self):
        self.screen.fill(COLOR_BG)
        
        # Grid/Floor
        start_x = int(self.camera_x // TILE_SIZE) * TILE_SIZE
        start_y = int(self.camera_y // TILE_SIZE) * TILE_SIZE
        for x in range(start_x, start_x + SCREEN_WIDTH + TILE_SIZE, TILE_SIZE):
            pygame.draw.line(self.screen, (40, 40, 45), (x - self.camera_x, 0), (x - self.camera_x, SCREEN_HEIGHT))
        for y in range(start_y, start_y + SCREEN_HEIGHT + TILE_SIZE, TILE_SIZE):
            pygame.draw.line(self.screen, (40, 40, 45), (0, y - self.camera_y), (SCREEN_WIDTH, y - self.camera_y))

        # Walls (Building Occlusion Simulation)
        for wall in self.walls:
            # Simple culling
            screen_rect = pygame.Rect(self.camera_x, self.camera_y, SCREEN_WIDTH, SCREEN_HEIGHT)
            if screen_rect.colliderect(wall):
                pygame.draw.rect(self.screen, COLOR_WALL, (wall.x - self.camera_x, wall.y - self.camera_y, wall.width, wall.height))
                pygame.draw.rect(self.screen, (80, 80, 90), (wall.x - self.camera_x, wall.y - self.camera_y, wall.width, wall.height), 2)

        # Zone
        pygame.draw.circle(self.screen, (50, 50, 200), (int(self.zone_center[0] - self.camera_x), int(self.zone_center[1] - self.camera_y)), int(self.zone_radius), 3)

        # Loot
        self.proximity_loot = []
        p_trans = self.entities[self.player_id]['transform']
        for eid, comps in self.entities.items():
            if 'loot' in comps:
                l_trans = comps['transform']
                dist = math.hypot(p_trans.x - l_trans.x, p_trans.y - l_trans.y)
                if dist < VIEW_DISTANCE:
                    color = (200, 200, 100)
                    if comps['loot'].type == "FRAME": color = (255, 100, 255)
                    if comps['loot'].type == "MODULE": color = (100, 255, 255)
                    pygame.draw.rect(self.screen, color, (l_trans.x - self.camera_x - 8, l_trans.y - self.camera_y - 8, 16, 16))
                    if dist < 100:
                        self.proximity_loot.append(comps['loot'].name)

        # Entities
        for eid, comps in self.entities.items():
            if 'transform' in comps:
                t = comps['transform']
                dist = math.hypot(p_trans.x - t.x, p_trans.y - t.y)
                if dist < VIEW_DISTANCE:
                    color = COLOR_PLAYER if eid == self.player_id else COLOR_BOT
                    
                    # Draw Direction Triangle
                    angle = math.radians(t.angle)
                    p1 = (t.x - self.camera_x + math.cos(angle) * 20, t.y - self.camera_y + math.sin(angle) * 20)
                    p2 = (t.x - self.camera_x + math.cos(angle + 2.5) * 15, t.y - self.camera_y + math.sin(angle + 2.5) * 15)
                    p3 = (t.x - self.camera_x + math.cos(angle - 2.5) * 15, t.y - self.camera_y + math.sin(angle - 2.5) * 15)
                    pygame.draw.polygon(self.screen, color, [p1, p2, p3])
                    
                    # Health Bar
                    if 'combat' in comps:
                        c = comps['combat']
                        pygame.draw.rect(self.screen, (255, 0, 0), (t.x - self.camera_x - 20, t.y - self.camera_y - 35, 40, 5))
                        pygame.draw.rect(self.screen, (0, 255, 0), (t.x - self.camera_x - 20, t.y - self.camera_y - 35, 40 * (c.health/c.max_health), 5))

        # Projectiles
        for p in self.projectiles:
            pygame.draw.circle(self.screen, (255, 255, 0), (int(p['x'] - self.camera_x), int(p['y'] - self.camera_y)), 3)

        # HUD
        self.draw_hud()

    def draw_hud(self):
        # Bottom Left: Health/Shield
        p_combat = self.entities[self.player_id]['combat']
        pygame.draw.rect(self.screen, (20, 20, 20), (20, SCREEN_HEIGHT - 80, 300, 60))
        # Shield
        pygame.draw.rect(self.screen, (0, 150, 255), (30, SCREEN_HEIGHT - 70, 280 * (p_combat.shield/100), 15))
        # Health
        pygame.draw.rect(self.screen, (50, 200, 50), (30, SCREEN_HEIGHT - 45, 280 * (p_combat.health/100), 20))
        
        # Bottom Right: Weapon & Modules
        frame_name = p_combat.frame['name']
        txt = self.large_font.render(frame_name, True, (255, 255, 255))
        self.screen.blit(txt, (SCREEN_WIDTH - 300, SCREEN_HEIGHT - 100))
        
        y_off = SCREEN_HEIGHT - 60
        for mod_key in p_combat.modules:
            mod_name = FUNCTION_MODULES[mod_key]['name']
            txt_mod = self.font.render(f"[+] {mod_name}", True, (100, 255, 255))
            self.screen.blit(txt_mod, (SCREEN_WIDTH - 300, y_off))
            y_off += 20

        # Top Right: Shards
        shard_txt = self.font.render(f"Aethel-shards: {self.shards}", True, COLOR_SHARD)
        self.screen.blit(shard_txt, (SCREEN_WIDTH - 200, 20))

        # Middle Right: Proximity Loot
        if self.proximity_loot:
            loot_title = self.font.render("NEARBY LOOT (E to Pick):", True, (200, 200, 200))
            self.screen.blit(loot_title, (SCREEN_WIDTH - 250, 200))
            for i, item in enumerate(self.proximity_loot[:5]):
                txt = self.font.render(f"- {item}", True, (255, 255, 255))
                self.screen.blit(txt, (SCREEN_WIDTH - 230, 225 + i * 20))

        # Center: Crosshair
        pygame.draw.circle(self.screen, (255, 255, 255), (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), 5, 1)
        
        # Telemetry
        fps_txt = self.font.render(f"FPS: {int(self.clock.get_fps())}", True, (0, 255, 0))
        self.screen.blit(fps_txt, (20, 20))
        ent_txt = self.font.render(f"Entities: {len(self.entities)}", True, (0, 255, 0))
        self.screen.blit(ent_txt, (20, 40))

    def run(self):
        while self.running:
            self.handle_input()
            self.update()
            self.draw()
            pygame.display.flip()
            self.clock.tick(FPS)
        pygame.quit()

if __name__ == "__main__":
    game = GameEngine()
    game.run()
