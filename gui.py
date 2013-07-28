import pygame
from pygame import Rect

from objects import Ship, Mothership, Bullet

class Minimap(object):
	def __init__(self, params):
		self.map_size = params["map_size"]
		self.world_size = params["world_size"]
		self.screen_resolution = params["screen_resolution"]
		self.entities = []

	def project_position(self, position):
		return position*self.map_size/self.world_size

	def update(self, dt, entities):
		self.entities = entities

	def render(self, surface, viewport):
		w = int(self.map_size.x)
		h = int(self.map_size.y)
		minimap = pygame.Surface((w,h))
		minimap.fill((0,0,0))
		for entity in self.entities:
			if isinstance(entity, Ship):
				width = 1
				if isinstance(entity, Mothership):
					width = 3

				color = (255,0,0) if entity.team == "red" else (0,0,255)
				ppos = self.project_position(entity.position)
				px = int(ppos.x)
				py = int(ppos.y)
				pygame.draw.circle(minimap, color, (px, py), width)
			elif isinstance(entity, Bullet):
				ppos = self.project_position(entity.position)
				px = int(ppos.x)
				py = int(ppos.y)
				pygame.draw.circle(minimap, (255, 255, 0), (px, py), 1)
			elif isinstance(entity, Viewport):
				ppos = self.project_position(entity.position)
				ppost = (int(ppos.x), int(ppos.y))
				psize = self.project_position(self.screen_resolution)
				psizet = (int(psize.x), int(psize.y))
				pygame.draw.rect(minimap, (255,255,255), Rect(ppost, psizet), 1) 

		surface.blit(minimap, (0, self.screen_resolution.y - self.map_size.y))

class Viewport:
	def __init__(self, params):
		self.position = params["position"]
		self.panning_speed = params["panning_speed"]
		self.screen_resolution = params["screen_resolution"]
		self.pan_border_width = params["pan_border_width"]

	def get_coordinates(self, position):
		return position - self.position

	def update(self, dt, entities):
		mp = pygame.mouse.get_pos()

		if mp[0] > self.screen_resolution.x - self.pan_border_width:
			self.position.x += self.panning_speed
		if mp[0] < self.pan_border_width:
			self.position.x -= self.panning_speed 
		if mp[1] > self.screen_resolution.y - self.pan_border_width:
			self.position.y += self.panning_speed
		if mp[1] < self.pan_border_width:
			self.position.y -= self.panning_speed


