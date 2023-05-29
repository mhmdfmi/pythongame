import sys
import random
from typing import Any
import pygame
from pygame.locals import *
from pygame.sprite import Group

pygame.init()

''' IMAGES'''

player_ship = 'plyship.png'
enemy_ship = 'enemyship.png'
ufo_ship = 'ufo.png'
player_bullet = 'pbullet.png'
enemy_bullet = 'enemybullet.png'
ufo_bullet = 'enemybullet.png'



screen = pygame.display.set_mode((0,0), FULLSCREEN)
s_width, s_height = screen.get_size()

clock = pygame.time.Clock()
FPS = 60

background_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
ufo_group = pygame.sprite.Group()
sprite_group = pygame.sprite.Group()
playerBullet_group = pygame.sprite.Group()
enemyBullet_group = pygame.sprite.Group()
ufoBullet_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
particle_group = pygame.sprite.Group()

pygame.mouse.set_visible(False)

class Background(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        self.image = pygame.Surface([x, y])
        self.image.fill('white')
        self.image.set_colorkey('black')
        self.rect = self.image.get_rect()

    def update(self):
        self.rect.y += 1
        self.rect.x += 1
        if self.rect.y > s_height:
            self.rect.y = random.randrange(-10, 0)
            self.rect.x = random.randrange(-400, s_width)

class Particle(Background):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.rect.x = random.randrange(0, s_width)
        self.rect.y = random.randrange(0, s_height)
        self.image.fill('blue')
        self.vel = random.randint(3, 8)

    def Update(self):
        self.rect.y += self.vel
        if self.rect.y > s_height:
            self.rect.x = random.randrange(0, s_width)
            self.rect.y = random.randrange(0, s_height)

class Player(pygame.sprite.Sprite):
    def __init__(self, img):
        super().__init__()
        self.image = pygame.image.load(img)
        self.rect = self.image.get_rect()
        self.image.set_colorkey('black')
        self.alive = True
        self.countToAlive = 0
        self.activateBullet = True
        self.alphaDuration = 0

    def update(self):
        if self.alive:
            self.image.set_alpha(80)
            self.alphaDuration += 1
            if self.alphaDuration > 170:
                self.image.set_alpha(255)
            mouse = pygame.mouse.get_pos()
            self.rect.x = mouse[0] - 20
            self.rect.y = mouse[1] + 40
        else:
            self.alphaDuration = 0
            expl_x = self.rect.x + 20
            expl_y = self.rect.y + 40
            explosion = Explosion(expl_x, expl_y)
            explosion_group.add(explosion)
            sprite_group.add(explosion)
            pygame.time.delay(20)
            self.rect.y = s_height + 200
            self.countToAlive += 1
            if self.countToAlive > 100:
                self.alive = True
                self.countToAlive = 0
                self.activateBullet = True

    def shoot(self):
        if self.activateBullet:
            bullet = PlayerBullet(player_bullet)
            mouse = pygame.mouse.get_pos()
            bullet.rect.x = mouse[0]
            bullet.rect.y = mouse[1]
            playerBullet_group.add(bullet)
            sprite_group.add(bullet)

    def dead(self):
        self.alive = False
        self.activateBullet = False
        
class Enemy(Player):
    def __init__(self, img):
        super().__init__(img)
        self.rect.x = random.randrange(80, s_width - 80)
        self.rect.y = random.randrange(-500, 0)
        screen.blit(self.image, (self.rect.x, self.rect.y))

    def update(self):
        self.rect.y += 1
        if self.rect.y > s_height:
            self.rect.x = random.randrange(80, s_width - 80)
            self.rect.y = random.randrange(-2000, 0)
        self.shoot()

    def shoot(self):
        if self.rect.y in (0, 300, 700):
            ufobullet = EnemyBullet(ufo_bullet)
            ufobullet.rect.x = self.rect.x + 20
            ufobullet.rect.y = self.rect.y +50 
            ufoBullet_group.add(ufobullet)
            sprite_group.add(ufobullet)

class Ufo(Enemy):
    def __init__(self, img):
        super().__init__(img)
        self.rect.x = -200
        self.rect.y = 200
        self.move = 1

    def update(self):
        self.rect.x += self.move
        if self.rect.x > s_width + 200:
            self.move *= -1
        elif self.rect.x < -200:
            self.move *= -1
        self.shoot()

    def shoot(self):
        if self.rect.x % 40 == 0:
            ufobullet = EnemyBullet(ufo_bullet)
            ufobullet.rect.x = self.rect.x + 50
            ufobullet.rect.y = self.rect.y + 70
            ufoBullet_group.add(ufobullet)
            sprite_group.add(ufobullet)

class PlayerBullet(pygame.sprite.Sprite):
    def __init__(self, img):
        super().__init__()
        self.image = pygame.image.load(img)
        self.rect = self.image.get_rect()
        self.image.set_colorkey('black')

    def update(self):
        self.rect.y -= 15
        if self.rect.y < 0:
            self.kill()

class EnemyBullet(PlayerBullet):
    def __init__(self, img):
        super().__init__(img)
        self.image.set_colorkey('white')

    def update(self):
        self.rect.y += 3
        if self.rect.y > s_height:
            self.kill()

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.img_list = []
        for i in range(1, 6):
            img = pygame.image.load(f'exp{i}.png').convert()
            img.set_colorkey('black')
            img = pygame.transform.scale(img, (120, 120))
            self.img_list.append(img)
        self.index = 0
        self.image = self.img_list[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.countDelay = 0

    def update(self):
        self.countDelay += 1
        if self.countDelay >= 12:
            if self.index < len(self.img_list) - 1:
                self.countDelay = 0
                self.index += 1
                self.image = self.img_list[self.index]
        if self.index >= len(self.img_list) - 1:
            if self.countDelay >= 12:
                self.kill()

class Game:
    def __init__(self):
        self.countHit = 0
        self.countHit2 = 0
        self.lives = 3
        self.score = 0
        self.init_create = True
        self.start_screen()

    def start_text(self):
        font = pygame.font.SysFont('Calibri', 50)
        text = font.render('SPACE WAR', True, 'blue')
        text_rect = text.get_rect(center=(s_width/2, s_height/2))
        screen.blit(text, text_rect)

        font2 = pygame.font.SysFont('Calibri', 30)
        text2 = font2.render('Press ENTER to START', True, 'white')
        text2_rect = text2.get_rect(center=(s_width/2, s_height/2 + 60))
        screen.blit(text2, text2_rect)

        font3 = pygame.font.SysFont('Calibri', 30)
        text3 = font3.render('Press ESC to QUIT', True, 'white')
        text3_rect = text3.get_rect(center=(s_width/2, s_height/2 + 120))
        screen.blit(text3, text3_rect)

        font4 = pygame.font.SysFont('Calibri', 15)
        text4 = font4.render('PyGame 2023 copy from YT = Python Project', True, 'white')
        text4_rect = text4.get_rect(center=(s_width/2, s_height/2 + 350))
        screen.blit(text4, text4_rect)

        font5 = pygame.font.SysFont('Calibri', 15)
        text5 = font5.render('Created by : UCOXX', True, 'white')
        text5_rect = text5.get_rect(center=(s_width/2 + -570, s_height/2 + 350))
        screen.blit(text5, text5_rect)

    def start_screen(self):
        while True:
            screen.fill('black')
            self.start_text()
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    
                    if event.key == K_RETURN:
                        self.run_game()

            pygame.display.update()


    def pause_screen(self):
        self.init_create = False
        while True:
            self.pause_text()
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.start_screen()
                    
                    if event.key == K_SPACE:
                        self.run_game()

            pygame.display.update()

    def pause_text(self):
        font = pygame.font.SysFont('Calibri', 50)
        text = font.render('PAUSED', True, 'white')
        text_rect = text.get_rect(center=(s_width/2, s_height/2))
        screen.blit(text, text_rect)

        font2 = pygame.font.SysFont('Calibri', 30)
        text2 = font2.render('Press ESC to BACK', True, 'white')
        text2_rect = text2.get_rect(center=(s_width/2, s_height/2 + 60))
        screen.blit(text2, text2_rect)

        font3 = pygame.font.SysFont('Calibri', 30)
        text3 = font3.render('Press SPACE to RESUME', True, 'white')
        text3_rect = text3.get_rect(center=(s_width/2, s_height/2 + 120))
        screen.blit(text3, text3_rect)

    def gameOver_text(self):
        font = pygame.font.SysFont('Calibri', 50)
        text = font.render('GAME OVER', True, 'red')
        text_rect = text.get_rect(center=(s_width/2, s_height/2))
        screen.blit(text, text_rect)

        font2 = pygame.font.SysFont('Calibri', 30)
        text2 = font2.render('Press ESC to QUIT', True, 'white')
        text2_rect = text2.get_rect(center=(s_width/2, s_height/2 + 60))
        screen.blit(text2, text2_rect)

        font3 = pygame.font.SysFont('Calibri', 30)
        text3 = font3.render('Press R to RESTART', True, 'white')
        text3_rect = text3.get_rect(center=(s_width/2, s_height/2 + 120))
        screen.blit(text3, text3_rect)

    def gameOver_screen(self):
        while True:
            screen.fill('black')
            self.gameOver_text()
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        pygame.quit()
                        sys.exit()

                    if event.key == K_r:
                        self.start_screen()

            pygame.display.update()


    def create_background(self):
        for i in range(30):
            x = random.randint(1,5)
            background_image = Background(x,x)
            background_image.rect.x = random.randrange(0, s_width)
            background_image.rect.y = random.randrange(0, s_height)
            background_group.add(background_image)
            sprite_group.add(background_image)

    def create_particle(self):
        for i in range(100):
            x = 1
            y = random.randint(1, 7)
            particle = Particle(x, y)
            particle_group.add(particle)
            sprite_group.add(particle)

    def create_player(self):
        self.player = Player(player_ship)
        player_group.add(self.player)
        sprite_group.add(self.player) 

    def create_enemy(self):
        for i in range(8):
            self.enemy = Enemy(enemy_ship)
            enemy_group.add(self.enemy)
            sprite_group.add(self.enemy)

    def create_ufo(self):
        for i in range(1):
            self.ufo = Ufo(ufo_ship)
            ufo_group.add(self.ufo)
            sprite_group.add(self.ufo)

    def playerBulletHitsEnemy(self):
        hits = pygame.sprite.groupcollide(enemy_group, playerBullet_group, False, True)
        for i in hits:
            self.countHit += 1
            if self.countHit == 3:
                self.score += 10
                expl_x = i.rect.x + 20
                expl_y = i.rect.y + 40
                explosion = Explosion(expl_x, expl_y)
                explosion_group.add(explosion)
                sprite_group.add(explosion)
                i.rect.x = random.randrange(0, s_width)
                i.rect.y = random.randrange(-3000, -100)
                self.countHit = 0

    def playerBulletHitsUfo(self):
        hits = pygame.sprite.groupcollide(ufo_group, playerBullet_group, False, True)
        for i in hits:
            self.countHit2 += 1
            if self.countHit2 == 10:
                self.score += 20
                expl_x = i.rect.x + 50
                expl_y = i.rect.y + 60
                explosion = Explosion(expl_x, expl_y)
                explosion_group.add(explosion)
                sprite_group.add(explosion)
                i.rect.x = -199
                self.countHit2 = 0

    def enemyBulletHitsPlayer(self):
        if self.player.image.get_alpha() == 255:
            hits = pygame.sprite.spritecollide(self.player, enemyBullet_group, True)
            if hits:
                self.lives -= 1
                self.player.dead()
                if self.lives < 0:
                    self.gameOver_screen()

    def ufoBulletHitsPlayer(self):
        if self.player.image.get_alpha() == 255:
            hits = pygame.sprite.spritecollide(self.player, ufoBullet_group, True)
            if hits:
                self.lives -= 1
                self.player.dead()
                if self.lives < 0:
                    self.gameOver_screen()

    def playerEnemyCrash(self):
        if self.player.image.get_alpha() == 255:
            hits = pygame.sprite.spritecollide(self.player, enemy_group, False)
            if hits:
                for i in hits:
                    i.rect.x = random.randrange(0, s_width)
                    i.rect.y = random.randrange(-3000, -100)
                    self.lives -= 1
                    self.player.dead()
                    if self.lives < 0:
                        self.gameOver_screen()

    def playerUfoCrash(self):
        if self.player.image.get_alpha() == 255:
            hits = pygame.sprite.spritecollide(self.player, ufo_group, False)
            if hits:
                for i in hits:
                    i.rect.x = -199
                    self.lives -= 1
                    self.player.dead()
                    if self.lives < 0:
                        self.gameOver_screen()
                        

    def create_lives(self):
        self.live_img = pygame.image.load(player_ship)
        self.live_img = pygame.transform.scale(self.live_img, (23,25))
        n = 0
        for i in range(self.lives):
            screen.blit(self.live_img, (0+n, s_height - 715))
            n += 60

    def create_score(self):
        score = self.score
        font = pygame.font.SysFont('Calibri', 30)
        text = font.render(str(score), True, 'green')
        text_rect = text.get_rect(center=(s_width-150, s_height-700))
        screen.blit(text, text_rect)

    def run_update(self):
        sprite_group.draw(screen)
        sprite_group.update()


    def run_game(self):
        if self.init_create:
            self.create_background()
            self.create_particle()
            self.create_player()
            self.create_enemy()
            self.create_ufo()
        while True:
            screen.fill('black')
            self.enemyBulletHitsPlayer()
            self.playerBulletHitsEnemy()
            self.ufoBulletHitsPlayer()
            self.playerEnemyCrash()
            self.playerUfoCrash()
            self.playerBulletHitsUfo()
            self.run_update()
            pygame.draw.rect(screen, 'black', (0,0,s_width,30))
            self.create_lives()
            self.create_score()
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == KEYDOWN:
                    if event.key == K_s:
                        self.player.shoot()
                    if event.key == K_ESCAPE:
                        pygame.quit()
                        sys.exit()

                    if event.key == K_SPACE:
                        self.pause_screen()
                        
            pygame.display.update()
            clock.tick(FPS)

def main():
    game = Game()

if __name__ == '__main__':
    main()