import math

import pygame
from pygame.locals import *

from gameobjects.vector2 import Vector2

import util
from objects import Ship

class AlienMothershipPlayerController(object):
	def __init__(self, params):
		self.ship = params["ship"]
		self.world_rect = params["world_rect"]

	def head_for(self, dt, position):
		# Change direction
		s2t = position - self.ship.position
		if s2t.x > 0:
			self.ship.move_right(dt)
		else:
			self.ship.move_left(dt)
		
		if s2t.y > 0: 
			self.ship.move_down(dt)
		else:
			self.ship.move_up(dt)

	def handle_event(self, event):
		if event.type == KEYDOWN:
			if event.key == K_1:
				self.ship.spawn(0)
			elif event.key == K_2:
				self.ship.spawn(1)
			elif event.key == K_3:
				self.ship.spawn(2)

	def update(self, dt, entities):
		if not self.world_rect.colliderect(self.ship.bb):
			self.head_for(dt, Vector2(self.world_rect.center))
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

class TerranMothershipAIController(object):
	def __init__(self, params):
		self.ship = params["ship"]
		self.world_rect = params["world_rect"]
		self.cruise_speed = params["cruise_speed"]

	def align_to(self, dt, v):
		a = util.angle_between_v(self.ship.direction, v)
		if a < 0:
			self.ship.turn_left(dt)
		else:
			self.ship.turn_right(dt)

		return a

	def stop(self, dt):
		a = util.angle_between_v(self.ship.direction, self.ship.velocity)
		ma = util.angle_between_v(self.ship.direction, -self.ship.velocity)
		aa = math.fabs(a)
		ama = math.fabs(ma)

		if aa < ama:
			self.align_to(dt, self.ship.velocity)
	
			if a < 0:
				self.ship.turn_left(dt)
			else:
				self.ship.turn_right(dt)

			if aa < 10:
				self.ship.decelerate(dt)
		else:
			self.align_to(dt, -self.ship.velocity)
		
			if ma < 0:
				self.ship.turn_left(dt)
			else:
				self.ship.turn_right(dt)

			if ama < 10:
				self.ship.accelerate(dt)

	def head_for(self, dt, position):
		s2t = position - self.ship.position
		v = util.project_v(self.ship.velocity, s2t)

		ratio = 0
		if self.ship.velocity.get_magnitude() > 0:
			v2 = util.project_v(v, self.ship.velocity)
			ratio = v.get_magnitude()/self.ship.velocity.get_magnitude()

		ret_a = 180
		if ratio > 0.99 or self.ship.velocity.get_magnitude() < 0.01:
			a = 180
			if s2t.get_magnitude() > (1.0/self.cruise_speed)*v.get_magnitude():
				a = self.align_to(dt, s2t)
				ret_a = a
			else:
				a = self.align_to(dt, -s2t)
	
			if math.fabs(a) < 10:
				self.ship.accelerate(dt)
		else:
			self.stop(dt)

		return ret_a

	def update(self, dt, entities):
		if not self.world_rect.colliderect(self.ship.bb):
			self.head_for(dt, Vector2(self.world_rect.center))
		else:
			self.stop(dt)

		fc = 0
		bcc = 0
		bsc = 0
		for entity in entities:
			if isinstance(entity, Ship): 
				if entity.name == "alien_mothership":
					self.ship.mission = entity

				if entity.name == "terran_fighter":
					fc += 1
				elif entity.name == "terran_battlecruiser":
					bcc += 1
				elif entity.name == "terran_battleship":
					bsc += 1

		fs = self.ship.blueprints[0][0]["resource_cost"]
		bcs = self.ship.blueprints[1][0]["resource_cost"]
		bss = self.ship.blueprints[2][0]["resource_cost"]

		l = [(fc+1)*fs, (bcc+1)*bcs, (bsc+1)*bss]
		mx = 9999999
		mxi = -1
		for i in range(len(l)):
			if l[i] < mx:
				mx = l[i]
				mxi = i

		self.ship.spawn(mxi)

class FighterAIController(object):
	def __init__(self, params):
		self.ship = params["ship"]
		self.target = None
		self.cruise_speed = params["cruise_speed"]
		self.world_rect = params["world_rect"]
		self.mission = None

	def set_mission(self, mission):
		self.mission = mission

	def set_target(self, target):
		self.target = target

	def align_to(self, dt, v):
		a = util.angle_between_v(self.ship.direction, v)
		if a < 0:
			self.ship.turn_left(dt)
		else:
			self.ship.turn_right(dt)

		return a

	def head_for(self, dt, position):
		s2t = position - self.ship.position
		v = util.project_v(self.ship.velocity, s2t)

		ratio = 0
		if self.ship.velocity.get_magnitude() > 0:
			v2 = util.project_v(v, self.ship.velocity)
			ratio = v.get_magnitude()/self.ship.velocity.get_magnitude()

		ret_a = 180
		if ratio > 0.99 or self.ship.velocity.get_magnitude() < 0.01:
			a = 180
			if s2t.get_magnitude() > (1.0/self.cruise_speed)*v.get_magnitude():
				a = self.align_to(dt, s2t)
				ret_a = a
			else:
				a = self.align_to(dt, -s2t)
	
			if math.fabs(a) < 10:
				self.ship.accelerate(dt)
		else:
			self.stop(dt)

		return ret_a

	def attack(self, dt, target):
		s2t = target.position - self.ship.position

		a = self.align_to(dt, s2t)
		if math.fabs(a) < 5:
			if s2t.get_magnitude() < 1500:
				self.ship.fire()

				v = util.project_v(self.ship.velocity, s2t)
				if (v+s2t).get_magnitude() > max([v.get_magnitude(), s2t.get_magnitude()]):
					self.ship.decelerate(dt)
				else:
					self.ship.accelerate(dt)
			else:
				self.ship.accelerate(dt)

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
		elif isinstance(self.target, Ship):
			if hasattr(self.target, "die"):
				self.target = None
			else:
				self.attack(dt, self.target)
				
				dist = (self.target.position - self.ship.position).get_magnitude()
				if dist > self.ship.sensor_range:
					self.target = None
		elif type(self.mission) == Vector2 or isinstance(self.mission, Ship):
			if type(self.mission) == Vector2:
				self.head_for(dt, self.mission)

				dist = (self.mission - self.ship.position).get_magnitude()
				if dist < 100:
					self.mission = None

			else:
				if hasattr(self.mission, "die"):
					self.mission = None
				else:
					self.attack(dt, self.mission)

		if not isinstance(self.target, Ship):
			self.target = self.ship.last_detected

		if not isinstance(self.target, Ship) and not isinstance(self.mission, Ship) and not isinstance(self.mission, Vector2):
			self.stop(dt)

