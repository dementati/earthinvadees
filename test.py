import pygame
from pygame.locals import *
from pygame import Rect
from gameobjects.vector2 import Vector2
from gameobjects.vector3 import Vector3
from gameobjects.util import pi
import math
import copy
import random

import util

RESOLUTION = (1024, 768)
SCREEN_RECT = Rect((0,0), RESOLUTION)
BULLET_INITIAL_VELOCITY = 1
RENDER_BB = False 
RENDER_FORCEFIELD = False
WORLD_RECT = Rect(-RESOLUTION[0]*4, -RESOLUTION[1]*4, RESOLUTION[0]*5, RESOLUTION[1]*5)

window = pygame.display.set_mode(RESOLUTION)
screen = pygame.display.get_surface()

background = pygame.image.load("/home/dementati/Downloads/background.jpg")

class Ship(object):
	def __init__(self, params, entities):
		self.position = params["position"]
		self.direction = params["direction"]
		self.length = params["length"]
		self.team = params["team"]
		self.thrust = params["thrust"]
		self.max_speed = params["max_speed"]
		self.turn_speed = params["turn_speed"]
		self.fire_rate = params["fire_rate"]
		self.shield = params["shield"]
		self.attack_power = params["attack_power"]
		self.sensor_range = params["sensor_range"]
		self.forcefield_radius = params["forcefield_radius"]
		self.forcefield_strength = params["forcefield_strength"]
		self.graphic = params["graphic"]
		self.graphic_direction = params["graphic_direction"]
		self.graphic_scale = params["graphic_scale"]
		self.bb = Rect(0,0,0,0)
		self.last_fired = 0
		self.entities = entities
		self.velocity = Vector2()
		self.last_detected = None

		if self.team == "blue":
			self.color = Vector3(0, 0, 255)
		elif self.team == "red":
			self.color = Vector3(255, 0, 0)

	def accelerate(self, dt):
		self.velocity += dt*self.thrust*self.direction

	def decelerate(self, dt):
		self.velocity -= dt*self.thrust*self.direction

	def turn_left(self, dt):
		self.direction = util.rotate_v(self.direction, -dt*self.turn_speed)

	def turn_right(self, dt):
		self.direction = util.rotate_v(self.direction, dt*self.turn_speed)

	def fire(self):
		if self.last_fired > self.fire_rate:
			v = BULLET_INITIAL_VELOCITY*self.direction
			self.entities.append(Bullet(self.position.copy() + self.direction*30, v, 3, self.attack_power, 1000))
			self.last_fired = 0

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
			self.die = True
		
		if self.last_fired < 9999999:
			self.last_fired += dt

	def update_bb(self):
		a = util.angle_between_v(self.direction, self.graphic_direction)
		img = pygame.transform.rotozoom(self.graphic, a, self.graphic_scale)
		self.bb = img.get_rect()
		self.bb.x = self.position.x - img.get_width()/2
		self.bb.y = self.position.y - img.get_height()/2

	def render(self, surface):
		a = util.angle_between_v(self.direction, self.graphic_direction)
		img = pygame.transform.rotozoom(self.graphic, a, self.graphic_scale)
		px = self.position.x - img.get_width()/2
		py = self.position.y - img.get_height()/2
		surface.blit(img, (px, py))

		if RENDER_BB:
			pygame.draw.rect(surface, (255, 255, 255), self.bb, 1) 

		if RENDER_FORCEFIELD:
			px = int(self.position.x)
			py = int(self.position.y)
			pygame.draw.circle(surface, (0, 0, 255), (px, py), self.forcefield_radius, 1) 

class Bullet(object):
	def __init__(self, position, velocity, radius, attack_power, ttl):
		self.position = position
		self.velocity = velocity
		self.radius = radius
		self.attack_power = attack_power
		self.ttl = ttl
		self.bb = Rect(0, 0, 2*radius, 2*radius)
		self.bb.center = self.position

	def collides(self, entity):
		return hasattr(entity, "bb") and self.bb.colliderect(entity.bb)

	def collided(self, entity):
		self.die = True

	def update(self, dt, entities):
		self.position += dt*self.velocity
		self.bb.center = self.position
		self.ttl -= dt
		
		if self.ttl < 0:
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
		if not SCREEN_RECT.colliderect(self.ship.bb):
			self.head_for(Vector2(SCREEN_RECT.center))
		else:
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
	def __init__(self, ship, cruise_speed):
		self.ship = ship
		self.target = None
		self.cruise_speed = cruise_speed

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
		if not WORLD_RECT.colliderect(self.ship.bb):
			self.head_for(dt, Vector2(SCREEN_RECT.center))
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

	def update(self, dt, entities):
		self.position = pygame.mouse.get_pos()

class Minimap(object):
	def __init__(self, map_size, world_size):
		self.map_size = map_size
		self.world_size = world_size
		self.entities = []

	def project_position(self, position):
		W = self.world_size.x
		H = self.world_size.y
		w = RESOLUTION[0]
		h = RESOLUTION[1]
		return self.map_size*(position + Vector2(W/2 - w/2,H/2 - h/2))/Vector2(W,H)

	def update(self, dt, entities):
		self.entities = entities

	def render(self, surface):
		w = int(self.map_size.x)
		h = int(self.map_size.y)
		minimap = pygame.Surface((w,h))
		minimap.fill((0,0,0))
		for entity in self.entities:
			if isinstance(entity, Ship):
				color = (255,0,0) if entity.team == "red" else (0,0,255)
				ppos = self.project_position(entity.position)
				px = int(ppos.x)
				py = int(ppos.y)
				pygame.draw.circle(minimap, color, (px, py), 2)
			elif isinstance(entity, Bullet):
				ppos = self.project_position(entity.position)
				px = int(ppos.x)
				py = int(ppos.y)
				pygame.draw.circle(minimap, (255, 255, 0), (px, py), 1)

		surface.blit(minimap, (0, RESOLUTION[1] - self.map_size.y))

clock = pygame.time.Clock()

entities_to_add = []

fighterParams = {
	"position" : Vector2(100, 100),
	"direction" : Vector2(0, 1),
	"length" : 10,
	"team" : "red",
	"thrust" : 0.0001,
	"max_speed" : 20,
	"turn_speed" : 0.1*pi/180,
	"fire_rate" : 250,
	"shield" : 1000,
	"attack_power" : 1,
	"sensor_range" : 600,
	"forcefield_radius" : 50,
	"forcefield_strength" : 0.00001
}

mothershipParams = {
	"position" : Vector2(400, 400),
	"direction" : Vector2(-1, 0),
	"length" : 10,
	"team" : "red",
	"thrust" : 0.00001,
	"max_speed" : 5,
	"turn_speed" : 0.01*pi/180,
	"fire_rate" : 250,
	"shield" : 10000,
	"attack_power" : 10,
	"sensor_range" : 600,
	"forcefield_radius" : 200,
	"forcefield_strength" : 0.00001,		
	"graphic" : pygame.image.load("/home/dementati/Downloads/mothership.png"),
	"graphic_direction" : Vector2(-1, 0),
	"graphic_scale" : 0.5
}


entities = []

mothership = Ship(mothershipParams, entities)
controller = PlayerController(mothership)
entities.append(mothership)
entities.append(controller)

for i in range(10):
	params = copy.deepcopy(fighterParams)
	params["position"] = Vector2(random.randint(0, RESOLUTION[0]), random.randint(0, RESOLUTION[1]))
	
	if i % 2 == 0:
		params["team"] = "red" 
		params["graphic"] = pygame.image.load("/home/dementati/Downloads/smallship.png")
		params["graphic_direction"] = Vector2(1, 0)
		params["graphic_scale"] = 1
	else:
		params["team"] = "blue"
		params["graphic"] = pygame.image.load("/home/dementati/Downloads/fighter2.png")
		params["graphic_direction"] = Vector2(0, 1)
		params["graphic_scale"] = 0.1

	ship = Ship(params, entities_to_add)
	controller = AIShipController(ship, 0.5)
	entities.append(ship)
	entities.append(controller)

entities.append(Minimap(Vector2(200, 200), Vector2(WORLD_RECT.width, WORLD_RECT.height)))

while True:
	dt = clock.tick(50)

	# Update
	for event in pygame.event.get():
		if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
			sys.exit(0)

	for entity in entities:
		if hasattr(entity, "update"):
			entity.update(dt, entities)

	for entity1 in entities:
		for entity2 in entities:
			if entity1 != entity2:
				if hasattr(entity1, "collides") and entity1.collides(entity2):
					entity1.collided(entity2)
				
				if hasattr(entity1, "at_relative_position") and hasattr(entity2, "position"):
					dist = (entity1.position - entity2.position).get_magnitude()
					entity1.at_relative_position(entity2, dt)

	entities.extend(entities_to_add)
	del entities_to_add[:]

	entities = [e for e in entities if not hasattr(e, 'die')]

	# Render
	screen.blit(background, (0, 0))
	for entity in entities:
		if hasattr(entity, "render"):
			entity.render(screen)

	pygame.display.flip()

