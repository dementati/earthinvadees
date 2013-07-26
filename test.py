import pygame
from pygame.locals import *
from gameobjects.vector2 import Vector2
from gameobjects.vector3 import Vector3
from gameobjects.util import pi
import math

import util

resolution = (1024, 768)

window = pygame.display.set_mode(resolution)
screen = pygame.display.get_surface()

background = pygame.image.load("/home/dementati/Downloads/background.jpg")

class Ship:
	def __init__(self, position, direction, length, color, speed, turn_speed):
		self.position = position
		self.direction = direction
		self.length = length
		self.color = color
		self.speed = speed
		self.turn_speed = turn_speed
		self.velocity = 0

	def accelerate(self):
		self.velocity += self.speed

	def decelerate(self):
		self.velocity -= self.speed

	def turn_left(self):
		self.direction = util.rotate_v(self.direction, self.turn_speed)

	def turn_right(self):
		self.direction = util.rotate_v(self.direction, -self.turn_speed)

	def update(self):
		self.position += self.direction*self.velocity

	def render(self, surface):
		p1 = self.position - self.direction*self.length/2
		p2 = self.position + self.direction*self.length/2
		pygame.draw.line(surface, self.color, p1.as_tuple(), p2.as_tuple(), 3)  

class AIShipController:
	def __init__(self, ship, accThreshold):
		self.ship = ship
		self.accThreshold = accThreshold

	def set_target(self, target):
		self.target = target

	def update(self):
		# Change direction
		s2t = self.target.position - self.ship.position
		a = util.angle_between_v(self.ship.direction, s2t)
		if a < 0:
			self.ship.turn_right()
		elif a > 0:
			self.ship.turn_left()

		# Change speed
		if math.fabs(a) < 10:
			self.ship.accelerate()	
		elif math.fabs(a) > 20:
			self.ship.decelerate()

class DummyTarget:
	def __init__(self, position):
		self.position = position

	def render(self, surface):
		px = int(self.position.x)
		py = int(self.position.y)
		pygame.draw.circle(surface, (0, 255, 0), (px, py), 10, 2)

ship = Ship(Vector2(100, 100), Vector2(0, 1), 10, Vector3(255, 0, 0), 0.1, 2*pi/180)
target = DummyTarget(Vector2(500, 300))
controller = AIShipController(ship, 100)
controller.set_target(target)

while True:

	# Update
	keystate = pygame.key.get_pressed()

	for event in pygame.event.get():
		if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
			sys.exit(0)
		else:
			print event

	if keystate[K_w]:
		ship.accelerate()
	if keystate[K_s]:
		ship.decelerate()
	if keystate[K_a]:
		ship.turn_left()
	if keystate[K_d]:
		ship.turn_right()

	controller.update()
	ship.update()

	# Render
	screen.blit(background, (0, 0))
	ship.render(screen)
	target.render(screen)
	pygame.display.flip()

