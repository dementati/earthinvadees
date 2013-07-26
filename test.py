import pygame
from pygame.locals import *
from gameobjects.vector2 import Vector2
from gameobjects.vector3 import Vector3
from gameobjects.util import pi
import math

import util

RESOLUTION = (1024, 768)
BULLET_INITIAL_VELOCITY = 10

window = pygame.display.set_mode(RESOLUTION)
screen = pygame.display.get_surface()

background = pygame.image.load("/home/dementati/Downloads/background.jpg")

class Ship:
	def __init__(self, position, direction, length, color, thrust, max_speed, turn_speed, entities):
		self.position = position
		self.direction = direction
		self.length = length
		self.color = color
		self.thrust = thrust
		self.max_speed = max_speed
		self.turn_speed = turn_speed
		self.entities = entities
		self.velocity = 0

	def accelerate(self):
		if self.velocity < self.max_speed:
			self.velocity += self.thrust

	def decelerate(self):
		if self.velocity > 0:
			self.velocity -= self.thrust

	def turn_left(self):
		self.direction = util.rotate_v(self.direction, -self.turn_speed)

	def turn_right(self):
		self.direction = util.rotate_v(self.direction, self.turn_speed)

	def fire(self):
		self.entities.append(Bullet(self.position.copy(), BULLET_INITIAL_VELOCITY*self.direction))

	def update(self):
		self.position += self.direction*self.velocity

	def render(self, surface):
		p1 = self.position - self.direction*self.length/2
		p2 = self.position + self.direction*self.length/2
		pygame.draw.line(surface, self.color, p1.as_tuple(), p2.as_tuple(), 3)  

class Bullet:
	def __init__(self, position, velocity):
		self.position = position
		self.velocity = velocity

	def update(self):
		self.position += self.velocity

		if self.position.x < 0 or self.position.y < 0 or self.position.x > RESOLUTION[0] or self.position.y > RESOLUTION[1]:
			self.die = True

	def render(self, surface):
		px = int(self.position.x)
		py = int(self.position.y)
		pygame.draw.circle(surface, (255, 0, 0), (px, py), 3, 3) 

class PlayerController:
	def __init__(self, ship):
		self.ship = ship

	def update(self):
		keystate = pygame.key.get_pressed()

		if keystate[K_w]:
			self.ship.accelerate()
		if keystate[K_s]:
			self.ship.decelerate()
		if keystate[K_a]:
			self.ship.turn_left()
		if keystate[K_d]:
			self.ship.turn_right()
		if keystate[K_SPACE]:
			self.ship.fire()

	def render(self, surface):
		return

class AIShipController:
	def __init__(self, ship):
		self.ship = ship

	def set_target(self, target):
		self.target = target

	def update(self):
		# Change direction
		s2t = self.target.position - self.ship.position
		a = util.angle_between_v(self.ship.direction, s2t)
		if a < 0:
			self.ship.turn_left()
		elif a > 0:
			self.ship.turn_right()

		# Change speed
		if math.fabs(a) < 10:
			self.ship.accelerate()	
		elif math.fabs(a) > 20:
			self.ship.decelerate()

	def render(self, surface):
		return


class DummyTarget:
	def __init__(self, position):
		self.position = position

	def render(self, surface):
		px = int(self.position.x)
		py = int(self.position.y)
		pygame.draw.circle(surface, (0, 255, 0), (px, py), 10, 2)

class MouseTarget:
	def __init__(self):
		self.position = Vector2()

	def update(self):
		self.position = pygame.mouse.get_pos()

entities_to_add = []

ship = Ship(Vector2(100, 100), Vector2(0, 1), 10, Vector3(255, 0, 0), 0.01, 10, 2*pi/180, entities_to_add)
ship2 = Ship(Vector2(800, 600), Vector2(-1, 0), 10, Vector3(0, 0, 255), 0.01, 20, 2*pi/180, entities_to_add)
controller = AIShipController(ship)
controller2 = PlayerController(ship2) 
controller.set_target(ship2)

entities = []
entities.append(ship)
entities.append(ship2)
entities.append(controller)
entities.append(controller2)

while True:
	# Update
	for event in pygame.event.get():
		if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
			sys.exit(0)
		else:
			print event

	for entity in entities:
		entity.update()

	entities.extend(entities_to_add)
	del entities_to_add[:]

	entities = [e for e in entities if not hasattr(e, 'die')]
	print len(entities)

	# Render
	screen.blit(background, (0, 0))
	for entity in entities:
		entity.render(screen)

	pygame.display.flip()

