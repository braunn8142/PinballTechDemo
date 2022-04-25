from typing import overload
from pygame.math import Vector2
import math

# Returns a new contact object of the correct type
# This function has been done for you.
def generate_contact(a, b):
    # Check if a's type comes later than b's alphabetically.
    # We will label our collision types in alphabetical order, 
    # so the lower one needs to go first.
    if b.contact_type < a.contact_type:
        a, b = b, a
    # This calls the class of the appropriate name based on the two contact types.
    return globals()[f"Contact_{a.contact_type}_{b.contact_type}"](a, b)
    
# Resolves a contact (by the default method) and returns True if it needed to be resolved
def resolve_contact(contact, restitution=0):
    a = contact.a
    b = contact.b
    n = contact.normal() # n^ = normal    
    d = contact.overlap() # d = overlap
    p = contact.point() # Point of contact
    # Resolve the overlap
    # Resolve only if overlap > 0
    if (d > 0):
        m = 1/(1/a.mass + 1/b.mass)
        # m = 1 / (1/ma + 1/mb)
        contact.a.pos += (m/a.mass) * d * n
        # translate a by (m/ma)*dn^ 
        contact.b.pos += -(m/b.mass) * d * n
        # translate b by -((m/ma)*dn^)

        # Resolve velocity at the point of contact
        # VatContact
        Va = a.vel
        Sa = p - a.pos
        Wa = a.avel
        SaT = Vector2(-Sa.y, Sa.x)
        # v - relative velocity 
        VaContact = Va + Wa * SaT

        Vb = b.vel
        Sb = p - b.pos
        Wb = b.avel
        SbT = Vector2(-Sb.y, Sb.x)
        VbContact = Vb + Wb * SbT

        # resolve velocity
        v = VaContact - VbContact

        # v = a.vel - b.vel        
        if(v.dot(n) < 0): # only resolve velocity if ->v * n^ < 0 (means objects are moving towards each other)
            # relative velocity ->v = va - vb
            j = -(1 + restitution) * m * (v.dot(n)) 
            # J = -(1 + E)m(->V*n^)
            J = j * n
            # ->J = Jn^
            a.impulse(J) # a.impulse(->J)
            b.impulse(-J) # b.impulse(->-J)

def resolve_bumper_contact(contact, rebound_strength):
    a = contact.a
    b = contact.b
    n = contact.normal() # n^ = normal    
    d = contact.overlap() # d = overlap
    p = contact.point() # Point of contact
    # Resolve the overlap
    # Resolve only if overlap > 0
    if (d > 0):
        m = 1/(1/a.mass + 1/b.mass)
        # m = 1 / (1/ma + 1/mb)
        contact.a.pos += (m/a.mass) * d * n
        # translate a by (m/ma)*dn^ 
        contact.b.pos += -(m/b.mass) * d * n
        # translate b by -((m/ma)*dn^)

        # Resolve velocity at the point of contact
        # # VatContact
        Va = a.vel
        Sa = p - a.pos
        Wa = a.avel
        SaT = Vector2(-Sa.y, Sa.x)
        # v - relative velocity 
        VaContact = Va + Wa * SaT

        Vb = b.vel
        Sb = p - b.pos
        Wb = b.avel
        SbT = Vector2(-Sb.y, Sb.x)
        VbContact = Vb + Wb * SbT

        #resolve velocity
        v = VaContact - VbContact

        #vrebound = 1
        vrebound = 300
    
        if(v.dot(n) < 0): # only resolve velocity if ->v * n^ < 0 (means objects are moving towards each other)
            # relative velocity ->v = va - vb
            j = m * (-v.dot(n) + vrebound)
            # J = -(1 + E)m(->V*n^)
            J = j * n
            # ->J = Jn^
            a.impulse(J) # a.impulse(->J)
            b.impulse(-J) # b.impulse(->-J)

    # E = restitution
    # m = reduced mass
    # ->V = relative velocity    
    
    # NOTES ON RESOLVING ROTATIONAL CONTACT
    # VaContact = Va + (Wa x Sa) <- Cross product
    # Va = translational velocity | a.vel
    # Wa = a.aVel
    # Sa = rc - ra (rc - pos of contact | ra - pos of a)
    # Wa x Sa = Wa * Sat
    # Sat = Sa rotated by 90 degrees = (-Sa.y, Sa.x)
    # Vb control - Vb + Wa x Sb
    # Sb = rc - rb
    # relative velocity V = Va control - Vb contact 
    # *Proceed as normal with resolve_contact()
    return False

# Generic contact class, to be overridden by specific scenarios
class Contact():
    def __init__(self, a, b):
        self.a = a
        self.b = b
        self.renew()
 
    def renew(self):
        pass

    def overlap(self):  # virtual function
        return 0                

    def normal(self):  # virtual function
        return Vector2(0,0)
    
    def point(self): # virtual function
        return Vector2(0,0)


# Contact class for two circles
class Contact_Circle_Circle(Contact):
    def __init__(self, a, b):
        super().__init__(a, b)

    def overlap(self):
        return (self.a.radius + self.b.radius) - (self.a.pos - self.b.pos).magnitude() # Fill in the appropriate expression
        # Return the calculated overlap

    def normal(self):
        return (self.a.pos - self.b.pos).normalize() # Fill in the appropriate expression
        # vectors (ra - rb).normalize()
        # return the calculated normal

# Contact class for a circle and a wall
class Contact_Circle_Wall(Contact):
    def __init__(self, a, b):
        super().__init__(a, b)
        self.circle = a
        self.wall = b

    def overlap(self):          
        return ((self.circle.radius) - (self.circle.pos - self.wall.pos).dot(self.wall.normal)) # Fill in the appropriate expression

    def normal(self):
        return self.wall.normal # Fill in the appropriate expression
        
# Empty class for wall -> wall collisions. Since overlap() and normal() are not being overridden those should not be overlapped
# Contact class for a circle and a wall
class Contact_Wall_Wall(Contact):
    def __init__(self, a, b):
        super().__init__(a, b)

# Contact class for a circle and a polygon
class Contact_Circle_Polygon(Contact):
    def __init__(self, a, b):        
        self.circle = a
        self.polygon = b
        super().__init__(a, b)

    def renew(self):
        # Check overlap with each side
        # Check overlap with a vertex
        # One option
        min_overlap = math.inf
        self.circle_overlaps_vertex = False

        for i in range(len(self.polygon.points)):
            wall_pos = self.polygon.points[i]
            wall_normal = self.polygon.normals[i]

        # Option 2, using zip (same as option 1)
        for i, (wall_pos, wall_normal) \
        in enumerate(zip(self.polygon.points, self.polygon.normals)):
            overlap = ((self.circle.radius) - (self.circle.pos - wall_pos).dot(wall_normal)) # Fill in the appropriate expression
            if overlap < min_overlap:
                min_overlap = overlap
                self.index = i # index of the side of least overlap

        ## Part 2 - Round off the endpoints
        # Check if the circle is beyond one of the two endpoints
        point1 = self.polygon.points[self.index]
        point2 = self.polygon.points[self.index - 1]

        side = point1 - point2
        if (self.circle.pos - point1).dot(side) > 0:
            # We are beyond point 1
            self.circle_overlaps_vertex = True
            self.index = self.index # variable index set to the index of the vertex
        elif (self.circle.pos - point2).dot(side) < 0:
            self.circle_overlaps_vertex = True
            self.index = self.index - 1 # variable index set to the index of the vertex

    def overlap(self):          
        if self.circle_overlaps_vertex:
            #Circle overlaps a vertex
            # return the overlap for two circles where the radius of the vertex is zero
            return ((self.circle.radius) - ((self.circle.pos - self.polygon.points[self.index]).magnitude()))
                    
        else:
            # Circle overlaps a side
            wall_pos = self.polygon.points[self.index]
            wall_normal = self.polygon.normals[self.index]
            return ((self.circle.radius) - (self.circle.pos - wall_pos).dot(wall_normal)) # Fill in the appropriate expression

    def normal(self):
        if self.circle_overlaps_vertex:
            # Circle overlaps vertex
            # just like the normal for two circles
            # a circle - circle ||| b circle is the vertex
            # COPY THE CODE FROM CIRCLE-CIRCLE COLLISION DETECTION
            return (self.circle.pos - self.polygon.points[self.index]).normalize()
        else:
            # Circle overlaps side
            return self.polygon.normals[self.index]# Fill in the appropriate expression
    
    def point(self):
        if self.circle_overlaps_vertex:
            return self.polygon.points[self.index]
        else:
            normal_offset = self.polygon.normals[self.index] * -1 * self.circle.radius
            return self.circle.pos + normal_offset
        
        # NOTES ON RESOLVING ROTATIONAL CONTACT
            # VaContact = Va + (Wa x Sa) <- Cross product
            # Va = translational velocity | a.vel
            # Wa = a.avel
            # Sa = rc - ra (rc - pos of contact | ra - pos of a)
            # Wa x Sa = Wa * Sat
            # Sat = Sa rotated by 90 degrees = (-Sa.y, Sa.x)
            # Vb control - Vb + Wa x Sb
            # Sb = rc - rb
            # relative velocity V = Va control - Vb contact 
            # *Proceed as normal with resolve_contact()
            # .