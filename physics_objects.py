from locale import normalize
import math
from zoneinfo import available_timezones
from pygame.math import Vector2
import pygame

class Particle:
    def __init__(self, mass=math.inf, pos=(0,0), vel=(0,0),
                       momi=math.inf, angle=0, avel=0, torque=0):
        self.mass = mass
        self.pos = Vector2(pos)
        self.vel = Vector2(vel)
        self.momi = momi
        self.angle = angle
        self.avel = avel
        self.torque = torque
        self.clear_force() # clear_force() belongs to our object self
        
        self.clear_force()

    def clear_force(self):
        self.force = Vector2(0,0)

    def add_force(self, force):
        self.force += force
        #

    def update(self, dt):
        # update velocity using the current force
        self.vel += (self.force / self.mass) * dt
        # update position using the newly updated velocity
        self.pos += self.vel * dt

        # Rotation
        self.avel += (self.torque/self.momi) * dt
        self.angle += self.avel*dt
    
    def impulse(self, impulse):        
        self.vel += impulse/self.mass

    def delta_pos(self, delta):
        self.pos += delta

class Circle(Particle):
    def __init__(self, radius = 10, color = [255, 255, 255], width = 0, **kwargs):
        # **kwargs is a dictionary to catch all the other keyword arguments
        self.radius = radius
        self.color = color
        self.width = width
        super().__init__(**kwargs) # calls the superclass constructor
        # **kwargs unpacking the kwargs dictionary into key=value, key=value, etc
        self.contact_type="Circle"

    def draw(self, window):
        pygame.draw.circle(window, self.color, self.pos, self.radius, self.width)

class Wall(Particle):
    def __init__(self, point1, point2, reverse=False, color=[0,0,0], width=1):
        # Two endpoints of the wall (visually)
        # Wall behaves as if it's infinite
        self.point1 = Vector2(point1)
        self.point2 = Vector2(point2)
        self.contact_type = "Wall"
        super().__init__(pos=(self.point1 + self.point2)/2)
        self.width = width
        self.color = color
        # Normal is perpendicular to the wall
        self.normal = (point2 - point1).normalize().rotate(90)
        # If normal is in the wrong direction, you can set reverse=True or swap point1/point2
        if reverse:
            self.normal *= -1

    def draw(self, screen):
        pygame.draw.line(screen, self.color, self.point1, self.point2, self.width)

# A polygon's points are interpreted as offsets from the position. 
# They are returned in a list of lists | Ex: offsets = [ [-10, -10], [10, -10], [10, 10], [-10, 10] ]
class Polygon(Particle):
    def __init__(self, offsets=[], color=[255,255,255], width=0, normals_length=0, reverse=False, **kwargs):
        
        self.contact_type = "Polygon"

        # Convert all offsets into Vector2
        self.offsets = []
        for offset in offsets:
            self.offsets.append(Vector2(offset))
        
        # Calculate local_normals | local_normals are the normals of the UNROTATED shape | Vertices 0 and 1 create the normal 1, etc
        self.local_normals = []
        for i in range(len(self.offsets)):
            normal = (self.offsets[i-1] - self.offsets[i]).normalize().rotate(90)
            if reverse:
                normal *= -1
            self.local_normals.append(normal)
        
        self.color = color
        self.width = width
        self.normals_length = normals_length

        super().__init__(**kwargs)
        
        self.points = self.offsets.copy()
        self.normals = self.local_normals.copy()
        self.update_points()

    # Compute where the vertices are in space | Iterate through all of the offsets and calc the points
    def update_points(self):
        for i in range(len(self.offsets)):
            self.points[i] = self.pos + self.offsets[i].rotate_rad(self.angle) # point = pos + offset
            self.normals[i] = self.local_normals[i].rotate_rad(self.angle)
            # rotate_rad must be included because the polygon might be rotated
    
    def draw(self, window):
        pygame.draw.polygon(window, self.color, self.points, self.width)
        if (self.normals_length > 0):
            for i in range(len(self.normals)):
                pygame.draw.line(window, [0,0,0], self.points[i], 
                                                  self.points[i] + self.normals[i] * self.normals_length)

    # Need to override update from Particle, to include updating the points
    def update(self, dt):
        # First, update the Particle things
        super().update(dt)
        # Next, update the points
        self.update_points()

#------------------------------------------------------#
# Rotation and polygon class
# mass -> moment of inerta (momi) | I
# pos -> angle                    | theta
# vel -> avel                     | w
# force -> torque                 | t
# 
# When we update linear motion: 
# change in r = v change in t.