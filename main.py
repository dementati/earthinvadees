import math
import copy
import random

import pygame
from pygame import Rect
from pygame.locals import *

from gameobjects.vector2 import Vector2

from objects import *
from controllers import *
from gui import *

SCREEN_RESOLUTION = (1024, 768)
SCREEN_RESOLUTION_V = Vector2(1024, 768)
SCREEN_RECT = Rect((0,0), SCREEN_RESOLUTION)
WORLD_RECT = Rect(0, 0, 5000, 5000)

window = pygame.display.set_mode(SCREEN_RESOLUTION)
screen = pygame.display.get_surface()

background = pygame.image.load("/home/dementati/Downloads/bg1024x768.png")

clock = pygame.time.Clock()

entities_to_add = []

bullet_params = {
	"radius" : 3,
	"attack_power" : 1,
	"ttl" : 1000,
	"initial_speed" : 1,
	"fire_rate" : 250
}
bullet = Bullet(bullet_params)

fighterParams = {
	"position" : Vector2(100, 100),
	"direction" : Vector2(0, 1),
	"length" : 10,
	"team" : "red",
	"thrust" : 0.0001,
	"max_speed" : 20,
	"turn_speed" : 0.1*math.pi/180,
	"fire_rate" : 250,
	"shield" : 1000,
	"attack_power" : 1,
	"sensor_range" : 600,
	"forcefield_radius" : 50,
	"forcefield_strength" : 0.00001,
	"weapon" : bullet,
	"resource_cost" : 10,
	"entities_to_add" : entities_to_add
}

ship_blueprint = copy.deepcopy(fighterParams)
ship_blueprint["team"] = "red"
ship_blueprint["graphic"] = pygame.image.load("/home/dementati/Downloads/smallship.png")
ship_blueprint["graphic_direction"] = Vector2(1, 0)
ship_blueprint["graphic_scale"] = 1

pilot_params = {
	"cruise_speed" : 0.5,
	"world_rect" : WORLD_RECT
}

mothershipParams = {
	"position" : Vector2(2500, 2500),
	"direction" : Vector2(-1, 0),
	"length" : 10,
	"team" : "red",
	"thrust" : 0.00001,
	"max_speed" : 5,
	"turn_speed" : 0.01*math.pi/180,
	"fire_rate" : 250,
	"shield" : 10000,
	"attack_power" : 10,
	"sensor_range" : 600,
	"forcefield_radius" : 200,
	"forcefield_strength" : 0.00001,		
	"graphic" : pygame.image.load("/home/dementati/Downloads/mother.png"),
	"graphic_direction" : Vector2(-1, 0),
	"graphic_scale" : 0.5,
	"resources" : 100,
	"weapon" : None,
	"blueprints" : [(ship_blueprint, pilot_params)],
	"resource_cost" : 9999
}

entities = []

mothership = Mothership(mothershipParams, entities_to_add)

mothership_controller_params = {
	"ship" : mothership,
	"world_rect" : WORLD_RECT
}

controller = MothershipPlayerController(mothership_controller_params)

entities.append(mothership)
entities.append(controller)

for i in range(20):
	params = copy.deepcopy(fighterParams)
	params["position"] = Vector2(random.randint(0, WORLD_RECT.width), random.randint(0, WORLD_RECT.height))
	
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

	controller_params = {
		"ship" : ship,
		"cruise_speed" : 0.5,
		"world_rect" : WORLD_RECT
	}

	controller = AIShipController(controller_params)
	entities.append(ship)
	entities.append(controller)

minimap_params = {
	"map_size" : Vector2(200, 200),
	"world_size" : Vector2(WORLD_RECT.width, WORLD_RECT.height),
	"screen_resolution" : SCREEN_RESOLUTION_V
}
entities.append(Minimap(minimap_params))

viewport_params = {
	"position" : Vector2(100, 100),
	"panning_speed" : 50,
	"screen_resolution" : SCREEN_RESOLUTION_V,
	"pan_border_width" : 100
}
viewport = Viewport(viewport_params)
entities.append(viewport)

while True:
	dt = clock.tick(50)

	# Update
	for event in pygame.event.get():
		for entity in entities:
			if hasattr(entity, "handle_event"):
				entity.handle_event(event)

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
			entity.render(screen, viewport)

	pygame.display.flip()

