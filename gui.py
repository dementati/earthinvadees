import pygame
from pygame import Rect
from pygame.locals import *

from objects import *

class Minimap(object):
	def __init__(self, params):
		self.map_size = params["map_size"]
		self.world_size = params["world_size"]
		self.screen_resolution = params["screen_resolution"]
		self.entities = []
		self.gui = True

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
				if isinstance(entity, AlienMothership) or isinstance(entity, TerranMothership):
					width = 5

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
		r = minimap.get_rect()
		r.topleft = (0, self.screen_resolution.y - self.map_size.y) 
		pygame.draw.rect(surface, (0, 255, 0), r, 1)

class Viewport:
	def __init__(self, params):
		self.position = params["position"]
		self.panning_speed = params["panning_speed"]
		self.screen_resolution = params["screen_resolution"]
		self.pan_border_width = params["pan_border_width"]
		self.world_rect = params["world_rect"]

	def world2screen_coordinates(self, position):
		return position - self.position

	def world2screen_rect(self, rect):
		tl = Vector2(rect.topleft)
		wc = self.world2screen_coordinates(tl)
		wct = util.v2i_tuple(wc)
		return Rect(wct, rect.size)

	def screen2world_coordinates(self, position):
		return position + self.position

	def update(self, dt, entities):
		mp = pygame.mouse.get_pos()

		if mp[0] > self.screen_resolution.x - self.pan_border_width and self.position.x < self.world_rect.width - self.screen_resolution.x:
			self.position.x += self.panning_speed
		if mp[0] < self.pan_border_width and self.position.x > 0:
			self.position.x -= self.panning_speed 
		if mp[1] > self.screen_resolution.y - self.pan_border_width and self.position.y < self.world_rect.height - self.screen_resolution.y:
			self.position.y += self.panning_speed
		if mp[1] < self.pan_border_width and self.position.y > 0:
			self.position.y -= self.panning_speed

class PlayerStats(object):
	def __init__(self, mothership):
		self.mothership = mothership
		self.font = pygame.font.SysFont("Monospace", 20, bold=True)
		self.gui = True

	def render(self, surface, viewport):
		y = 0
		text = "Shields: %d" % self.mothership.shield
		label = self.font.render(text, 1, (255, 255, 255))
		surface.blit(label, (0,y))
		y += 20
		text = "Resources: %d" % self.mothership.resources
		label = self.font.render(text, 1, (255, 255, 255))
		surface.blit(label, (0,y))

class MissionSelector(object):
	def __init__(self, viewport, mothership):
		self.viewport = viewport
		self.entities = []
		self.mothership = mothership
		self.gui = True

	def handle_event(self, event):	
		if event.type == MOUSEBUTTONDOWN:
			mp = Vector2(pygame.mouse.get_pos())	
			wp = self.viewport.screen2world_coordinates(mp)

			iwp = util.v2i_tuple(wp)
			for entity in self.entities:
				if isinstance(entity, TerranMothership):
					if entity.bb.collidepoint(iwp):
						self.mothership.mission = entity
						return

			self.mothership.mission = wp

	def update(self, dt, entities):
		self.entities = entities

	def render(self, surface, viewport):
		if type(self.mothership.mission) == Vector2:
			sp = viewport.world2screen_coordinates(self.mothership.mission)
			pygame.draw.rect(surface, (255, 0, 255), Rect(int(sp.x) - 10, int(sp.y) - 10, 20, 20), 1)
		elif isinstance(self.mothership.mission, Ship):
			if hasattr(self.mothership.mission, "die"):
				self.mothership.mission = None
			else:
				sr = viewport.world2screen_rect(self.mothership.mission.bb)
				pygame.draw.rect(surface, (255, 0, 255), sr, 1)

class SpawnBar(object):
	def __init__(self, mothership):
		self.mothership = mothership
		self.position = Vector2(200,0)
		self.slot_dimension = (200, 140)
		self.gui = True
		self.font = pygame.font.SysFont("monospace", 14, bold=True)

	def render(self, surface, viewport):
		pos = copy.deepcopy(self.position)
		i = 1
		for (blueprint, ai) in self.mothership.blueprints:
			dim = util.v2i_tuple(Vector2(blueprint["graphic"].get_size())*blueprint["graphic_scale"])
			g = pygame.transform.scale(blueprint["graphic"], dim)
			surface.blit(g, (int(pos.x + self.slot_dimension[0]/2 - dim[0]/2), int(pos.y + self.slot_dimension[1]/2 - dim[1]/2)))
			label = self.font.render(str(i), 1, (255,255,255))
			surface.blit(label, util.v2i_tuple(pos))
			label = self.font.render(str(blueprint["resource_cost"]), 1, (255, 255, 255))
			surface.blit(label, util.v2i_tuple(pos + Vector2(0, self.slot_dimension[1] - 14)))
			pos.x += self.slot_dimension[0]
			i += 1

class ShipStats(object):
	def __init__(self, viewport):
		self.ship = None
		self.font = pygame.font.SysFont("monospace", 14, bold=True)
		self.viewport = viewport

	def update(self, dt, entities):
		mp = pygame.mouse.get_pos()

		print self.ship

		for entity in entities:
			if isinstance(entity, Ship):
				bb = self.viewport.world2screen_rect(entity.bb)
				if bb.collidepoint(mp):
					self.ship = entity
					return

		self.ship = None

	def render(self, surface, viewport):
		if isinstance(self.ship, Ship):
			bb = self.viewport.world2screen_rect(self.ship.bb)
			pygame.draw.rect(surface, (255, 255, 0), bb, 1)
			text = "Shield: " + str(self.ship.shield)
			label = self.font.render(text, 1, (255,255,255))
			surface.blit(label, (bb.topleft[0], bb.topleft[1] - 14))
