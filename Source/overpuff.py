import pygame, sys
import random
import math
from vectors import *
random.seed()

BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)
RED = (255,   0,   0)
GREEN = (  0, 255,   0)
BLUE = (  0,   0, 255)

pygame.init()
size = (700, 500)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("OverPuffs")

done = False
clock = pygame.time.Clock()
tick_interval = 0.017

NPCBehaviors = ["idle", "wander", "pursue", "attack", "flee"]

# DEFINED NPC BEHAVIORS
class BehaviorType:
    IDLE = 1
    WANDER = 2
    PURSUE = 3
    ATTACK = 4
    FLEE = 5

# STEERING BEHAVIORS
class SteeringBehavior():
        def __init__(self, _vehicle):
                self.behaviors = []
                self.weight_seek = 0.5
                self.weight_wander = 0.5
                self.vehicle = _vehicle
                self.target = None

        def Calculate(self):
                #Weighted Truncated Sum
                total_steering_force = Vec2d(0, 0)
                total_steering_force += self.Seek(self.target) * self.weight_seek
                total_steering_force += self.Wander() * self.weight_wander
                return total_steering_force;

        def SetTarget(self, target):
                self.target = target
                
        def Seek(self, target):
                if (self.target != None):
                        self.behaviors.append( BehaviorType.PURSUE)
                        desired_velocity = (self.target.GetPos() - Vec2d(self.vehicle.rect.x, self.vehicle.rect.y)).normalized() * self.vehicle.max_speed
                        return self.vehicle.mass * (desired_velocity - self.vehicle.velocity)

        def Wander(self):
                self.behaviors.append(BehaviorType.WANDER)
                jitter = 10.0
                x = self.vehicle.rect.x
                y = self.vehicle.rect.y
                RandomTargetPoint = Vec2d(random.uniform(x - jitter, x + jitter), random.uniform(y - jitter, y + jitter))
                desired_velocity = (RandomTargetPoint - Vec2d(self.vehicle.rect.x, self.vehicle.rect.y)).normalized() * self.vehicle.max_speed
                return self.vehicle.mass * (desired_velocity - self.vehicle.velocity)


# SPRITE CLASS
class MovingEntity(pygame.sprite.Sprite):
        def __init__(self, color, width, height):
                pygame.sprite.Sprite.__init__(self)
                self.velocity = Vec2d(0,0)
                self.heading = Vec2d(0,0)
                self.mass = 1.0
                self.max_speed = 200.0
                self.max_force = 1000.0
                self.max_turnrate = 0.3

class Doge(MovingEntity):
        def __init__(self, color, width, height):
                MovingEntity.__init__(self, color, width, height)
                self.image = pygame.image.load("../Assets/Sprites/derpdog.gif")
                self.rect = self.image.get_rect()
                #physics variables
                self.steering_behavior = SteeringBehavior(self)
                
        def Update(self, time_elapsed):
                steering_force = self.steering_behavior.Calculate()
                acceleration = steering_force / self.mass
                self.velocity += acceleration * time_elapsed
                self.velocity = self.LimitVelocity(self.velocity, self.max_speed)
                #updating position
                self.rect += self.velocity * time_elapsed
                if (self.velocity.get_length_sqrd() > 0.00000001):
                        self.heading = self.velocity.normalized()

        def SetTarget(self, target):
                self.steering_behavior.target = target

        def LimitVelocity(self, velocity, max_speed):
                velocity_trunc = Vec2d(velocity[0], velocity[1])
                if (velocity[0] >= 0):
                        velocity_trunc[0] = min(velocity[0], max_speed)
                else:
                        velocity_trunc[0] = max(velocity[0], -max_speed)
                if (velocity[0] >= 0):
                        velocity_trunc[1] = min(velocity[1], max_speed)
                else:
                        velocity_trunc[1] = max(velocity[1], -max_speed)
                return velocity_trunc        

class Player(pygame.sprite.Sprite):
        def __init__(self, color, width, height):
                pygame.sprite.Sprite.__init__(self)
                self.image = pygame.image.load("../Assets/Sprites/8-bit-ana.png")
                self.rect = self.image.get_rect()
                self.size = self.image.get_rect().size

        def GetPos(self):
                return Vec2d(self.rect[0], self.rect[1])

        def moveRight(self, pixels):
                self.rect = (self.rect[0] + pixels, self.rect[1])
 
        def moveLeft(self, pixels):
                self.rect = (self.rect[0] - pixels, self.rect[1])

        def moveUp(self, pixels):
                self.rect = (self.rect[0], self.rect[1] - pixels)

        def moveDown(self, pixels):
                self.rect = (self.rect[0], self.rect[1] + pixels)
                
all_sprites_list = pygame.sprite.Group()
dogos = []
num_doges = 10
screen_center = (size[0]/2, size[1]/2)

player = Player(WHITE, 10, 10)
player.rect = (screen_center[0] - player.size[0]/2, screen_center[1] - player.size[1]/2) 
all_sprites_list.add(player)

radius = 200.0
radial_step = 2.0 * math.pi / num_doges
for x in range(0, num_doges):
        dogo = Doge(WHITE, 10, 10)
        dogo.SetTarget(player)
        dogo.rect.x = screen_center[0] + radius * math.sin(radial_step * x)
        dogo.rect.y = screen_center[1] + radius * math.cos(radial_step * x)
        all_sprites_list.add(dogo)
        dogos.append(dogo)

# MAIN GAME LOOP
while not done:
        # if quitting
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                        done = True
                elif event.type==pygame.KEYDOWN:
                        if event.key==pygame.K_ESCAPE: #Pressing the x Key will quit the game
                                done = True
 
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player.moveLeft(5)
        if keys[pygame.K_RIGHT]:
            player.moveRight(5)
        if keys[pygame.K_UP]:
            player.moveUp(5)
        if keys[pygame.K_DOWN]:
            player.moveDown(5)
        
        # update tiles
        screen.fill(BLACK) #clear previous frame
        
        all_sprites_list.draw(screen)

        for d in dogos:
                d.Update(tick_interval)

        pygame.display.flip()
        clock.tick(1/tick_interval) #~60 frames per second

pygame.quit()
