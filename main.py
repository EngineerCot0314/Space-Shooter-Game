import pygame,asyncio

from random import randint,uniform

class Player(pygame.sprite.Sprite):
    def __init__(self,groups):
        super().__init__(groups)
        self.image = pygame.image.load("images/player.png").convert_alpha()
        self.rect = self.image.get_frect(center = (window_width / 2,window_height / 2))
        self.direction = pygame.math.Vector2()
        self.speed = 300
        
        #cooldown for laser
        self.can_shoot = True
        self.laser_shoot_time = 0
        self.cooldown_duration = 400

        

    def laser_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.laser_shoot_time >= self.cooldown_duration:
                self.can_shoot = True

    def update(self, dt):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_RIGHT] or keys[pygame.K_d]) - int(keys[pygame.K_LEFT] or keys[pygame.K_a])
        self.direction.y = int(keys[pygame.K_DOWN] or keys[pygame.K_s]) - int(keys[pygame.K_UP] or keys[pygame.K_w])
        self.direction = self.direction.normalize() if self.direction else self.direction
        self.rect.center += self.direction * self.speed * dt
        self.laser_timer()

class Star(pygame.sprite.Sprite):
    def __init__(self,groups,surf):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(center = (randint(0,window_width),randint(0,window_height)))

class Laser(pygame.sprite.Sprite):
    def __init__(self,surf,pos,groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(midbottom = pos)

    def update(self,dt):
            self.rect.centery -= 400 * dt
            if self.rect.bottom < 0:
                self.kill()

class Meteor(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.original_surf = surf
        self.image = surf
        self.rect = self.image.get_frect(center = pos)
        self.start_time = pygame.time.get_ticks()
        self.lifetime = 3000
        self.direction = pygame.Vector2(uniform(-0.5,0.5),1)
        self.speed = randint(400,500)
        self.rotation_speed = randint(40,80)
        self.rotation = 0

    def update(self,dt):
        self.rect.center += self.direction * self.speed * dt
        if pygame.time.get_ticks() - self.start_time >= self.lifetime:
            self.kill()
        self.rotation += self.rotation * dt
        self.image = pygame.transform.rotozoom(self.original_surf,self.rotation,1)
        self.rect = self.image.get_frect(center = self.rect.center)

class AnimatedExplosion(pygame.sprite.Sprite):
    def __init__(self,frames,pos,groups):
        super().__init__(groups)
        self.frames = frames
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_frect(center = pos)
        explosion_sound.play()
    def update(self,dt):
        self.frame_index += 20 * dt
        if self.frame_index < len(self.frames):
            self.image = self.frames[int(self.frame_index)]
        else:
            self.kill()

def colisions():
    global running

    colision_sprites = pygame.sprite.spritecollide(player, meteor_sprites,True,pygame.sprite.collide_mask)
    if colision_sprites:
        running = False

    for laser in laser_sprites:
        collided_sprites = pygame.sprite.spritecollide(laser, meteor_sprites,True)
        if collided_sprites:
            laser.kill()
            AnimatedExplosion(explosion_frames,laser.rect.midtop,all_sprites)
           
def display_score():
    current_time = pygame.time.get_ticks() //100
    text_surf = font.render(str(current_time),True,(240,240,240))
    text_rect = text_surf.get_frect(midbottom = (window_width/2, window_height - 50))
    display_surf.blit(text_surf,text_rect)
    pygame.draw.rect(display_surf,(240,240,240), text_rect.inflate(20,10).move(0,-8),5,10)

#general setup
pygame.init()
window_width,window_height = 1280,720
display_surf = pygame.display.set_mode((window_width,window_height))
pygame.display.set_caption("Space Shooter")
running = True
clock = pygame.time.Clock()

#imports
star_surf = pygame.image.load("images/star.png").convert_alpha()
meteor_surf = pygame.image.load("images/meteor.png").convert_alpha()
laser_surf = pygame.image.load("images/laser.png").convert_alpha()
font = pygame.font.Font("images/Oxanium-Bold.ttf",40)
explosion_frames = [pygame.image.load(f"images/explosion/{i}.png").convert_alpha() for i in range(21)]

laser_sound = pygame.mixer.Sound("audio/laser.ogg")
laser_sound.set_volume(0.2)
explosion_sound = pygame.mixer.Sound("audio/explosion.ogg")
explosion_sound.set_volume(0.2)
game_music = pygame.mixer.Sound("audio/game_music.ogg")
game_music.set_volume(0.3)
game_music.play(loops= -1)

#sprites
all_sprites = pygame.sprite.Group()
meteor_sprites = pygame.sprite.Group()
laser_sprites = pygame.sprite.Group()
for i in range(20):
    Star(all_sprites, star_surf)
player = Player(all_sprites)

#custom events
meteor_event = pygame.event.custom_type()
pygame.time.set_timer( meteor_event,500)


async def main():
    global running
    while running:
        dt =clock.tick() / 1000
        #event loop
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player.can_shoot:
                    Laser(laser_surf, player.rect.midtop, (all_sprites, laser_sprites))
                    player.can_shoot = False
                    player.laser_shoot_time = pygame.time.get_ticks()
                    laser_sound.play()
            if event.type == pygame.QUIT:
                running = False

            if event.type == meteor_event:
                x,y = randint(0,window_width), randint(-200,-100)
                Meteor(meteor_surf,(x,y),(all_sprites,meteor_sprites))
        #update  
        all_sprites.update(dt)
        colisions()
        await asyncio.sleep(0)

        #draw the game
        display_surf.fill("#3a2e3f")
        all_sprites.draw(display_surf)

        display_score()
        pygame.display.update()

asyncio.run(main())
pygame.quit()