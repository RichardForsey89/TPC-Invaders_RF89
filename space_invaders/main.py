from ast import Global
from ctypes import sizeof
import random
import pygame
import pygame.font
import time


WIDTH, HEIGHT = 480, 740
SCALE = 1.5
SCALE_WIDTH, SCALE_HEIGHT = WIDTH * SCALE, HEIGHT * SCALE
FPS = 60

pygame.font.init()
GAME_FONT = pygame.font.SysFont('couriernew', 30)

# Game Over Flag
GAME_OVER = False

player_score = 0
difficulty = 1
current_health = 0

# Sprite Collision Groups
bullet_group = pygame.sprite.Group()
alien_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()


#create spaceship class
class Spaceship(pygame.sprite.Sprite):
  def __init__(self, x, y, health):
    pygame.sprite.Sprite.__init__(self)
    self.load_sprites()
    self.image = self.player_sprite_n
    self.rect = self.image.get_rect()
    self.rect.center = [x, y]
    self.last_shot = pygame.time.get_ticks()

    global current_health
    current_health = health

    # Shooting Sound
    self.shoot_sound = pygame.mixer.Sound('sounds/laser_shot.wav')

  def load_sprites(self):
    #Load the sprite sheet
    self.sprites = pygame.image.load("sprites/Player_ship (16 x 16).png").convert_alpha()
    #Get the individual sprites
    self.player_sprite_n = self.sprites.subsurface((16, 0,16,16))
    self.player_sprite_r = self.sprites.subsurface((32,0,16,16))
    self.player_sprite_l = self.sprites.subsurface((0,0,16,16))
      #scale the sprites
    self.player_sprite_n = pygame.transform.scale(self.player_sprite_n, (32, 32))
    self.player_sprite_r = pygame.transform.scale(self.player_sprite_r, (32, 32))
    self.player_sprite_l = pygame.transform.scale(self.player_sprite_l, (32, 32))

  # Call every game update
  def update(self, dt, time_now):
    #set movement speed
    speed = 250
    #set a cooldown variable
    cooldown = 500 / difficulty #milliseconds
    dx = 0

    #get key press for movement
    key = pygame.key.get_pressed()
    if key[pygame.K_LEFT] and self.rect.left > 0:
      dx = -1 #Set the direction delta
      self.image = self.player_sprite_l # Set the Sprite
    elif key[pygame.K_RIGHT] and self.rect.right < WIDTH:
      dx = 1 #Set the direction delta
      self.image = self.player_sprite_r # Set the Sprite
    else:
      dx = 0 #Set the direction delta
      self.image = self.player_sprite_n # Set the Sprite

    # On Space press create bullet at position
    if key[pygame.K_SPACE] and time_now - self.last_shot > cooldown:
      #Add Bullet to sprite group 
      bullet = Bullet(self.rect.centerx, self.rect.top)
      bulletR = Scatter_Bullet(self.rect.centerx, self.rect.top, 10)
      bulletL = Scatter_Bullet(self.rect.centerx, self.rect.top, -10)
      bullet_group.add(bullet)
      bullet_group.add(bulletR)
      bullet_group.add(bulletL)

      # Play laser shot sound
      self.shoot_sound.play()
      self.last_shot = time_now

    if key[pygame.K_b] and time_now - self.last_shot > cooldown:

      #Add torp to sprite group 
      torp = Torp(self.rect.centerx, self.rect.top)

      bullet_group.add(torp)


      # Play laser shot sound
      self.shoot_sound.play()
      self.last_shot = time_now

    # Move the ship
    self.rect.x += dx * speed * dt

class Big_Explosion(pygame.sprite.Sprite):
  def __init__(self, x, y):
    pygame.sprite.Sprite.__init__(self)
    self.load_sprite()
    self.rect = self.image.get_rect()
    self.rect.center = [x,y]
    self.dir = dir
    self.timer = 0
    self.sound = pygame.mixer.Sound('sounds/torp_explosion.wav')

    # explosion sound
    self.sound.play()

  def load_sprite(self):
    self.image_sheet = pygame.image.load("sprites/big_boom (128 x 128).png").convert_alpha()
    self.dir = 1
    self.sprites = []

    pixels = 128
    rows = 7
    cols = 6
    for r in range(rows):
      for c in range(cols):
        self.sprites.append(self.image_sheet.subsurface((128*c,128*r,128,128)))

    for i in range(len(self.sprites)):
      self.sprites[i] = pygame.transform.scale(self.sprites[i], (256,256))

    self.image = self.sprites[0]
    self.image_index = 0

  def update(self, dt, time_now):
    if time_now - self.timer >= 10:
      self.image_index += 1
      if self.image_index == 1:
        oofd = pygame.sprite.spritecollide(self, alien_group, False)
        for alien in oofd:
          # explosion = Explosion(alien.rect.centerx, alien.rect.centery)
          # explosion_group.add(explosion)

          # Need to make a "quiet explosion"
          
          alien.kill()
        
      if self.image_index >= len(self.sprites):
        self.kill()
      else:
        self.image = self.sprites[self.image_index]
        self.timer = time_now

class Explosion(pygame.sprite.Sprite):
  def __init__(self, x, y):
    pygame.sprite.Sprite.__init__(self)
    self.load_sprite()
    self.rect = self.image.get_rect()
    self.rect.center = [x,y]
    self.dir = dir
    self.timer = 0
    self.sound = pygame.mixer.Sound('sounds/bomb.wav')

    # explosion sound
    self.sound.play()

  def load_sprite(self):
    self.image_sheet = pygame.image.load("sprites/explosion_pixelfied (16 x 16).png").convert_alpha()
    self.dir = 1
    self.sprites = []
    self.sprites.append(self.image_sheet.subsurface((0,0,16,16)))
    self.sprites.append(self.image_sheet.subsurface((16,0,16,16)))
    self.sprites.append(self.image_sheet.subsurface((32,0,16,16)))
    self.sprites.append(self.image_sheet.subsurface((48,0,16,16)))

    self.sprites.append(self.image_sheet.subsurface((0,16,16,16)))
    self.sprites.append(self.image_sheet.subsurface((16,16,16,16)))
    self.sprites.append(self.image_sheet.subsurface((32,16,16,16)))
    self.sprites.append(self.image_sheet.subsurface((48,16,16,16)))

    self.sprites.append(self.image_sheet.subsurface((0,32,16,16)))
    self.sprites.append(self.image_sheet.subsurface((16,32,16,16)))
    self.sprites.append(self.image_sheet.subsurface((32,32,16,16)))
    self.sprites.append(self.image_sheet.subsurface((48,32,16,16)))

    self.sprites.append(self.image_sheet.subsurface((0,48,16,16)))
    self.sprites.append(self.image_sheet.subsurface((16,48,16,16)))
    self.sprites.append(self.image_sheet.subsurface((32,48,16,16)))
    self.sprites.append(self.image_sheet.subsurface((48,48,16,16)))

    for i in range(len(self.sprites)):
      self.sprites[i] = pygame.transform.scale(self.sprites[i], (32,32))

    self.image = self.sprites[0]
    self.image_index = 0

  def update(self, dt, time_now):
    if time_now - self.timer >= 20:
      self.image_index += 1
      if self.image_index >= len(self.sprites):
        self.kill()
      else:
        self.image = self.sprites[self.image_index]
        self.timer = time_now

class Alien(pygame.sprite.Sprite):
  def __init__(self, x, y, dir=1, speed=5):
    pygame.sprite.Sprite.__init__(self)
    self.load_sprite()
    self.rect = self.image.get_rect()
    self.rect.center = [x,y]
    self.speed = speed
    self.dir = dir
    self.timer = 0
    self.sound = pygame.mixer.Sound('sounds/alien_shot.wav')
    self.hp = difficulty

  def damage(self):
    self.hp -= 1

  def load_sprite(self):
    self.image_sheet = pygame.image.load("sprites/Alan (16 x 16).png").convert_alpha()
    self.dir = 1
    self.sprites = []
    self.sprites.append(self.image_sheet.subsurface((48,0,16,16)))
    self.sprites.append(self.image_sheet.subsurface((64,0,16,16)))
    self.sprites.append(self.image_sheet.subsurface((80,0,16,16)))

    for i in range(len(self.sprites)):
      self.sprites[i] = pygame.transform.scale(self.sprites[i], (32,32))

    self.image = self.sprites[0]
    self.image_index = 0

  def update(self, dt, time_now):

    if time_now - self.timer >= 300:
      self.image_index += 1
      if self.image_index >= len(self.sprites):
        self.image_index = 0
      #print("SPRITE CAHNGE")
      if random.random() < 0.005 * difficulty:
        bullet_group.add(Alien_Bullet(self.rect.centerx, self.rect.bottom))
        self.sound.play()
      self.image = self.sprites[self.image_index]
      self.timer = time_now 

class Torp(pygame.sprite.Sprite):
  def __init__(self, x, y):
    pygame.sprite.Sprite.__init__(self)
    self.image = pygame.image.load('sprites/torp.png')
    self.rect = self.image.get_rect()
    self.rect.center = [x,y]
    self.speed = 250

  def update(self, dt, time_now):
    self.rect.y -= self.speed * dt

    if self.rect.y <= -5:
      self.kill()
    if pygame.sprite.spritecollide(self, alien_group, False):
      blast = Big_Explosion(self.rect.centerx, self.rect.centery)
      explosion_group.add(blast)
      self.kill()
      print("TORPEDO")

      global player_score
      player_score += 10000


class Bullet(pygame.sprite.Sprite):
  def __init__(self, x, y):
    pygame.sprite.Sprite.__init__(self)
    self.image = pygame.image.load('sprites/Player_beam (16 x 16).png')
    self.image = pygame.transform.scale(self.image, (32,32))
    self.rect = self.image.get_rect()
    self.rect.center = [x,y]
    self.speed = 500

  def update(self, dt, time_now):
    self.rect.y -= self.speed * dt

    if self.rect.y <= -5:
      self.kill()
    if pygame.sprite.spritecollide(self, alien_group, False):

      test = pygame.sprite.spritecollide(self, alien_group, False)
      target = test[0]
      target.damage()
      if target.hp < 1:
        explosion = Explosion(target.rect.centerx, target.rect.centery)
        explosion_group.add(explosion)
        target.kill()

      global player_score
      player_score += 100
      self.kill()
      print("HIT")

class Scatter_Bullet(Bullet):
  def __init__(self, x, y, scatter):
    self.scatter = scatter
    super().__init__(x, y)

  def update(self, dt, time_now):
    self.rect.y -= self.speed * dt

    # I don't know why, but for right vs left there needs to be different multipliers.
    if self.scatter > 0:
      #right
      self.rect.x += self.scatter * 10 * dt
    else:
      #left
      self.rect.x += self.scatter * 2 * dt

    if self.rect.y <= -5:
      self.kill()
    if pygame.sprite.spritecollide(self, alien_group, False):

      test = pygame.sprite.spritecollide(self, alien_group, False)
      target = test[0]
      target.damage()
      if target.hp < 1:
        explosion = Explosion(target.rect.centerx, target.rect.centery)
        explosion_group.add(explosion)
        target.kill()

      global player_score
      player_score += 100
      self.kill()
      print("HIT")

class Alien_Bullet(pygame.sprite.Sprite):
  def __init__(self, x, y):
    pygame.sprite.Sprite.__init__(self)
    self.load_sprite()
    self.image = pygame.transform.scale(self.image, (32, 32))
    self.rect = self.image.get_rect()
    self.rect.center = [x,y]
    self.speed = 500

  def load_sprite(self):
    sprite_sheet = pygame.image.load('sprites/Enemy_projectile (16 x 16).png')
    self.image = sprite_sheet;
  def update(self, dt, time_now):
    self.rect.y += self.speed * dt

    if self.rect.y >= HEIGHT:
      self.kill()
    if pygame.sprite.spritecollide(self, player_group, False):
      self.kill()
      global current_health
      current_health -= 1

      if current_health < 1:
         player = player_group.sprites()
         player[0].kill()
         global GAME_OVER
         GAME_OVER = True

   
  
class Level():

  def __init__(self):
    self.background = pygame.image.load("sprites/Space_BG (2 frames) (64 x 64).png").convert_alpha()
    background_a = self.background.subsurface((0,0, 64, 64))
    background_b = self.background.subsurface((64,0, 64, 64))
    self.background_a = self.create_surface(background_a, background_b)
    self.background_b = self.create_surface(background_b, background_a)
    self.timer = 0
    
  def create_aliens(self,rows, cols, alien_group):
    for row in range(rows):
      for item in range(cols):
        alien = Alien(80 + item * 64, 100 + row * 64)
        alien_group.add(alien)
    return alien_group

  def create_surface(self, a, b):
    self.surface = pygame.Surface((WIDTH,HEIGHT))
    for y in range(0, int(HEIGHT/64) + 64):
      for x in range(0, int(WIDTH/64) + 64):
        if x * y % 2 == 0:
          self.surface.blit(pygame.transform.rotate(a, 90 * x), (x * 64, y*64))
        else:
          self.surface.blit(pygame.transform.rotate(b, 90 * x), (x * 64, y*64))

    self.surface.blit(self.background, (0,0))
    return self.surface
  
  def get_surface(self):
    return (self.background_a, (0,0))
  
  def on_loop(self, time_now):
    #print(time_now - self.timer)
    if time_now - self.timer > 1500:
      self.timer = time_now
      self.background_a, self.background_b = self.background_b, self.background_a

# Main Application class
class App():

  # Initialize varibles for Application Class
  def __init__(self):
    # Clock for FPS limiting
    self.clock = pygame.time.Clock()
    # Time for delta time
    self.dt = 0
    self.prev_time = time.time()
    GAME_OVER = False
    # Pygame varibles
    self.running = True
    self._display_surf = None
    self.size = self.weight, self.height = SCALE_WIDTH, SCALE_HEIGHT


  def on_init(self):
    #Pygame Surface initialisation
    pygame.init()
    self._display_surf = pygame.display.set_mode(self.size, pygame.HWSURFACE)
    self._running = True

    self.level = Level()

    #Initialise groups
    self.spaceship = Spaceship(int(WIDTH / 2), HEIGHT - 100, 3)
    
    
    
    self.player_group = player_group
    self.player_group.add(self.spaceship)

    self.bullet_group = bullet_group
    self.alien_group = alien_group
    self.explosion_group = explosion_group

    self.alien_group = self.level.create_aliens(6,6,self.alien_group)
  # Handle events
  def on_event(self, event):
    if event.type == pygame.QUIT:
      self._running = False


  def on_loop(self):
    global GAME_OVER
    self.clock.tick(FPS)
    # print(self.clock.get_fps())
    self.now = time.time()
    self.dt = self.now - self.prev_time
    self.prev_time = self.now
    time_now = pygame.time.get_ticks();
    
    ## GAME LOGIC GOES HERE
    self.level.on_loop(time_now)
    if GAME_OVER == False:
      self.spaceship.update(self.dt, time_now)
    else:
      if pygame.key.get_pressed()[pygame.K_SPACE]:
        self.on_reset()

    self.bullet_group.update(self.dt, time_now)
    self.alien_group.update(self.dt, time_now)
    self.explosion_group.update(self.dt, time_now)

    if len(alien_group) == 0:
      self.on_continue()


  # blit render layers to screen surface
  def on_render(self):
    temp_buffer = pygame.Surface((WIDTH, HEIGHT))
    temp_buffer.blit(*self.level.get_surface())

    string = "Score: {0}".format(player_score)
    score_text = GAME_FONT.render(string,True,(255,255,255))

    string = "Difficulty: {0}".format(difficulty)
    difficulty_text = GAME_FONT.render(string,True,(255,255,255))

    string = "Health: {0}".format(current_health)
    health_text = GAME_FONT.render(string,True,(255,255,255))

    
    self.player_group.draw(temp_buffer)
    self.bullet_group.draw(temp_buffer)
    self.alien_group.draw(temp_buffer)

    self.explosion_group.draw(temp_buffer)

    temp_buffer = pygame.transform.scale(temp_buffer, (SCALE_WIDTH, SCALE_HEIGHT))
    self._display_surf.blit(temp_buffer, (0,0))

    self._display_surf.blit(score_text, (0,0))
    self._display_surf.blit(difficulty_text, (400,0))
    self._display_surf.blit(health_text, (0,30))

    #update display
    pygame.display.update()

  def on_continue(self):

    global difficulty
    global current_health
    difficulty += 1
    if current_health < 3:
      current_health += 1

    self.alien_group = self.level.create_aliens(6,6,self.alien_group)

  def on_reset(self):
    self.bullet_group.empty()
    self.player_group.empty()
    self.alien_group.empty()
    self.explosion_group.empty()

    global GAME_OVER
    GAME_OVER = False

    global player_score
    player_score = 0

    global difficulty
    difficulty = 1

    global current_health
    current_health = 3

    self.on_init()
  def on_cleanup(self):
    pygame.quit()

  def on_execute(self):
    if self.on_init() == False:
      self._running = False
    self.music = pygame.mixer.Sound('sounds/music.wav')
    self.music.play()

    while ( self._running ):
      for event in pygame.event.get():
        self.on_event(event)

      self.on_loop()
      self.on_render()
    self.on_cleanup()


if __name__ == "__main__":
  app = App()
  app.on_execute()