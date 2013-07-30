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
SCREEN_RESOLUTION = (1920, 1200)
SCREEN_RESOLUTION_V = Vector2(SCREEN_RESOLUTION)
SCREEN_RECT = Rect((0,0), SCREEN_RESOLUTION)
WORLD_RECT = Rect(0, 0, 5000, 5000)
SHOW_FPS = True

# General initialization
pygame.mixer.pre_init(44100, -16, 2, 2048)
pygame.init()
flags = FULLSCREEN | DOUBLEBUF
window = pygame.display.set_mode(SCREEN_RESOLUTION, flags)
pygame.event.set_allowed([QUIT, KEYDOWN, MOUSEBUTTONDOWN])
screen = pygame.display.get_surface()
clock = pygame.time.Clock()
entities_to_add = []
entities = []

# Sprites
graphics = {
	"splash" : pygame.image.load("content/splash.png").convert_alpha(),
	"background" : pygame.image.load("content/bg.png").convert_alpha(),
	"alien_fighter" : pygame.image.load("content/smallship.png").convert_alpha(),
	"alien_battlecruiser" : pygame.image.load("content/aliencruiser.png").convert_alpha(),
	"alien_battleship" : pygame.image.load("content/alienbattleship.png").convert_alpha(),
	"alien_mothership" : pygame.image.load("content/mother.png").convert_alpha(),
	"terran_fighter" : pygame.image.load("content/humansmallship.png").convert_alpha(),
	"terran_battlecruiser" : pygame.image.load("content/terrancruiser.png").convert_alpha(),
	"terran_battleship" : pygame.image.load("content/terranbattleship.png").convert_alpha(),
	"terran_mothership" : pygame.image.load("content/terranmother.png").convert_alpha()
}

graphics_direction = {
	"alien_fighter" : Vector2(1,0),
	"alien_battlecruiser" : Vector2(-1,0),
	"alien_battleship" : Vector2(1,0),
	"alien_mothership" : Vector2(0,-1),
	"terran_fighter" : Vector2(-1,0),
	"terran_battlecruiser" : Vector2(-1,0),
	"terran_battleship" : Vector2(1,0),
	"terran_mothership" : Vector2(1,0)
}

# Viewport
viewport_params = {
	"position" : Vector2(1000 - SCREEN_RESOLUTION[0]/2, 1000 - SCREEN_RESOLUTION[1]/2),
	"panning_speed" : 50,
	"screen_resolution" : SCREEN_RESOLUTION_V,
	"pan_border_width" : 10,
	"world_rect" : WORLD_RECT
}
viewport = Viewport(viewport_params)
entities.append(viewport)

# Sound and music
sound_effects = {
	"light_blast" : pygame.mixer.Sound("content/light_blast.wav"),		
	"medium_blast" : pygame.mixer.Sound("content/medium_blast.wav"),		
	"heavy_blast" : pygame.mixer.Sound("content/heavy_blast.wav"),	
	"spawn" : pygame.mixer.Sound("content/spawn.wav"),
	"blast_hit" : pygame.mixer.Sound("content/blast_hit.wav"),
	"destroyed" : pygame.mixer.Sound("content/destroyed.wav")
}

sound_player = SoundPlayer(sound_effects, viewport)


# Weapons
light_blast_params = {
	"radius" : 2,
	"attack_power" : 1,
	"ttl" : 1000,
	"initial_speed" : 1,
	"fire_rate" : 250,
	"color" : (255,255,0),
	"fire_sound" : "light_blast",
	"hit_sound" : "blast_hit",
	"sound_player" : sound_player
}
light_blast = Bullet(light_blast_params)

medium_blast_params = {
	"radius" : 4,
	"attack_power" : 10,
	"ttl" : 5000,
	"initial_speed" : 2,
	"fire_rate" : 500,
	"color" : (255,0,255),
	"fire_sound" : "medium_blast",
	"hit_sound" : "blast_hit",
	"sound_player" : sound_player
}
medium_blast = Bullet(medium_blast_params)

heavy_blast_params = {
	"radius" : 6,
	"attack_power" : 50,
	"ttl" : 10000,
	"initial_speed" : 0.1,
	"fire_rate" : 3000,
	"color" : (255,0,0),
	"fire_sound" : "heavy_blast",
	"hit_sound" : "blast_hit",
	"sound_player" : sound_player
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
	"entities_to_add" : entities_to_add,
	"destroyed_sound" : "destroyed",
	"sound_player" : sound_player
}

# Battlecruiser
battlecruiser_params = {
	"position" : Vector2(),
	"direction" : Vector2(0, 1),
	"thrust" : 0.00001,
	"max_speed" : 20,
	"turn_speed" : 0.1*math.pi/180,
	"shield" : 200,
	"sensor_range" : 1000,
	"forcefield_radius" : 100,
	"forcefield_strength" : 0.00005,
	"weapon" : medium_blast,
	"resource_cost" : 50,
	"entities_to_add" : entities_to_add,
	"destroyed_sound" : "destroyed",
	"sound_player" : sound_player
}

# Battleship
battleship_params = {
	"position" : Vector2(),
	"direction" : Vector2(0, 1),
	"thrust" : 0.00001,
	"max_speed" : 20,
	"turn_speed" : 0.05*math.pi/180,
	"shield" : 500,
	"sensor_range" : 1500,
	"forcefield_radius" : 100,
	"forcefield_strength" : 0.0001,
	"weapon" : heavy_blast,
	"resource_cost" : 100,
	"entities_to_add" : entities_to_add,
	"destroyed_sound" : "destroyed",
	"sound_player" : sound_player
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

alien_battleship_blueprint = copy.copy(battleship_params)
alien_battleship_blueprint["team"] = "red"
alien_battleship_blueprint["graphic"] = graphics["alien_battleship"]
alien_battleship_blueprint["graphic_direction"] = graphics_direction["alien_battleship"]
alien_battleship_blueprint["graphic_scale"] = 1
alien_battleship_blueprint["name"] = "alien_battleship"

alien_controller_params = {
	"cruise_speed" : 0.0002,
	"world_rect" : WORLD_RECT
}

alien_blueprints = []
alien_blueprints.append((alien_fighter_blueprint, alien_controller_params))
alien_blueprints.append((alien_battlecruiser_blueprint, alien_controller_params))
alien_blueprints.append((alien_battleship_blueprint, alien_controller_params))

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
	"name" : "alien_mothership",
	"spawn_sound" : "spawn",
	"destroyed_sound" : "destroyed",
	"sound_player" : sound_player
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

terran_battleship_blueprint = copy.copy(battleship_params)
terran_battleship_blueprint["team"] = "blue"
terran_battleship_blueprint["graphic"] = graphics["terran_battleship"]
terran_battleship_blueprint["graphic_direction"] = graphics_direction["terran_battleship"]
terran_battleship_blueprint["graphic_scale"] = 1
terran_battleship_blueprint["name"] = "terran_battleship"

terran_controller_params = {
	"cruise_speed" : 0.5,
	"world_rect" : WORLD_RECT
}

terran_blueprints = []
terran_blueprints.append((terran_fighter_blueprint, terran_controller_params))
terran_blueprints.append((terran_battlecruiser_blueprint, terran_controller_params))
terran_blueprints.append((terran_battleship_blueprint, terran_controller_params))

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
	"name" : "terran_mothership",
	"spawn_sound" : "spawn",
	"destroyed_sound" : "destroyed",
	"sound_player" : sound_player
}
terran_mothership = TerranMothership(terran_mothership_params, entities_to_add)

terran_mothership_controller_params = {
	"ship" : terran_mothership,
	"cruise_speed" : 0.5,
	"world_rect" : WORLD_RECT
}
terran_mothership_controller = TerranMothershipAIController(terran_mothership_controller_params)

entities.append(terran_mothership)
entities.append(terran_mothership_controller)

# Gravity wells
for i in range(4):
	pos = Vector2(random.random(), random.random()) * Vector2(WORLD_RECT.size)
	well_params = {
		"position" : pos,
		"strength" : 0.0003
	}

	well = GravityWell(well_params)
	entities.append(well)

# Player stats
stats = PlayerStats(alien_mothership)
entities.append(stats)

# MissionSelector
ms = MissionSelector(viewport, alien_mothership)
entities.append(ms)

# Minimap
minimap_params = {
	"map_size" : Vector2(200, 200),
	"world_size" : Vector2(WORLD_RECT.width, WORLD_RECT.height),
	"screen_resolution" : SCREEN_RESOLUTION_V,
	"viewport" : viewport
}
entities.append(Minimap(minimap_params))



# Spawn bar
sb = SpawnBar(alien_mothership)
entities.append(sb)

# Ship stats
ss = ShipStats(viewport)
entities.append(ss)

# FPS
dd = DebugData(clock)
entities.append(dd)

# Splash screen
pygame.mixer.music.load("content/splash.mp3")
pygame.mixer.music.play(-1)

run = True
while run:
	for event in pygame.event.get():
		if event.type == MOUSEBUTTONDOWN or event.type == KEYDOWN:
			run = False

	screen.blit(graphics["splash"], (0,0))
	pygame.display.flip()

# Main game loop
pygame.mixer.music.load("content/background.mp3")
pygame.mixer.music.play(-1)

win = True
run = True
while True:
	dt = clock.tick(50)

	# Event handling
	for event in pygame.event.get():
		for entity in entities:
			if hasattr(entity, "handle_event"):
				entity.handle_event(event)
				continue

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
			if hasattr(entity, "bb"):
				if entity.bb.colliderect(viewport.rect):
					entity.render(screen, viewport)
			else:
				entity.render(screen, viewport)

	for entity in entities:
		if hasattr(entity, "render") and hasattr(entity, "gui"):
			entity.render(screen, viewport)

	if not run:
		font = pygame.font.SysFont("monospace", 72, bold=True)
		text = "You win!"
		if not win:
			pygame.mixer.music.load("content/defeat.mp3")
			pygame.mixer.music.play()
			text = "You lose!"
		else:
			pygame.mixer.music.load("content/victory.mp3")
			pygame.mixer.music.play()

		label = font.render(text, 1, (255, 255, 255))
		screen.blit(label, (SCREEN_RESOLUTION[0]/2 - label.get_rect().width/2, SCREEN_RESOLUTION[1]/2 - label.get_rect().height/2))
		pygame.display.flip()

		while True:
			for event in pygame.event.get():
				if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
					sys.exit(0)

	pygame.display.flip()

