import pygame
from maps import *
import math
from settings import *
pygame.init()

class Door:
    def __init__(self, door):
        self.x = door[0] - 1
        self.y = door[1] - 1
        self.spawn_direction = door[2]
        self.target_room = door[3]
        self.target_doorway = door[4]
        self.rect = pygame.Rect(self.x * TILE_SIZE - (TILE_SIZE // 2), self.y * TILE_SIZE  - (TILE_SIZE // 2), TILE_SIZE * 2, TILE_SIZE * 2)
    def draw(self, win, camera):
        offset_pos = camera.custom_draw(self)  # Get the offset position
        adjusted_rect = pygame.Rect(offset_pos, (TILE_SIZE * 2, TILE_SIZE * 2))
        pygame.draw.rect(win, (97, 48, 2), adjusted_rect)

class DungeonMap:
    def __init__(self, game):
        self.game = game
        self.maps = {
            'start_room': start_room,
            'key_room_1': key_room_1,
            'key_room_2_level_1': key_room_2_level_1,
            'key_room_2_level_2': key_room_2_level_2,
            'key_room_2': key_room_2,
            'key_room_3_level_1': key_room_3_level_1,
            'key_room_3_level_2': key_room_3_level_2,
            'key_room_3': key_room_3,
            'final_boss_room' : final_boss_room
        }
        self.doors = {
            'start_room': start_room_doorways,
            'key_room_1': key_room_1_doorways,
            'key_room_2_level_1': key_room_2_level_1_doorways,
            'key_room_2_level_2': key_room_2_level_2_doorways,
            'key_room_2': key_room_2_doorways,
            'key_room_3_level_1': key_room_3_level_1_doorways,
            'key_room_3_level_2': key_room_3_level_2_doorways,
            'key_room_3': key_room_3_doorways,
            'final_boss_room': final_boss_room_doorways
        }
        self.enemies = {
            'start_room': start_room_enemies,
            'key_room_1': key_room_1_enemies,
            'key_room_2_level_1': key_room_2_level_1_enemies,
            'key_room_2_level_2': key_room_2_level_2_enemies,
            'key_room_2': key_room_2_enemies,
            'key_room_3_level_1': key_room_3_level_1_enemies,
            'key_room_3_level_2': key_room_3_level_2_enemies,
            'key_room_3': key_room_3_enemies,
            'final_boss_room': final_boss_room_enemies
         }
        self.current_map = self.maps['start_room']
        self.current_doors = self.doors['start_room']
        self.current_enemies_data = self.enemies['start_room']
        self.current_enemies = self.spawn_enemies(self.current_enemies_data)
        self.doors_list = [Door(door) for door in self.current_doors]    
    def spawn_enemies(self, enemies_data):
        return [Enemy(self.game, x, y, enemy_type, health, speed, status) for x, y, enemy_type, health, speed, status in enemies_data]
    def switch_map(self, target_room):
        self.current_enemies_data.clear()
        for enemy in self.current_enemies:
            self.current_enemies_data.append((enemy.x, enemy.y, enemy.type, enemy.health, enemy.speed, enemy.dead))
        
        self.current_map = self.maps[target_room]
        self.current_doors = self.doors[target_room]
        self.current_enemies_data = self.enemies[target_room]
        self.current_enemies = self.spawn_enemies(self.current_enemies_data)
        self.doors_list = [Door(d) for d in self.current_doors]

class Camera(pygame.sprite.Sprite):
    def __init__(self, game):
        self.game = game
        self.offset = pygame.math.Vector2()
    def custom_draw(self, sprite):
        self.offset.x = self.game.player.rect.center[0] - GAME_WIDTH // 2
        self.offset.y = self.game.player.rect.center[1] - GAME_HEIGHT // 2
        return sprite.rect.topleft - self.offset

class Enemy(pygame.sprite.Sprite):  
    def __init__(self, game, x, y, enemy_type, health, speed, status):
        super().__init__()
        self.game = game
        self.x = x
        self.y = y
        self.speed = speed
        self.health = health
        self.type = enemy_type
        self.load_animations(enemy_type)
        self.image = self.idleRight[0]
        self.mask = pygame.mask.from_surface(self.image)
        self.direction = 'right'
        self.isidle = True
        self.idleCount = 0
        self.attacking = False
        self.attackCount = 0
        self.attackCooldown = 0
        self.attacking_animation_running = False
        self.walkCount = 0
        self.rect = self.image.get_rect(topleft=(self.x, self.y))
        self.chase_range = ENEMY_CHASE_RANGE
        self.attack_range = ENEMY_ATTACK_RANGE
        self.taking_hit = False
        self.take_hit_count = 0
        self.hit_animation_complete = False
        self.knockback_speed = 0
        self.knockback_direction = pygame.math.Vector2(0, 0)
        self.dead = status
        self.death_direction = 'right'
        self.death_animation_count = 0
    def load_animations(self, enemy_type):
        self.enemy_types = {
            # idle frames, walk frames, attack frames, takehit frames, die frames
            'skeleton1' : (4, 4, 8, 5, 4),
            'skeleton2' : (8, 10, 10, 5, 13)
        }
        self.idleRight = [pygame.image.load(f'images/{enemy_type}/idleR{i}.png') for i in range(1, self.enemy_types[enemy_type][0] + 1)]
        self.idleLeft = [pygame.image.load(f'images/{enemy_type}/idleL{i}.png') for i in range(1, self.enemy_types[enemy_type][0] + 1)]
        self.walkRight = [pygame.image.load(f'images/{enemy_type}/R{i}walk.png') for i in range(1, self.enemy_types[enemy_type][1] + 1)]
        self.walkLeft = [pygame.image.load(f'images/{enemy_type}/L{i}walk.png') for i in range(1, self.enemy_types[enemy_type][1] + 1)]
        self.attackRight = [pygame.image.load(f'images/{enemy_type}/attackR{i}.png') for i in range(1, self.enemy_types[enemy_type][2] + 1)]
        self.attackLeft = [pygame.image.load(f'images/{enemy_type}/attackL{i}.png') for i in range(1, self.enemy_types[enemy_type][2] + 1)]
        self.takehitRight = [pygame.image.load(f'images/{enemy_type}/takehitR{i}.png') for i in range(1, self.enemy_types[enemy_type][3] + 1)]
        self.takehitLeft = [pygame.image.load(f'images/{enemy_type}/takehitL{i}.png') for i in range(1, self.enemy_types[enemy_type][3] + 1)]
        self.dieRight = [pygame.image.load(f'images/{enemy_type}/dieR{i}.png') for i in range(1, self.enemy_types[enemy_type][4] + 1)]
        self.dieLeft = [pygame.image.load(f'images/{enemy_type}/dieL{i}.png') for i in range(1, self.enemy_types[enemy_type][4] + 1)]
    def update(self):

        if self.health <= 0:
            self.dead = True

        if self.dead:
            self.dying()

        if not self.dead:
            for bullet in self.game.bullets:
                if pygame.sprite.collide_mask(self, bullet):
                    self.taking_hit = True
                    self.health -= BULLET_DAMAGE
                    bullet.kill()

                    knockback_vector = pygame.math.Vector2(self.rect.center) - pygame.math.Vector2(bullet.rect.center)
                    self.knockback_direction = knockback_vector.normalize()
                    self.knockback_speed = KNOCKBACK_FORCE  # Set this to a suitable value

            if self.knockback_speed > 0:
                self.apply_knockback()

            self.mask = pygame.mask.from_surface(self.image)

            if self.taking_hit:
                self.take_hit()
            elif self.in_attack_range() and self.game.player.alive:
                self.attacking = True
            elif not self.game.player.alive:
                self.idle()
                self.attacking = False
            else:
                self.attacking = False
                self.move()
            
            if not self.taking_hit:
                self.attack()
                if self.isidle:
                    self.idle()
            self.death_directon = self.direction
        
        self.game.win.blit(self.image, self.game.camera.custom_draw(self))
    def apply_knockback(self):
        self.x += self.knockback_direction.x * self.knockback_speed
        self.y += self.knockback_direction.y * self.knockback_speed
        self.rect.topleft = (self.x, self.y)

        collided_obstacles = pygame.sprite.spritecollide(self, self.game.collidables, False)

    # If a collision occurs, resolve it
        for obstacle in collided_obstacles:
            # Calculate the overlap on both axes
            overlap_x = min(self.rect.right - obstacle.rect.left, obstacle.rect.right - self.rect.left)
            overlap_y = min(self.rect.bottom - obstacle.rect.top, obstacle.rect.bottom - self.rect.top)

            # Adjust position to resolve collision
            if abs(overlap_x) < abs(overlap_y):
                if self.knockback_direction.x > 0:  # Moving right
                    self.rect.right = obstacle.rect.left
                elif self.knockback_direction.x < 0:  # Moving left
                    self.rect.left = obstacle.rect.right
            else:
                if self.knockback_direction.y > 0:  # Moving down
                    self.rect.bottom = obstacle.rect.top
                elif self.knockback_direction.y < 0:  # Moving up
                    self.rect.top = obstacle.rect.bottom

            # Update position based on rect adjustment
            self.x, self.y = self.rect.topleft

        self.knockback_speed -= KNOCKBACK_FRICTION  
        if self.knockback_speed < 0:
            self.knockback_speed = 0
    def move(self):
        if self.player_in_chase_range() and self.has_line_of_sight():
            self.isidle = False
            self.idleCount = 0
            direction_vector = pygame.math.Vector2(
                self.game.player.rect.centerx - self.rect.centerx, 
                self.game.player.rect.centery - self.rect.centery
            )
            if direction_vector.length() > 0:
                direction_vector = direction_vector.normalize() * self.speed
                self.x += direction_vector.x
                self.y += direction_vector.y
                self.rect.topleft = (self.x, self.y)

                angle = math.atan2(direction_vector.y, direction_vector.x)

                angle_degrees = (math.degrees(angle) + 360) % 360

                if 90 < angle_degrees < 270:  # Facing left
                    self.direction = 'left'
                else:  # Facing right
                    self.direction = 'right'
        else:
            self.isidle = True      

        if self.walkCount + 1 >= self.enemy_types[self.type][1]*5:
            self.walkCount = 0
        
        if self.direction == 'right':
            self.image = self.walkRight[self.walkCount // 5]
            self.walkCount += 1
        if self.direction == 'left':
            self.image = self.walkLeft[self.walkCount // 5]
            self.walkCount += 1
    def take_hit(self):
        self.take_hit_count += 1
        if self.direction == 'right':
            self.image = self.takehitRight[self.take_hit_count // 5]
        elif self.direction == 'left':
            self.image = self.takehitLeft[self.take_hit_count // 5]

        if self.take_hit_count + 1 >= self.enemy_types[self.type][3] * 5:
            self.take_hit_count = 0
            self.taking_hit = False
            self.hit_animation_complete = True
    def idle(self):
        if self.idleCount + 1 >= self.enemy_types[self.type][0]*5:
            self.idleCount = 0

        if self.direction == 'right':
            self.image = self.idleRight[self.idleCount // 5]
            self.idleCount += 1
        elif self.direction == 'left':
            self.image = self.idleLeft[self.idleCount // 5]
            self.idleCount += 1
    def has_line_of_sight(self):
        player_position = self.game.player.rect.center
        enemy_position = self.rect.center

        # Apply the camera offset to both positions
        offset_player_position = player_position - self.game.camera.offset
        offset_enemy_position = enemy_position - self.game.camera.offset

        #line = pygame.draw.line(self.game.win, (255, 0, 0), offset_enemy_position, offset_player_position, 1) 
        # /\ Unhash this to visualize enemy field of view

        obstacles = self.game.collidables.sprites()
        for obstacle in obstacles:
            if obstacle.rect.clipline(enemy_position, player_position):
                return False
        return True
    def in_attack_range(self):
        distance_to_player = math.sqrt((self.game.player.rect.centerx - self.rect.centerx) ** 2 + 
                                    (self.game.player.rect.centery - self.rect.centery) ** 2)
        
        angle_to_player = math.atan2(self.game.player.rect.centery - self.rect.centery,
                                    self.game.player.rect.centerx - self.rect.centerx)
        
        angle_degrees = (math.degrees(angle_to_player) + 360) % 360
        
        within_angle_range = 90 <= angle_degrees <= 270  # Prevent attacks from above, allow from below
        
        return distance_to_player <= self.attack_range and within_angle_range
    def player_in_chase_range(self):
        distance_to_player = math.sqrt((self.game.player.rect.centerx - self.rect.centerx) ** 2 + 
                                    (self.game.player.rect.centery - self.rect.centery) ** 2)
        return distance_to_player <= self.chase_range
    def attack(self):
        if self.attackCooldown > 0:
            self.attackCooldown -= 1

        if self.attackCooldown == 0:
            self.attackCooldown = 40

        if self.attacking:
            self.attacking_animation_running = True

        if self.attacking_animation_running:
            self.attackCount += 1
            if self.direction == 'right':
                self.image = self.attackRight[self.attackCount // 3]
            elif self.direction == 'left':
                self.image = self.attackLeft[self.attackCount // 3]

            if self.attackCount + 1 >= self.enemy_types[self.type][2]*3:  # Finish the attack animation
                self.attackCount = 0
                self.attacking_animation_running = False  # Attack is complete
    def dying(self):
        self.death_animation_count += 1

        if self.death_animation_count + 1 >= self.enemy_types[self.type][4]*5:
            self.death_animation_count = self.enemy_types[self.type][4]*5 - 1
            self.kill()

        if self.death_direction == 'right':
            self.image = self.dieRight[self.death_animation_count // 5]
        elif self.death_direction == 'left':
            self.image = self.dieLeft[self.death_animation_count // 5]

class Player(pygame.sprite.Sprite):
    walkRight = [pygame.image.load(f'images/player/R{i}.png') for i in range(1, 9)]
    walkLeft = [pygame.image.load(f'images/player/L{i}.png') for i in range(1, 9)]
    Bracing_Right = [pygame.image.load('images/player/BracingR1.png'),  pygame.image.load('images/player/BracingR2.png')]
    Bracing_Left = [pygame.image.load('images/player/BracingL1.png'),  pygame.image.load('images/player/BracingL2.png')]
    dieRight = [pygame.image.load(f'images/player/dieR{i}.png') for i in range(1, 9)]
    dieLeft = [pygame.image.load(f'images/player/dieL{i}.png') for i in range(1, 9)]
    def __init__(self, game, dungeon_map):
        super().__init__()
        self.game = game
        self.x = PLAYER_START_X
        self.y = PLAYER_START_Y
        self.speed = PLAYER_SPEED
        self.walkCount = 0
        self.shotCount = 0
        self.bracing = False
        self.dungeon_map = dungeon_map

        self.image = self.walkRight[0]
        self.weapon_last_direction = 'right'
        self.rect = self.image.get_rect(topleft=(self.x, self.y))
        self.mask = pygame.mask.from_surface(self.image)
        self.alive = True
        self.death_direction = 'right'
        self.death_animation_count = 0
    def check_collision(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy
        
        collided_tile = pygame.sprite.spritecollideany(self, self.game.collidables)

        if collided_tile:
            if dx > 0:
                self.rect.right = collided_tile.rect.left
            if dx < 0:
                self.rect.left = collided_tile.rect.right
            if dy > 0:
                self.rect.bottom = collided_tile.rect.top
            if dy < 0:
                self.rect.top = collided_tile.rect.bottom
            
            self.x, self.y = self.rect.topleft
            return 
        self.x, self.y = self.rect.topleft
    def check_doors(self, dungeon_map):
        for door in dungeon_map.doors_list:
            if self.rect.colliderect(door.rect):
                dungeon_map.switch_map(door.target_room)

                target_door = dungeon_map.doors_list[door.target_doorway - 1]
                if target_door.spawn_direction == 'right':
                    self.rect.midleft = target_door.rect.midright
                elif target_door.spawn_direction == 'left':
                    self.rect.midright = target_door.rect.midleft
                elif target_door.spawn_direction == 'down':
                    self.rect.midtop = target_door.rect.midbottom
                elif target_door.spawn_direction == 'up':
                    self.rect.midbottom = target_door.rect.midtop
                self.x, self.y = self.rect.topleft
                self.game.tiles.clear()
                self.game.draw_map(dungeon_map.current_map)
                break
    def move(self):
        if not self.alive:
            return

        self.velocity_x = 0
        self.velocity_y = 0

        if self.game.keys[pygame.K_a]:
            self.velocity_x -= self.speed
        if self.game.keys[pygame.K_d]:
            self.velocity_x += self.speed
        if self.game.keys[pygame.K_w]:
            self.velocity_y -= self.speed
        if self.game.keys[pygame.K_s]:
            self.velocity_y += self.speed

        if self.velocity_x != 0 and self.velocity_y != 0:
            self.velocity_y /= math.sqrt(2)
            self.velocity_x /= math.sqrt(2)
        
        self.handle_bracing()

        self.check_doors(self.dungeon_map)
        self.check_collision(self.velocity_x, 0)
        self.check_collision(0, self.velocity_y)

        self.check_death()
    def handle_bracing(self):
        if self.game.weapon.is_shooting and self.game.weapon.cooldown == 0:
            self.bracing = True
        
        if self.bracing:
            self.velocity_x, self.velocity_y = 0, 0
            self.shotCount += 1

            # Strong initial recoil with faster decay
            initial_recoil_force = 15  # Adjust the initial recoil strength
            decay_rate = 0.8  # Faster decay rate

            recoil_force = initial_recoil_force * (decay_rate ** self.shotCount)
            
            if self.shotCount >= 60:  # End bracing after 24 frames for quicker decay
                self.shotCount = 0
                self.bracing = False
                recoil_force = 0

            angle = math.radians(self.game.weapon.angle) 

            recoil_x = math.cos(angle) * recoil_force
            recoil_y = math.sin(angle) * recoil_force

            if self.weapon_last_direction == 'right':
                self.image = self.Bracing_Right[self.shotCount // 30]
                self.velocity_x -= recoil_x
                self.velocity_y -= recoil_y
            else:
                self.image = self.Bracing_Left[self.shotCount // 30]
                self.velocity_x -= recoil_x
                self.velocity_y -= recoil_y      
    def draw(self):
        if self.alive:
            self.move()
            self.rect.topleft = (self.x, self.y)
            if self.bracing:
                self.game.win.blit(self.image, self.game.camera.custom_draw(self))
                return
            
            if not (self.game.keys[pygame.K_a] or self.game.keys[pygame.K_d] or self.game.keys[pygame.K_w] or self.game.keys[pygame.K_s]):
                self.walkCount = 0

            if self.walkCount + 1 >= 24:
                self.walkCount = 0
            
            if self.weapon_last_direction == 'right':
                self.image = self.walkRight[self.walkCount // 3]
                self.walkCount += 1
            elif self.weapon_last_direction == 'left':
                self.image = self.walkLeft[self.walkCount // 3]
                self.walkCount += 1
            self.death_direction = self.weapon_last_direction
        else:
            self.play_death_animation()

        self.game.win.blit(self.image, self.game.camera.custom_draw(self))
    def check_death(self):
        for enemy in self.dungeon_map.current_enemies:
            if enemy.attacking and pygame.sprite.collide_mask(self, enemy):
                self.alive = False
    def play_death_animation(self):
        self.death_animation_count += 1

        if self.death_animation_count + 1 >= 40:
            self.death_animation_count = 39

        if self.death_direction == 'right':
            self.image = self.dieRight[self.death_animation_count // 5]
        elif self.death_direction == 'left':
            self.image = self.dieLeft[self.death_animation_count // 5]

class Weapon(pygame.sprite.Sprite):
    shootAnimation = [pygame.image.load(f'images/shotgun/shotgun{i}.png') for i in range(14)]
    def __init__(self, game, player):
        super().__init__()
        self.game = game
        self.player = player
        self.camera = self.game.camera
        self.image = pygame.image.load('images/shotgun/shotgun0.png')
        self.current_image = self.image
        self.rect = self.image.get_rect()
        self.width = self.rect.width
        self.height = self.rect.height
        self.gun_offset = 30
        self.is_shooting = False
        self.animation_running = False        
        self.shotCount = 0
        self.angle = None
        self.cooldown = 0
    def draw(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        dx = mouse_x - (self.rect.center[0] - self.camera.offset.x)
        dy = mouse_y - (self.rect.center[1] - self.camera.offset.y)
        self.angle = math.degrees(math.atan2(dy, dx))
        self.shoot()

        # Flip horizontally if the angle is on the left side
        if not (-90 <= self.angle <= 90):
            self.image = pygame.transform.flip(self.current_image, False, True)
            self.player.weapon_last_direction = 'left'
        else:
            self.image = self.current_image
            self.player.weapon_last_direction = 'right'
        
        self.image, self.rect = self.rotate_image(self.image, self.angle)

        offset_x = math.cos(math.radians(self.angle)) * self.gun_offset
        offset_y = math.sin(math.radians(self.angle)) * self.gun_offset + 8
        
        # Center the new rect with the calculated offsets
        self.rect.center = (
            self.player.rect.center[0] + offset_x, 
            self.player.rect.center[1] + offset_y
        )
        
        self.gun_end_x = self.rect.center[0]
        self.gun_end_y = self.rect.center[1]

        if self.player.alive:
            self.game.win.blit(self.image, self.camera.custom_draw(self))
    def rotate_image(self, image, angle):
        rotated_image = pygame.transform.rotate(image, -angle)
        new_rect = rotated_image.get_rect(center=image.get_rect(center=(0, 0)).center)
        return rotated_image, new_rect    
    def shoot(self):
        if self.is_shooting and self.cooldown == 0:
            self.animation_running = True

        if self.animation_running:
            self.shotCount += 1
            self.current_image = self.shootAnimation[self.shotCount // 3]
            if self.shotCount + 1 >= 42:
                self.shotCount = 0
                self.cooldown = SHOOTING_COOLDOWN
                self.animation_running = False
        else:
            if self.cooldown != 0:
                self.cooldown -= 1

class Projectile(pygame.sprite.Sprite):
    def __init__(self, game, camera, x, y, angle):
        super().__init__()
        self.game = game
        self.camera = camera
        self.radius = BULLET_SIZE
        self.color = (128, 128, 128)
        self.angle = angle
        self.velocity = BULLET_SPEED
        self.dx = self.velocity * math.cos(math.radians(self.angle))
        self.dy = self.velocity * math.sin(math.radians(self.angle))
        self.image = pygame.Surface((2 * self.radius, 2 * self.radius), pygame.SRCALPHA)
        # Draw a circle on the surface
        pygame.draw.circle(self.image, self.color, (self.radius, self.radius), self.radius)
        # Generate the rect and mask
        self.rect = self.image.get_rect(center=(x, y))
        self.mask = pygame.mask.from_surface(self.image)
    def move(self):
        self.rect.center = (self.rect.center[0] + self.dx, self.rect.center[1] + self.dy)
                
        self.mask = pygame.mask.from_surface(self.image)

        for obstacle in self.game.collidables:
            if pygame.sprite.collide_rect(self, obstacle):
                self.kill()
                return
        if not (0 < self.rect.center[0] - self.camera.offset.x < GAME_WIDTH and 
                0 < self.rect.center[1] - self.camera.offset.y < GAME_HEIGHT):
            self.kill()
            return
    def draw(self):
        self.move()
        pygame.draw.circle(self.game.win, self.color, self.camera.custom_draw(self), self.radius)

class Tile(pygame.sprite.Sprite):
    def __init__(self, x, y, tile_type, tile_images, camera):
        super().__init__()
        self.x = x
        self.y = y
        self.tile_type = tile_type
        self.image = tile_images.get(tile_type, None)
        self.rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        self.camera = camera
    def draw(self, win):
        if self.image:
            win.blit(self.image, self.camera.custom_draw(self))

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Game Name") # ADD A GAME NAME
        self.win = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))
        self.clock = pygame.time.Clock()
        self.map = DungeonMap(self)
        self.camera = Camera(self)
        self.player = Player(self, self.map)
        self.weapon = Weapon(self, self.player)
        self.bullets = pygame.sprite.Group()
        self.keys = []
        self.collidables = pygame.sprite.Group()
        self.ground_img = pygame.image.load('images/blocks/Ground.png').convert()
        self.wall_img = pygame.image.load('images/blocks/Wall.png').convert()
        self.tile_images = {
            0: None,
            1: self.ground_img,
            2: self.wall_img
        }
        self.tiles = []
        self.draw_map(self.map.current_map)
    def draw_map(self, map):
        self.tiles = []
        self.collidables.empty()
        for y, row in enumerate(map):
            for x, tile_type in enumerate(row):
                tile = Tile(x, y, tile_type, self.tile_images, self.camera)
                self.tiles.append(tile)
                if tile.tile_type == 2:
                    self.collidables.add(tile)
    def redrawGameWindow(self):
        self.win.fill((0, 0, 0))
        for tile in self.tiles:
            tile.draw(self.win)
        for door in self.map.doors_list:
            door.draw(self.win, self.camera)
        self.player.draw()
        for enemy in self.map.current_enemies:
            enemy.update()
        self.weapon.draw()

        self.bullets.update()
        for bullet in self.bullets:
            bullet.draw()

        pygame.display.update()
    def main(self):
        running = True
        while running:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    for bullet in self.bullets:
                        print(bullet, bullet.rect.x, bullet.rect.y)
            self.keys = pygame.key.get_pressed()
            mouse_buttons = pygame.mouse.get_pressed()
            mouse_x, mouse_y = pygame.mouse.get_pos()

            #Shotting projectile
            if mouse_buttons[0] and self.player.alive and self.weapon.shotCount == 0 and self.weapon.cooldown == 0:
                self.weapon.is_shooting = True
                dx = mouse_x - (self.weapon.rect.center[0] - self.camera.offset.x)
                dy = mouse_y - (self.weapon.rect.center[1] - self.camera.offset.y)
                angle = math.degrees(math.atan2(dy, dx))
                self.bullets.add(Projectile(self, self.camera, round(self.weapon.gun_end_x), round(self.weapon.gun_end_y), angle)) 
                self.bullets.add(Projectile(self, self.camera, round(self.weapon.gun_end_x), round(self.weapon.gun_end_y), angle + 18)) 
                self.bullets.add(Projectile(self, self.camera, round(self.weapon.gun_end_x), round(self.weapon.gun_end_y), angle - 18)) 
            else:
                self.weapon.is_shooting = False

            self.redrawGameWindow()

        pygame.quit()

if __name__ == "__main__":
    Game().main()