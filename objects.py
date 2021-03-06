
import util
import copy
import random
import math

import pygame
from pygame import Rect

from gameobjects.vector2 import Vector2
from gameobjects.vector3 import Vector3

RENDER_BB = False
RENDER_FORCEFIELD = False

class Ship(object):
	def __init__(self, params, entities_to_add):
		self.position = params["position"]
		self.direction = params["direction"]
		self.team = params["team"]
		self.thrust = params["thrust"]
		self.max_speed = params["max_speed"]
		self.turn_speed = params["turn_speed"]
		self.shield = params["shield"]
		self.sensor_range = params["sensor_range"]
		self.forcefield_radius = params["forcefield_radius"]
		self.forcefield_strength = params["forcefield_strength"]
		self.graphic = params["graphic"]
		self.graphic_direction = params["graphic_direction"]
		self.graphic_scale = params["graphic_scale"]
		self.weapon = params["weapon"]
		self.bb = Rect(0,0,0,0)
		self.last_fired = 0
		self.entities_to_add = entities_to_add
		self.velocity = Vector2()
		self.last_detected = None
		self.resource_cost = params["resource_cost"]
		self.name = params["name"]
		self.destroyed_sound = params["destroyed_sound"]
		self.sound_player = params["sound_player"]

		if self.team == "blue":
			self.color = Vector3(0, 0, 255)
		elif self.team == "red":
			self.color = Vector3(255, 0, 0)

	def accelerate(self, dt, magnitude=1):
		self.velocity += dt*self.thrust*self.direction*magnitude

	def decelerate(self, dt, magnitude=1):
		self.velocity -= dt*self.thrust*self.direction*magnitude

	def turn_left(self, dt, magnitude=1):
		self.direction = util.rotate_v(self.direction, -dt*self.turn_speed*magnitude)

	def turn_right(self, dt, magnitude=1):
		self.direction = util.rotate_v(self.direction, dt*self.turn_speed*magnitude)

	def fire(self):
		if self.last_fired > self.weapon.fire_rate:
			shot = copy.copy(self.weapon)
			shot.set_direction(self.direction)
			radius = max([self.graphic.get_width(), self.graphic.get_height()])*self.graphic_scale
			shot.set_position(self.position + self.direction*(radius+10))
			self.entities_to_add.append(shot)
			self.last_fired = 0
			shot.sound_player.play(shot.fire_sound, self.position)

	def collides(self, entity):
		return hasattr(entity, "bb") and self.bb.colliderect(entity.bb)

	def collided(self, entity):
		if type(entity) is Bullet:
			self.shield -= entity.attack_power

	def at_relative_position(self, entity, dt):
		if isinstance(entity, Ship):
			v = entity.position - self.position
			if v.get_magnitude() < self.forcefield_radius:
				entity.velocity += v*dt*self.forcefield_strength

	def detect_enemies(self, entities):
		self.last_detected = None
		min_dist = 99999
		for entity in entities:
			if entity != self and isinstance(entity, Ship) and entity.team != self.team:
				dist = (entity.position - self.position).get_magnitude()
				if dist < self.sensor_range and dist < min_dist:
					self.last_detected = entity
					min_dist = dist

	def update(self, dt, entities):
		self.position += dt*self.velocity
		self.update_bb()

		self.detect_enemies(entities)

		if self.shield < 0:
			self.sound_player.play(self.destroyed_sound, self.position)
			self.die = True
		
		if self.last_fired < 9999999:
			self.last_fired += dt

	def update_bb(self):
		a = util.angle_between_v(self.direction, self.graphic_direction)
		img = pygame.transform.rotozoom(self.graphic, a, self.graphic_scale)
		self.bb = img.get_rect()
		self.bb.x = self.position.x - img.get_width()/2
		self.bb.y = self.position.y - img.get_height()/2

	def render(self, surface, viewport):
		a = util.angle_between_v(self.direction, self.graphic_direction)
		img = pygame.transform.rotozoom(self.graphic, a, self.graphic_scale)
		pos = viewport.world2screen_coordinates(self.position)
		px = pos.x - img.get_width()/2
		py = pos.y - img.get_height()/2
		surface.blit(img, (px, py))

		if RENDER_BB:
			bb = viewport.world2screen_rect(self.bb)
			pygame.draw.rect(surface, (255, 255, 255), bb, 1) 

		if RENDER_FORCEFIELD:
			px = int(self.position.x)
			py = int(self.position.y)
			pygame.draw.circle(surface, (0, 0, 255), (px, py), self.forcefield_radius, 1) 

class TerranMothership(Ship):
	def __init__(self, params, entities_to_add):
		self.resources = params["resources"]
		self.blueprints = params["blueprints"]
		self.resource_growth_rate = 1000
		self.last_growth = 0
		self.mission = None
		self.spawn_sound = params["spawn_sound"]
		super(TerranMothership, self).__init__(params, entities_to_add)

	def spawn(self, index):
		blueprint = self.blueprints[index][0]
		if self.resources >= blueprint["resource_cost"]:
			self.sound_player.play(self.spawn_sound, self.position)

			self.resources -= blueprint["resource_cost"]

			ship = Ship(blueprint, self.entities_to_add)
			a = 2*random.random()*math.pi
			ship.position = self.position + Vector2(math.cos(a)*400, math.sin(a)*400)

			pilot_params = copy.copy(self.blueprints[index][1])
			pilot_params["ship"] = ship
			controller = FighterAIController(pilot_params)
			controller.set_mission(self.mission)

			self.entities_to_add.append(ship)
			self.entities_to_add.append(controller)

	def update(self, dt, entities):
		super(TerranMothership, self).update(dt, entities)

		self.last_growth += dt
		if self.last_growth > self.resource_growth_rate:
			self.resources += 1
			self.last_growth = 0

class AlienMothership(Ship):
	def __init__(self, params, entities_to_add):
		self.resources = params["resources"]
		self.blueprints = params["blueprints"]
		self.resource_growth_rate = 1000
		self.last_growth = 0
		self.mission = None
		self.spawn_sound = params["spawn_sound"]
		super(AlienMothership, self).__init__(params, entities_to_add)

	def move_left(self, dt):
		self.velocity += Vector2(-1,0)*dt*self.thrust

	def move_right(self, dt):
		self.velocity += Vector2(1,0)*dt*self.thrust

	def move_up(self, dt):
		self.velocity += Vector2(0,-1)*dt*self.thrust

	def move_down(self, dt):
		self.velocity += Vector2(0,1)*dt*self.thrust

	def spawn(self, index):
		blueprint = self.blueprints[index][0]
		if self.resources >= blueprint["resource_cost"]:
			self.sound_player.play(self.spawn_sound, self.position)

			self.resources -= blueprint["resource_cost"]

			ship = Ship(blueprint, self.entities_to_add)
			a = 2*random.random()*math.pi
			ship.position = self.position + Vector2(math.cos(a)*400, math.sin(a)*400)

			pilot_params = copy.copy(self.blueprints[index][1])
			pilot_params["ship"] = ship
			controller = FighterAIController(pilot_params)
			controller.set_mission(self.mission)

			self.entities_to_add.append(ship)
			self.entities_to_add.append(controller)

	def update(self, dt, entities):
		super(AlienMothership, self).update(dt, entities)

		self.last_growth += dt
		if self.last_growth > self.resource_growth_rate:
			self.resources += 1
			self.last_growth = 0

class Bullet(object):
	def __init__(self, params):
		self.position = Vector2()
		self.velocity = Vector2()
		self.radius = params["radius"]
		self.attack_power = params["attack_power"]
		self.ttl = params["ttl"]
		self.initial_speed = params["initial_speed"]
		self.fire_rate = params["fire_rate"]
		self.bb = Rect(0, 0, 2*self.radius, 2*self.radius)
		self.bb.center = self.position
		self.color = params["color"]
		self.fire_sound = params["fire_sound"]
		self.hit_sound = params["hit_sound"]
		self.sound_player = params["sound_player"]

	def set_position(self, position):
		self.position = position
		self.bb.center = self.position

	def set_direction(self, direction):
		self.velocity = self.initial_speed*direction

	def collides(self, entity):
		return hasattr(entity, "bb") and self.bb.colliderect(entity.bb)

	def collided(self, entity):
		if not isinstance(entity, Bullet):
			self.sound_player.play(self.hit_sound, self.position)
			self.die = True

	def update(self, dt, entities):
		self.position += dt*self.velocity
		self.bb = Rect(0, 0, 2*self.radius, 2*self.radius)
		self.bb.center = self.position
		self.ttl -= dt

		if self.ttl < 0:
			self.die = True

	def render(self, surface, viewport):
		pos = viewport.world2screen_coordinates(self.position)
		px = int(pos.x)
		py = int(pos.y)
		pygame.draw.circle(surface, self.color, (px, py), self.radius) 

		if RENDER_BB:
			bb = viewport.world2screen_rect(self.bb)
			pygame.draw.rect(surface, (255, 255, 255), bb, 1)

class GravityWell(object):
	def __init__(self, params):
		self.position = params["position"]
		self.strength = params["strength"]

	def update(self, dt, entities):
		for entity in entities:
			if hasattr(entity, "position") and hasattr(entity, "velocity"):
				e2w = self.position - entity.position
				entity.velocity += e2w.normalize()*self.strength/e2w.get_magnitude()**2

from controllers import FighterAIController
