import math
import copy
import random
import sys

import pygame
from pygame import Rect
from pygame.locals import *

from gameobjects.vector2 import Vector2

from objects import *
from controllers import *
from gui import *

# Global parameters
SCREEN_RESOLUTION = (1024, 768)
SCREEN_RESOLUTION_V = Vector2(1024, 768)
SCREEN_RECT = Rect((0,0), SCREEN_RESOLUTION)
WORLD_RECT = Rect(0, 0, 5000, 5000)

# General initialization
pygame.init()
window = pygame.display.set_mode(SCREEN_RESOLUTION)
screen = pygame.display.get_surface()
clock = pygame.time.Clock()
entities_to_add = []
entities = []

# Sprites
graphics = {
	"background" : pygame.image.load("/home/dementati/Downloads/bg1024x768.png"),
	"alien_fighter" : pygame.image.load("/home/dementati/Downloads/smallship.png"),
	"alien_battlecruiser" : pygame.image.load("/home/dementati/Downloads/aliencruiser.png"),
	"alien_mothership" : pygame.image.load("/home/dementati/Downloads/mother.png"),
	"terran_fighter" : pygame.image.load("/home/dementati/Downloads/humansmallship.png"),
	"terran_battlecruiser" : pygame.image.load("/home/dementati/Downloads/terrancruiser.png"),
	"terran_mothership" : pygame.image.load("/home/dementati/Downloads/mothership.png")
}

graphics_direction = {
	"alien_fighter" : Vector2(1,0),
	"alien_battlecruiser" : Vector2(-1,0),
	"alien_mothership" : Vector2(0,-1),
	"terran_fighter" : Vector2(-1,0),
	"terran_battlecruiser" : Vector2(-1,0),
	"terran_mothership" : Vector2(-1,0)
}

# Weapons
light_blast_params = {
	"radius" : 2,
	"attack_power" : 1,
	"ttl" : 1000,
	"initial_speed" : 1,
	"fire_rate" : 250,
	"color" : (255,255,0)
}
light_blast = Bullet(light_blast_params)

medium_blast_params = {
	"radius" : 4,
	"attack_power" : 10,
	"ttl" : 5000,
	"initial_speed" : 2,
	"fire_rate" : 500,
	"color" : (255,0,255)
}
medium_blast = Bullet(medium_blast_params)

heavy_blast_params = {
	"radius" : 6,
	"attack_power" : 50,
	"ttl" : 10000,
	"initial_speed" : 0.1,
	"fire_rate" : 3000,
	"color" : (255,0,0)
}
heavy_blast = Bullet(heavy_blast_params)

# Fighter
fighter_params = {
	"position" : Vector2(),
	"direction" : Vector2(0, 1),
	"thrust" : 0.0001,
	"max_speed" : 20,
	"turn_speed" : 0.1*math.pi/180,
	"fire_rate" : 250,
	"shield" : 10,
	"sensor_range" : 1000,
	"forcefield_radius" : 50,
	"forcefield_strength" : 0.00001,
	"weapon" : light_blast,
	"resource_cost" : 10,
	"entities_to_add" : entities_to_add
}

# Battlecruiser
battlecruiser_params = {
	"position" : Vector2(),
	"direction" : Vector2(0, 1),
	"thrust" : 0.00005,
	"max_speed" : 20,
	"turn_speed" : 0.1*math.pi/180,
	"shield" : 100,
	"sensor_range" : 1000,
	"forcefield_radius" : 100,
	"forcefield_strength" : 0.00001,
	"weapon" : medium_blast,
	"resource_cost" : 50,
	"entities_to_add" : entities_to_add
}

# Alien mothership
alien_fighter_blueprint = copy.copy(fighter_params)
alien_fighter_blueprint["team"] = "red"
alien_fighter_blueprint["graphic"] = graphics["alien_fighter"]
alien_fighter_blueprint["graphic_direction"] = graphics_direction["alien_fighter"]
alien_fighter_blueprint["graphic_scale"] = 1
alien_fighter_blueprint["name"] = "alien_fighter"

alien_battlecruiser_blueprint = copy.copy(battlecruiser_params)
alien_battlecruiser_blueprint["team"] = "red"
alien_battlecruiser_blueprint["graphic"] = graphics["alien_battlecruiser"]
alien_battlecruiser_blueprint["graphic_direction"] = graphics_direction["alien_battlecruiser"]
alien_battlecruiser_blueprint["graphic_scale"] = 1
alien_battlecruiser_blueprint["name"] = "alien_battlecruiser"

alien_controller_params = {
	"cruise_speed" : 0.0002,
	"world_rect" : WORLD_RECT
}

alien_blueprints = []
alien_blueprints.append((alien_fighter_blueprint, alien_controller_params))
alien_blueprints.append((alien_battlecruiser_blueprint, alien_controller_params))

alien_mothership_params = {
	"position" : Vector2(1000, 1000),
	"direction" : Vector2(-1, 0),
	"length" : 10,
	"team" : "red",
	"thrust" : 0.00001,
	"max_speed" : 5,
	"turn_speed" : 0.01*math.pi/180,
	"fire_rate" : 250,
	"shield" : 1000,
	"attack_power" : 10,
	"sensor_range" : 600,
	"forcefield_radius" : 200,
	"forcefield_strength" : 0.00001,		
	"graphic" : graphics["alien_mothership"],
	"graphic_direction" : graphics_direction["alien_mothership"],
	"graphic_scale" : 0.5,
	"resources" : 100,
	"weapon" : None,
	"blueprints" : alien_blueprints,
	"resource_cost" : 9999,
	"name" : "alien_mothership"
}

alien_mothership = AlienMothership(alien_mothership_params, entities_to_add)

alien_mothership_controller_params = {
	"ship" : alien_mothership,
	"world_rect" : WORLD_RECT
}

alien_mothership_controller = AlienMothershipPlayerController(alien_mothership_controller_params)
entities.append(alien_mothership)
entities.append(alien_mothership_controller)

# Terran mothership
terran_fighter_blueprint = copy.copy(fighter_params)
terran_fighter_blueprint["team"] = "blue"
terran_fighter_blueprint["graphic"] = graphics["terran_fighter"]
terran_fighter_blueprint["graphic_direction"] = graphics_direction["terran_fighter"]
terran_fighter_blueprint["graphic_scale"] = 1
terran_fighter_blueprint["name"] = "terran_fighter"

terran_battlecruiser_blueprint = copy.copy(battlecruiser_params)
terran_battlecruiser_blueprint["team"] = "blue"
terran_battlecruiser_blueprint["graphic"] = graphics["terran_battlecruiser"]
terran_battlecruiser_blueprint["graphic_direction"] = graphics_direction["terran_battlecruiser"]
terran_battlecruiser_blueprint["graphic_scale"] = 1
terran_battlecruiser_blueprint["name"] = "terran_battlecruiser"

terran_controller_params = {
	"cruise_speed" : 0.5,
	"world_rect" : WORLD_RECT
}

terran_blueprints = []
terran_blueprints.append((terran_fighter_blueprint, terran_controller_params))
terran_blueprints.append((terran_battlecruiser_blueprint, terran_controller_params))

terran_mothership_params = {
	"position" : Vector2(4000, 4000),
	"direction" : Vector2(-1, 0),
	"length" : 10,
	"team" : "blue",
	"thrust" : 0.00001,
	"max_speed" : 5,
	"turn_speed" : 0.01*math.pi/180,
	"shield" : 1000,
	"sensor_range" : 600,
	"forcefield_radius" : 200,
	"forcefield_strength" : 0.00001,		
	"graphic" : graphics["terran_mothership"],
	"graphic_direction" : graphics_direction["terran_mothership"],
	"graphic_scale" : 0.5,
	"resources" : 100,
	"weapon" : None,
	"blueprints" : terran_blueprints,
	"resource_cost" : 9999,
	"name" : "terran_mothership"
}
terran_mothership = TerranMothership(terran_mothership_params, entities_to_add)

terran_mothership_controller_params = {
	"ship" : terran_mothership,
	"world_rect" : WORLD_RECT
}
terran_mothership_controller = TerranMothershipAIController(terran_mothership_controller_params)

entities.append(terran_mothership)
entities.append(terran_mothership_controller)

# Add test fighters
for i in range(0):
	params = copy.copy(fighterParams)
	params["position"] = Vector2(random.randint(0, WORLD_RECT.width), random.randint(0, WORLD_RECT.height))
	
	params["team"] = "blue"
	params["graphic"] = graphics["terran_fighter"]
	params["graphic_direction"] = graphics_direction["terran_fighter"]
	params["graphic_scale"] = 0.1

	ship = Ship(params, entities_to_add)

	controller_params = {
		"ship" : ship,
		"cruise_speed" : 0.5,
		"world_rect" : WORLD_RECT
	}

	controller = FighterAIController(controller_params)
	entities.append(ship)
	entities.append(controller)

# Minimap
minimap_params = {
	"map_size" : Vector2(200, 200),
	"world_size" : Vector2(WORLD_RECT.width, WORLD_RECT.height),
	"screen_resolution" : SCREEN_RESOLUTION_V
}
entities.append(Minimap(minimap_params))

# Player stats
stats = PlayerStats(alien_mothership)
entities.append(stats)

# Viewport
viewport_params = {
	"position" : Vector2(1000 - SCREEN_RESOLUTION[0]/2, 1000 - SCREEN_RESOLUTION[1]/2),
	"panning_speed" : 50,
	"screen_resolution" : SCREEN_RESOLUTION_V,
	"pan_border_width" : 70,
	"world_rect" : WORLD_RECT
}
viewport = Viewport(viewport_params)
entities.append(viewport)

# MissionSelector
ms = MissionSelector(viewport, alien_mothership)
entities.append(ms)

# Spawn bar
sb = SpawnBar(alien_mothership)
entities.append(sb)

# Main game loop
win = True
run = True
while True:
	dt = clock.tick(50)

	# Event handling
	for event in pygame.event.get():
		for entity in entities:
			if hasattr(entity, "handle_event"):
				entity.handle_event(event)

		if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
			sys.exit(0)

	# Update 
	for entity in entities:
		if hasattr(entity, "update"):
			entity.update(dt, entities)

	# Collision detection
	for entity1 in entities:
		for entity2 in entities:
			if entity1 != entity2:
				if hasattr(entity1, "collides") and entity1.collides(entity2):
					entity1.collided(entity2)
				
				if hasattr(entity1, "at_relative_position") and hasattr(entity2, "position"):
					dist = (entity1.position - entity2.position).get_magnitude()
					entity1.at_relative_position(entity2, dt)

	# Update entity list
	entities.extend(entities_to_add)
	del entities_to_add[:]

	for entity in entities:
		if hasattr(entity, 'die'):
			if isinstance(entity, Ship):
				if entity.name == "terran_fighter":
					alien_mothership.resources += terran_fighter_blueprint["resource_cost"]
				elif entity.name == "terran_battlecruiser":
					alien_mothership.resources += terran_battlecruiser_blueprint["resource_cost"]
				elif entity.name == "alien_fighter":
					terran_mothership.resources += alien_fighter_blueprint["resource_cost"]
				elif entity.name == "alien_battlecruiser":
					terran_mothership.resources += alien_battlecruiser_blueprint["resource_cost"]
				elif entity.name == "terran_mothership":
					win = True
					run = False
				elif entity.name == "alien_mothership":
					win = False
					run = False


	entities = [e for e in entities if not hasattr(e, 'die')]

	# Render
	screen.blit(graphics["background"], (0, 0))
	for entity in entities:
		if hasattr(entity, "render") and not hasattr(entity, "gui"):
			entity.render(screen, viewport)

	for entity in entities:
		if hasattr(entity, "render") and hasattr(entity, "gui"):
			entity.render(screen, viewport)

	if not run:
		font = pygame.font.SysFont("monospace", 72, bold=True)
		text = "You win!"
		if not win:
			text = "You lose!"
		label = font.render(text, 1, (255, 255, 255))
		screen.blit(label, (SCREEN_RESOLUTION[0]/2 - label.get_rect().width/2, SCREEN_RESOLUTION[1]/2 - label.get_rect().height/2))
		pygame.display.flip()

		while True:
			for event in pygame.event.get():
				if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
					sys.exit(0)

	pygame.display.flip()

