import pygame
from pygame.math import Vector2
import itertools
import math

class SingleForce:
    def __init__(self, objects_list=[]):
        self.objects_list = objects_list

    def apply(self):
        for obj in self.objects_list:
            force = self.force(obj)
            obj.add_force(force)

    def force(self, obj): # virtual function
        return Vector2(0, 0)


class PairForce:
    def __init__(self, objects_list=[]):
        self.objects_list = objects_list

    def apply(self):        
        # Loop over all pairs of objects and apply the calculated force
        for object in self.objects_list:
            for i in self.objects_list:
                force = self.force(i, object)
                (i).add_force(force)
                object.add_force(-force)

        # to each object, respecting Newton's 3rd Law.  
        # Use either two nested for loops (taking care to do each pair once)
        # or use the itertools library (specifically, the function combinations).
        pass

    def force(self, a, b): # virtual function
        return Vector2(0, 0)


class BondForce: # Bond the objects together in order
    def __init__(self, pairs_list=[]):
        # pairs_list has the format [[obj1, obj2], [obj3, obj4], ... ]
        self.pairs_list = pairs_list

    def apply(self):
        # Loop over all pairs from the pairs list.  
        # Apply the force to each member of the pair respecting Newton's 3rd Law.
        # One way to do this
        for pair in self.pairs_list:
            # Add force for A
            force = self.force(pair[0], pair[1])
            pair[0].add_force(force)
            # Add force for B
            pair[1].add_force(-force)
            

        # Alt way to do this
        # for a,b in self.pairs_list: # unpacking the two-element list
            # a
            # b

        # Add the connecting lines
        # circle_lines.append(pygame.draw.line([200, 0, 0], a.pos, b.pos))
        pass

    def force(self, a, b): # virtual function
        return Vector2(0, 0) # return force on A due to B
    
    # Draw function in Spring class
    # def draw(self, a, b):
        

# Add Gravity, SpringForce, SpringRepulsion, AirDrag
class Gravity(SingleForce):
    def __init__(self, acc=(0,0), **kwargs):
        self.acc = Vector2(acc)
        super().__init__(**kwargs)

    def force(self, obj): # overriding the super class
        if (obj.mass == math.inf):
            return pygame.Vector2(0,0)
        else:
            return obj.mass*self.acc
        # Note: this will throw an error if the object has infinite mass.
        # Think about how to handle those.

class SpringForce(BondForce):
    def __init__(self, pairs_list=[]):
        # pairs_list has the format [[obj1, obj2], [obj3, obj4], ... ]
        self.pairs_list = pairs_list

    def force(self, objA, objB):        
        k=2.5
        l=30
        # b=0.0002
        b=.0002
        zeroV = Vector2(0,0)
        if(objA.pos - objB.pos == zeroV):
            return zeroV
            
        r = Vector2(objA.pos - objB.pos)
        v = Vector2(objA.vel - objB.vel)

        # v = Vector2(objA.vel - objB.vel)
        Fspring = (-k * (r.magnitude() - l) - (b * v).dot(r.normalize())) * r.normalize()
        return Fspring

        # Spring force 
        # | | = magnitude
        # ^r = normalize
        # Fspring = [-k(|r| - l)-bv * ^r] ^r
        # r = ra - rb | v = va - vb
        # keep dampening at 0 until stiffness/length are good
        # k = spring stiffness | l = natural length | b = dampening constant

    # Allow drawing of the lines
    def draw(self, window):
        for a,b in self.pairs_list: # unpacking the two-element list
            pygame.draw.line(window, [225, 225, 0], a.pos, b.pos)

class AirDrag(SingleForce):
    def __init__(self, wind, **kwargs):
        self.wind = wind
        super().__init__(**kwargs)

    def apply(self):
        for obj in self.objects_list:
            force = self.force(obj)
            obj.add_force(force)

    def force(self, obj): # virtual function
        # self.wind = Vector2(0,0)
        v = obj.vel - self.wind        
        Cd = .01
        p = .001
        A = math.pi
        Fairdrag = -(1/2)*Cd*p*A*v.magnitude()*v
        # Fairdrag = -1/2(Cd * p * A * |v|v)
        return Fairdrag

    
class SpringRepulsion(PairForce):
    def __init__(self, objects_list=[]):
        self.objects_list = objects_list

    def force(self, a, b): # virtual function
        k = 1
        r = a.pos - b.pos
        Ra = a.radius
        Rb = b.radius

        if ((Ra + Rb - r.magnitude()) > 0) and (r.length() != 0):
            Frepel = k * (Ra + Rb - r.magnitude()) * r.normalize()
            return Frepel
        else:
            return Vector2(0,0)
