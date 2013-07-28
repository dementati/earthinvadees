import math

import pygame
from pygame.locals import *

from gameobjects.vector2 import Vector2

import util

class MothershipPlayerController(object):
	def __init__(self, params):
		self.ship = params["ship"]
		self.world_rect = params["world_rect"]

	def head_for(self, position):
		# Change direction
		s2t = position - self.ship.position
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

		return a

	def update(self, dt, entities):
		if not self.world_rect.colliderect(self.ship.bb):
			self.head_for(Vector2(WORLD_RECT.center))
		else:
			keystate = pygame.key.get_pressed()

			if keystate[K_w]:
				self.ship.move_up(dt)
			if keystate[K_s]:
				self.ship.move_down(dt)
			if keystate[K_a]:
				self.ship.move_left(dt)
			if keystate[K_d]:
				self.ship.move_right(dt)

class AIShipController(object):
	def __init__(self, params):
		self.ship = params["ship"]
		self.target = None
		self.cruise_speed = params["cruise_speed"]
		self.world_rect = params["world_rect"]

	def set_target(self, target):
		self.target = target

	def head_for(self, dt, position):
		# Change direction
		s2t = position - self.ship.position
		a = util.angle_between_v(self.ship.direction, s2t)
		if a < 0:
			self.ship.turn_left(dt)
		elif a > 0:
			self.ship.turn_right(dt)

		# Change speed
		if math.fabs(a) < 10:
			v = util.project_v(self.ship.velocity, self.ship.direction)
			if v.get_magnitude() < self.cruise_speed:
				self.ship.accelerate(dt)	
			else:
				self.ship.decelerate(dt)

		return a

	def stop(self, dt):
		a = util.angle_between_v(self.ship.direction, -self.ship.velocity)
		if a < 0:
			self.ship.turn_left(dt)
		else:
			self.ship.turn_right(dt)

		if math.fabs(a) < 10:
			self.ship.accelerate(dt)

	def update(self, dt, entities):
		if not self.world_rect.colliderect(self.ship.bb):
			self.head_for(dt, Vector2(self.world_rect.center))
		elif self.target != None:
			if hasattr(self.target, "die"):
				self.target = None
			else:
				a = self.head_for(dt, self.target.position)		
				if math.fabs(a) < 10:
					self.ship.fire()
				
				dist = (self.target.position - self.ship.position).get_magnitude()
				if dist > self.ship.sensor_range:
					self.target = None
		else:
			self.stop(dt)
			self.target = self.ship.last_detected


