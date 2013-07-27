import pygame
from pygame.locals import *
from pygame import Rect
from gameobjects.vector2 import Vector2
from gameobjects.vector3 import Vector3
from gameobjects.util import pi
import math

import util

RESOLUTION = (1024, 768)
BULLET_INITIAL_VELOCITY = 0.1
RENDER_BB = False

window = pygame.display.set_mode(RESOLUTION)
screen = pygame.display.get_surface()

background = pygame.image.load("/home/dementati/Downloads/background.jpg")

class Ship(object):
	def __init__(self, params, entities):

		self.position = params["position"]
		self.direction = params["direction"]
		self.length = params["length"]
		self.color = params["color"]
		self.thrust = params["thrust"]
		self.max_speed = params["max_speed"]
		self.turn_speed = params["turn_speed"]
		self.fire_rate = params["fire_rate"]
		self.shield = params["shield"]
		self.attack_power = params["attack_power"]
		self.bb = Rect(0,0,0,0)
		self.last_fired = 0
		self.entities = entities
		self.velocity = 0

	def accelerate(self, dt):
		if self.velocity < self.max_speed:
			self.velocity += dt*self.thrust

	def decelerate(self, dt):
		if self.velocity > 0:
			self.velocity -= dt*self.thrust

	def turn_left(self, dt):
		self.direction = util.rotate_v(self.direction, -dt*self.turn_speed)

	def turn_right(self, dt):
		self.direction = util.rotate_v(self.direction, dt*self.turn_speed)

	def fire(self):
		if self.last_fired > self.fire_rate:
			v = self.velocity + BULLET_INITIAL_VELOCITY
			self.entities.append(Bullet(self.position.copy() + self.direction*10, v*self.direction, 3, self.attack_power))
			self.last_fired = 0

	def collides(self, entity):
		return hasattr(entity, "bb") and self.bb.colliderect(entity.bb)

	def collided(self, entity):
		if type(entity) is Bullet:
			self.shield -= entity.attack_power

	def update_bb(self):
		p1 = self.position - self.direction*self.length/2
		p2 = self.position + self.direction*self.length/2
		tl = (min([p1.x, p2.x]), min([p1.y, p2.y]))
		br = (max([p1.x, p2.x]), max([p1.y, p2.y]))
		self.bb.topleft = tl
		self.bb.size = (br[0] - tl[0], br[1] - tl[1])

	def update(self, dt):
		self.position += dt*self.direction*self.velocity
		self.update_bb()

		if self.shield < 0:
			self.die = True
		
		if self.last_fired < 9999999:
			self.last_fired += dt

	def render(self, surface):
		p1 = self.position - self.direction*self.length/2
		p2 = self.position + self.direction*self.length/2
		pygame.draw.line(surface, self.color, p1.as_tuple(), p2.as_tuple(), 3)  

		if RENDER_BB:
			pygame.draw.rect(surface, (255, 255, 255), self.bb)

class Bullet(object):
	def __init__(self, position, velocity, radius, attack_power):
		self.position = position
		self.velocity = velocity
		self.radius = radius
		self.attack_power = attack_power
		self.bb = Rect(0, 0, 2*radius, 2*radius)
		self.bb.center = self.position

	def collides(self, entity):
		return hasattr(entity, "bb") and self.bb.colliderect(entity.bb)

	def collided(self, entity):
		self.die = True

	def update(self, dt):
		self.position += dt*self.velocity
		self.bb.center = self.position

		if self.position.x < 0 or self.position.y < 0 or self.position.x > RESOLUTION[0] or self.position.y > RESOLUTION[1]:
			self.die = True

	def render(self, surface):
		px = int(self.position.x)
		py = int(self.position.y)
		pygame.draw.circle(surface, (255, 255, 0), (px, py), self.radius) 

		if RENDER_BB:
			pygame.draw.rect(surface, (255, 255, 255), self.bb)

class PlayerController(object):
	def __init__(self, ship):
		self.ship = ship

	def update(self, dt):
		keystate = pygame.key.get_pressed()

		if keystate[K_w]:
			self.ship.accelerate(dt)
		if keystate[K_s]:
			self.ship.decelerate(dt)
		if keystate[K_a]:
			self.ship.turn_left(dt)
		if keystate[K_d]:
			self.ship.turn_right(dt)
		if keystate[K_SPACE]:
			self.ship.fire()

class AIShipController(object):
	def __init__(self, ship):
		self.ship = ship

	def set_target(self, target):
		self.target = target

	def update(self, dt):
		# Change direction
		s2t = self.target.position - self.ship.position
		a = util.angle_between_v(self.ship.direction, s2t)
		if a < 0:
			self.ship.turn_left(dt)
		elif a > 0:
			self.ship.turn_right(dt)

		# Change speed
		if math.fabs(a) < 10:
			self.ship.accelerate(dt)	
		elif math.fabs(a) > 20:
			self.ship.decelerate(dt)

class DummyTarget(object):
	def __init__(self, position):
		self.position = position

	def render(self, surface):
		px = int(self.position.x)
		py = int(self.position.y)
		pygame.draw.circle(surface, (0, 255, 0), (px, py), 10, 2)

class MouseTarget(object):
	def __init__(self):
		self.position = Vector2()

	def update(self, dt):
		self.position = pygame.mouse.get_pos()

clock = pygame.time.Clock()

entities_to_add = []

shipParams = {
	"position" : Vector2(100, 100),
	"direction" : Vector2(0, 1),
	"length" : 10,
	"color" : Vector3(255, 0, 0),
	"thrust" : 0.0001,
	"max_speed" : 10,
	"turn_speed" : 0.1*pi/180,
	"fire_rate" : 250,
	"shield" : 100,
	"attack_power" : 10,
	"bb" : Rect(0, 0, 5, 10)
}

ship2Params = {
	"position" : Vector2(800, 600),
	"direction" : Vector2(-1, 0),
	"length" : 10,
	"color" : Vector3(0, 0, 255),
	"thrust" : 0.0001,
	"max_speed" : 20,
	"turn_speed" : 0.1*pi/180,
	"fire_rate" : 250,
	"shield" : 100,
	"attack_power" : 10,
	"bb" : Rect(0, 0, 5, 10)
}

ship = Ship(shipParams, entities_to_add)
ship2 = Ship(ship2Params, entities_to_add)
#controller = AIShipController(ship)
controller2 = PlayerController(ship2) 
#controller.set_target(ship2)

entities = []
entities.append(ship)
entities.append(ship2)
#entities.append(controller)
entities.append(controller2)

while True:
	dt = clock.tick(50)

	# Update
	for event in pygame.event.get():
		if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
			sys.exit(0)
		else:
			print event

	for entity in entities:
		if hasattr(entity, "update"):
			entity.update(dt)

	for entity1 in entities:
		if hasattr(entity1, "collides"):
			for entity2 in entities:
				if entity1 != entity2 and entity1.collides(entity2):
					entity1.collided(entity2)

	entities.extend(entities_to_add)
	del entities_to_add[:]

	entities = [e for e in entities if not hasattr(e, 'die')]

	# Render
	screen.blit(background, (0, 0))
	for entity in entities:
		if hasattr(entity, "render"):
			entity.render(screen)

	pygame.display.flip()

