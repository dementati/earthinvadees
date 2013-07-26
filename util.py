import math

from gameobjects.vector2 import Vector2

def rotate_vector2(v, angle):
	cs = math.cos(angle)
	sn = math.sin(angle)

	px = v.x*cs - v.y*sn
	py = v.x*sn + v.y*cs

	return Vector2(px, py)
