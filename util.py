import math

from gameobjects.vector2 import Vector2

def rotate_v(v, angle):
	cs = math.cos(angle)
	sn = math.sin(angle)

	px = v.x*cs - v.y*sn
	py = v.x*sn + v.y*cs

	return Vector2(px, py)

def dot_v(v1, v2):
	return v1.x*v2.x + v1.y*v2.y

def angle_between_v(v1, v2):
	return math.atan2(v1.x*v2.y - v1.y*v2.x, dot_v(v1,v2)) * 180.0/math.pi

def project_v(u,v):
	return v*dot_v(u,v)/v.get_magnitude()**2
