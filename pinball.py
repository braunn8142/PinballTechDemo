import math
import pygame
from pygame.constants import *
from pygame.math import Vector2
from physics_objects import Circle, Polygon, Wall
from contact import generate_contact, resolve_bumper_contact, resolve_contact
from forces import Gravity

pygame.init()
pygame.font.init()

# Fonts
pygame.font.init()
font = pygame.font.SysFont('monaco-ms', 24, True, False)

# Colors
bg_color1 = [0, 0, 0]
bg_color2 = [80, 200, 80]

wall_color1 = [120, 20, 20] # Red
wall_color2 = [255,127,0] # Orange
wall_color3 = [107, 53, 41]

obj_color1 = [20, 120, 120]
obj_color2 = [120, 120, 0]

score_color1=[255, 80, 80] # Pink
score_color2=[20,150,20] # Green
score_color3=[20, 13, 226] # Blue
score_color4=[255,255,255] # White

disabled_pad_color = [100, 0, 0]

ball_color = [255, 255, 255]
ball_color2 = [5, 255, 255]

# Create window
# Original width - 1000, width - 800
width = 1000
height = 1000
window = pygame.display.set_mode([width,height])

# Variables
# 3px = 1cm
# Gravity set to 490 rather than the normal 980

# Game Mechanic Variables
score = 0
balls_left = 2
no_bonus_ball = True

# Board setup/functionality variables
safezone_offset = 30
status_offset = height/5

play_width = width - safezone_offset
play_height = height - safezone_offset
play_height_top = height - status_offset
half_board_height = (height+status_offset)/2
play_area_center = Vector2(width/2, half_board_height)
# play_width/height were intended to only be used after wall generation functions

plunger_lane_width = safezone_offset/2
plunger_lane_center = width - (safezone_offset * 1.5)

plunger_y_max = height - (height * 0.3)
plunger_y_min = height - (height * 0.1)
plunger_accel = 50

flipper_ang_accel = 0.7
flipper_ang_decel = 0.7
flipper_angle = 25
flipper_max_angle = 30

# Bumpers
# Adjusts the distance that the ball will rebound off of all bumpers
rebound_multiplier = 1

# Score zones
pad_timer = 0
gfx_timer = 0

# Game over handling
game_over = False

# Clock object for timing
clock = pygame.time.Clock()
fps = 60
dt = 1/fps

def setup_walls():
    # Create the outside walls
    walls.append(Wall(point1=Vector2(safezone_offset, status_offset), point2=Vector2(play_width, status_offset), reverse=False, color=wall_color1))
    walls.append(Wall(point1=Vector2(play_width, status_offset), point2=Vector2(play_width, play_height), reverse=False, color=wall_color1))
    walls.append(Wall(point1=Vector2(safezone_offset, play_height), point2=Vector2(safezone_offset, status_offset), reverse=False, color=wall_color1))    
    
    # Setup the plunger lane walls on the right side of the screen
    walls.append(create_box(30, 30, (play_width, play_height), 1, wall_color1))
    walls.append(create_box(30, 300, (play_width - 2 * safezone_offset, height-300), 1, wall_color1))

    # Setup the plunger lane walls on the left side of the screen
    walls.append(create_box(30, 300, (safezone_offset + 2 * safezone_offset, height-300), 1, wall_color1))

    # Triangles on top of the plunger lane walls
    walls.append(create_board_poly(-410, 630, [Vector2(0,0), Vector2(-30, 30), Vector2(30, 30)], False, wall_color1))
    walls.append(create_board_poly(-410, 630, [Vector2(0,0), Vector2(-30, 30), Vector2(30, 30)], True, wall_color1))

    # Setup the top set of curves at the corners of the screen    
    create_curve(60, Vector2(width-70, status_offset + safezone_offset), 30, True, 1, 20)
    create_curve(60, Vector2(70, status_offset + safezone_offset), 30, False, 1, 20)    

    # Setup the curves in the middle of the screen
    create_curve(60, Vector2(width/2-80, status_offset + safezone_offset), 30, True, 1, 20)
    create_curve(60, Vector2(width/2+80, status_offset + safezone_offset), 30, False, 1, 20)    

    # Setup the gutters on the bottom to roll the ball into the center
    walls.append(Polygon(pos=(width/2+100, height-140), offsets=[(0,0), (280, 0), (280, -100)], color=wall_color1, reverse=True))
    walls.append(Polygon(pos=(width/2-100, height-140), offsets=[(0,0), (-280, 0), (-280, -100)], color=wall_color1))
        
    # Scaffolding beneath the gutters
    walls.append(Polygon(pos=(width/2+100, height-140), offsets=[(0,0),(100, 0), (100, 200)], color=wall_color1, reverse=True))
    walls.append(Polygon(pos=(width/2-100, height-140), offsets=[(0,0),(-100, 0), (-100, 200)], color=wall_color1))

    # Gutter roof
    walls.append(create_board_poly(x_pos_offset=120, y_pos_offset=180, offset=[Vector2(0,0), Vector2(200, -100), Vector2(200, -110), Vector2(0, -10)], facing_left=False, in_color=wall_color1))
    walls.append(create_board_poly(x_pos_offset=120, y_pos_offset=180, offset=[Vector2(0,0), Vector2(200, -100), Vector2(200, -110), Vector2(0, -10)], facing_left=True, in_color=wall_color1))    

    # Gutter walls
    walls.append(create_board_poly(x_pos_offset=320, y_pos_offset=290, offset=[Vector2(0,0), Vector2(0, -100), Vector2(0, -110)], facing_left=False, in_color=wall_color1))
    walls.append(create_board_poly(x_pos_offset=320, y_pos_offset=290, offset=[Vector2(0,0), Vector2(0, -100), Vector2(0, -110)], facing_left=True, in_color=wall_color1))


    # TESTING | SETUP A HUGE LOOP
    loop_offsets = [
        # Setup "outside" box
        Vector2(0,0),
        Vector2(0, 100),
        Vector2(20, 100),
        Vector2(30, 80),
        Vector2(30, 70),
        Vector2(10, 60),
        Vector2(10, 30),
        Vector2(30, 10),
        Vector2(50, 10),
        Vector2(50, 0)

        #Vector2(100, 100),
        #Vector2(100, 0)
        
        
        #Vector2(80, 0), Vector2(70, 20), Vector2(70, 30),
        #Vector2(95, 70), Vector2(95, 85), Vector2(80, 95), Vector2(0, 95), Vector2(0, 100)

    ]
    

    one_way_offsets = [
        Vector2(0,0),
        Vector2(0, 20),
        Vector2(40, 10),
        Vector2(60, 20),
        Vector2(60, 0),
        Vector2(55, -10)
        #Vector2(30, -20)
        
    ]
    walls.append(create_board_poly(410, 630, one_way_offsets, True, score_color3))

def setup_bumpers():
    # Center circle bumper
    bumpers.append(Circle(radius=20, pos=(width/2+200, height-500), color=score_color1))

    # Triple cluster of bumpers in the top left
    bumpers.append(Circle(radius=15, pos=(width/2 - 200, height-700), color=score_color1))
    bumpers.append(Circle(radius=15, pos=(width/2 - 400, height-700), color=score_color1))
    bumpers.append(Circle(radius=15, pos=(width/2 - 300, height-650), color=score_color1))
    
    # Gutter roof bumpers
    bumpers.append(create_board_poly(x_pos_offset=220, y_pos_offset=240, offset=[Vector2(0,0), Vector2(100, -50), Vector2(100, -60), Vector2(0, -10)], facing_left=False, in_color=score_color1))
    bumpers.append(create_board_poly(x_pos_offset=220, y_pos_offset=240, offset=[Vector2(0,0), Vector2(100, -50), Vector2(100, -60), Vector2(0, -10)], facing_left=True, in_color=score_color1))

    # Single bumper on the right side
    bumpers.append(Circle(radius=15, pos=(width/2 + 200, height-700), color=score_color1))

    # Add all bumpers to the objects array    
    for obj in bumpers:
        objects.append(obj)

def setup_bonus():
    # Circle on the right side of the screen
    bonus_zones.append(Circle(radius=12, pos=(width/2, height-400), color=score_color2))
    
    # Set of 2 strips, each extending from the center outwards and up to the top of the screen
    bonus_zones.append(create_board_poly(100, 500, [Vector2(-50, 50), Vector2(0, 50), Vector2(50, 0), Vector2(0, 0)], True, score_color2))    
    bonus_zones.append(create_board_poly(200, 600, [Vector2(-50, 50), Vector2(0, 50), Vector2(50, 0), Vector2(0, 0)], True, score_color2))
    bonus_zones.append(create_board_poly(300, 700, [Vector2(-50, 50), Vector2(0, 50), Vector2(50, 0), Vector2(0, 0)], True, score_color2))    

    # Strips indicating flipper launch angle from right flipper to top left
    bonus_zones.append(create_board_poly(30, 300, [Vector2(-20, 30), Vector2(0, 30), Vector2(20, 0), Vector2(0, 0)], False, score_color2))
    bonus_zones.append(create_board_poly(70, 360, [Vector2(-20, 30), Vector2(0, 30), Vector2(20, 0), Vector2(0, 0)], False, score_color2))
    bonus_zones.append(create_board_poly(110, 420, [Vector2(-20, 30), Vector2(0, 30), Vector2(20, 0), Vector2(0, 0)], False, score_color2))
    bonus_zones.append(create_board_poly(150, 480, [Vector2(-20, 30), Vector2(0, 30), Vector2(20, 0), Vector2(0, 0)], False, score_color2))
    bonus_zones.append(create_board_poly(190, 540, [Vector2(-20, 30), Vector2(0, 30), Vector2(20, 0), Vector2(0, 0)], False, score_color2))    

    for obj in bonus_zones:
        objects.append(obj)

def create_curve(side_length, center_pos, center_angle, facing_left, height_multiplier, corner_offset):
    # center_angle (degree)| Adjusts the sharpness of the curve
    # corner_offset (int)| Adjusts how close triangles are to the center triangle
    y_swap = 1
    if facing_left == True:
        y_swap = -1

    walls.append(create_turn(side_length, (center_pos.x-corner_offset, center_pos.y + y_swap * corner_offset), -center_angle, facing_left, height_multiplier))
    walls.append(create_turn(side_length, (center_pos.x, center_pos.y), 0, facing_left, height_multiplier))
    walls.append(create_turn(side_length, (center_pos.x+corner_offset, center_pos.y - y_swap * corner_offset), center_angle, facing_left, height_multiplier))
    
    # Adding additional walls because the curve needed more smoothing
    if facing_left == True:
        walls.append(create_turn(side_length, (center_pos.x-(corner_offset*1.5), center_pos.y + y_swap * corner_offset), -center_angle/2, facing_left, height_multiplier))
        walls.append(create_turn(side_length, (center_pos.x+(corner_offset/2), center_pos.y -y_swap * corner_offset), center_angle/2, facing_left, height_multiplier))
    else:        
        walls.append(create_turn(side_length, (center_pos.x-(corner_offset/2), center_pos.y + y_swap * corner_offset), -center_angle/2, facing_left, height_multiplier))
        walls.append(create_turn(side_length, (center_pos.x+(corner_offset*1.5), center_pos.y -y_swap * corner_offset), center_angle/2, facing_left, height_multiplier))    
    
def create_box(width_size, height_size, box_pos, wall_width, in_color):
    # Creates boxes by width and height
    return Polygon(
        offsets=[Vector2(-width_size, -height_size), Vector2(width_size, -height_size), Vector2(width_size, height_size), Vector2(-width_size, height_size)],
        pos=(box_pos),
        width=wall_width,
        reverse=False,
        normals_length=1,
        color=in_color
    )

def create_flipper(total_length, total_height, starting_pos, facing_left, rest_angle):    
    if facing_left == True:
    # Sets offsets to face left
        temp_offsets=[Vector2(0,0), Vector2(-total_length, 0), Vector2(-total_length, total_height/2), Vector2(0, total_height)]
    else:
        temp_offsets=[Vector2(0,0), Vector2(total_length, 0),Vector2(total_length, total_height/2), Vector2(0, total_height)]    
    return Polygon(
        offsets = temp_offsets,
        pos = starting_pos,
        angle = rest_angle,
        reverse = facing_left,
        color=obj_color1
    )

def create_turn(side_length, edge_pos, center_angle, facing_left, height_multiplier):    
    # edge_pos is the centerpoint for the triangle
    # height_multiplier adjusts the height of the peak of the triangle (int)
    if facing_left == True:
        # Sets offsets to face left
        temp_offsets=[Vector2(-side_length, -side_length/height_multiplier), Vector2(side_length, -side_length/height_multiplier), Vector2(side_length, side_length/height_multiplier)]        
    else:
        temp_offsets=[Vector2(-side_length, -side_length/height_multiplier), Vector2(side_length, -side_length/height_multiplier), Vector2(-side_length, side_length/height_multiplier)]    
    
    return Polygon(
        offsets=temp_offsets,
        pos=(edge_pos),
        angle = (convert_degree(center_angle)),            
        reverse=False,
        color=wall_color1
    )

def create_board_poly(x_pos_offset, y_pos_offset, offset, facing_left, in_color):
    side_check = 1
    if not facing_left:
        side_check *= -1
        for obj in offset:
            obj.x *= -1

    return Polygon (
        pos=(width/2 + side_check * x_pos_offset, height - y_pos_offset), 
        offsets=offset,
        color=in_color,
        reverse=facing_left,
        
        # DETELE AFTER DEBUG!!!!!!!
        width=1
    )

# Decor is rendered on the layer ABOVE the game board
def setup_decor():
    gfx_objs.append(Polygon(pos=(width/2+200, height-140), offsets=[(0,0), (180, 0), (180, 140)], color=wall_color2))
    gfx_objs.append(Polygon(pos=(width/2-200, height-140), offsets=[(0,0), (-180, 0), (-180, 140)], color=wall_color2))

    # Bumper overlay GFX
    # Center Bumper
    gfx_objs.append(Circle(radius= 15, pos=bumpers[0].pos, color=score_color3))
    gfx_objs.append(Circle(radius= 5, pos=bumpers[0].pos, color=score_color4))

    # Create a 30x30 border around the outside of the screen. Commented out during testing.
    gfx_objs.append(create_box(30, play_height, Vector2(0,0), 0, wall_color1))
    gfx_objs.append(create_box(15, play_height, Vector2(0,0), 0, bg_color1))
    gfx_objs.append(create_box(30, play_height, Vector2(play_width+safezone_offset, 0), 0, wall_color1))
    gfx_objs.append(create_box(15, play_height, Vector2(play_width+safezone_offset, 0), 0, bg_color1))
#    gfx_objs.append(create_box(play_width/2, 30, Vector2(play_width/2,0), 0, wall_color1))

    # Create a large rectangle to cover the top of the board
    gfx_objs.append(create_box(play_width/2, status_offset, Vector2(width/2,0), 0, wall_color1))

    # Create a box around where the text will be displayed to emulate a backbox screen
    gfx_objs.append(create_box(width/4, safezone_offset * 2, Vector2(width/2, status_offset/2), 0, bg_color1))

    # Lanes on both sides of the top "half-pipe" structures
    gfx_objs.append(create_box(40, 30, Vector2(play_width/4, status_offset-30), 0, wall_color2))
    gfx_objs.append(create_box(30, 30, Vector2(play_width/4, status_offset-30), 0, wall_color3))    

    # Create Graphics that will change color frequently during the game
    flashing_gfx.append(create_board_poly(100, 490, [Vector2(-30, 30), Vector2(0, 30), Vector2(30, 0), Vector2(0, 0)], True, score_color3))    
    flashing_gfx.append(create_board_poly(200, 590, [Vector2(-30, 30), Vector2(0, 30), Vector2(30, 0), Vector2(0, 0)], True, score_color3))
    flashing_gfx.append(create_board_poly(300, 690, [Vector2(-30, 30), Vector2(0, 30), Vector2(30, 0), Vector2(0, 0)], True, score_color3))

    for obj in flashing_gfx:
        gfx_objs.append(obj)

def reset_ball():
    for obj in balls:
            obj.pos = Vector2(play_width-safezone_offset * 0.5, height-400)
            obj.vel = Vector2(0,0)
    
    # ball_in_play.pos=Vector2(width-45, height-400)
    # ball_in_play.vel=Vector2(0,0)
    # if not no_bonus_ball:
    #     ball_in_play2.pos=Vector2(width-45, height-400)
        

def convert_degree(degrees):
    converted_radians = (math.pi/180) * degrees
    return converted_radians

# OBJECTS
objects = []

# walls
walls = []
setup_walls()

# bumpers
bumpers = []
setup_bumpers()

# bonus zones
bonus_zones = []
setup_bonus()

# Create anything that will be handled by the decor list
gfx_objs = []
flashing_gfx = []
setup_decor()

# paddles
left_flipper = create_flipper(90, 20, (width/2-100, height-140), False, convert_degree(flipper_angle))
left_flipper_ball = Circle(radius=10, pos=Vector2(width/2-98, height-128), color=obj_color1)
right_flipper = create_flipper(90, 20, (width/2+100, height-140), True, convert_degree(-flipper_angle))
right_flipper_ball = Circle(radius=10, pos=Vector2(width/2+98, height-128), color=obj_color1)
#l=270 | r=650

# plunger
plunger = create_box(plunger_lane_width/2, 20, (play_width - plunger_lane_width, plunger_y_max), 0, wall_color1)

# ball
balls = []
ball_in_play = Circle(mass=1, pos=Vector2(width-50, height-500), radius=9, color=ball_color, width=1)

# Create some gfx for the ball
ball_arm = Circle(pos=ball_in_play.pos, radius=6, color=obj_color2)

gfx_objs.append(ball_arm)
balls.append(ball_in_play)
reset_ball()

# Create a way to save the ball by teleporting it to a set point on the board
save_ball_tele_entr = Circle(radius=12, pos=(safezone_offset * 1.5, height-50), color=obj_color1)
save_ball_tele_exit = Circle(radius=12, pos=(width/2 + 250, height-700), color=obj_color1, width=1)
objects.append(save_ball_tele_entr)
objects.append(save_ball_tele_exit)

# Add walls and ball interactions to the wall array
walls.append(plunger)
walls.append(right_flipper)
walls.append(left_flipper)

# Add all previous objects to the objects array so the ball can interact properly
objects.append(plunger)
objects.append(right_flipper)
objects.append(right_flipper_ball)
objects.append(left_flipper)
objects.append(left_flipper_ball)
objects.append(ball_in_play)

# I put all of the controls in a single function. I would split these into multiple functions normally.
def control_setup():
    # Plunger control
    keys = pygame.key.get_pressed()
    mouse = Vector2(pygame.mouse.get_pos())

    if keys[K_SPACE]:        
        if plunger.pos.y < plunger_y_min:
            plunger.vel = Vector2(0, 150)
        else:
            plunger.vel = Vector2(0,0)
    
    elif (not keys[K_SPACE]):
        if plunger.pos.y > plunger_y_max:
            plunger.vel.y -= plunger_accel
        elif plunger.pos.y <= plunger_y_max and plunger.vel != Vector2(0,0):
            plunger.vel = Vector2(0,0)
    
    # Paddle controls
    # Prevent the paddle from swinging too far
    if left_flipper.angle <= convert_degree(-flipper_max_angle):
        left_flipper.angle = convert_degree(-flipper_max_angle)
    if left_flipper.angle >= convert_degree(flipper_angle):
        left_flipper.angle = convert_degree(flipper_angle)
    if right_flipper.angle >= convert_degree(flipper_max_angle):
        right_flipper.angle = convert_degree(flipper_max_angle)
    if right_flipper.angle <= convert_degree(-flipper_angle):
        right_flipper.angle = convert_degree(-flipper_angle)
        # Simplify this code 

    if keys[K_LSHIFT]:                
        if left_flipper.angle > convert_degree(-flipper_max_angle):
            left_flipper.avel += -flipper_ang_accel
        else:
            left_flipper.avel = 0
    elif (not keys[K_LSHIFT]):
        if left_flipper.angle < convert_degree(flipper_angle):
            left_flipper.avel += flipper_ang_decel
        else:
            left_flipper.avel = 0
    
    if keys[K_RSHIFT]:                
        if right_flipper.angle < convert_degree(flipper_max_angle):
            right_flipper.avel += flipper_ang_accel
        else:
            right_flipper.avel = 0    
    elif (not keys[K_RSHIFT]):
        if right_flipper.angle > convert_degree(-flipper_angle):
            right_flipper.avel += -flipper_ang_decel
        else:
            right_flipper.avel = 0

    # DEBUG 
    if keys[K_f]:
        ball_in_play.pos = mouse
        ball_in_play.vel = Vector2(0,0)

# Setup forces
gravity = Gravity(objects_list=balls, acc=(0,490))

# Game loop
running = True
while running:
    # Event handling loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False                    
        elif (balls_left < 0):
            game_over = True

    # KEY STATE
    control_setup()
    
    # CONTACTS    
    # Process ball on wall collisions
    for wall in walls:
        for ball in balls:
            c = generate_contact(wall, ball)
            resolve_contact(c, restitution=0.3)    
    
    # Process ball on bumper collisions
    for obj in bumpers:
        for ball in balls:
            c = generate_contact(obj, ball)
            resolve_bumper_contact(c, rebound_strength = rebound_multiplier)
            if c.overlap() >= 0:
                score+=100 

    # Set timer for pad reset
    pad_timer += dt
    print(pad_timer)
    if (pad_timer > 3):
        pad_timer = 0

    for obj in bonus_zones:
        for ball in balls:
            c = generate_contact(obj, ball)
            if c.overlap() > 2 and obj.color == score_color2:
                print(f"Overlap with score zone!")
                score += 100
                obj.color=disabled_pad_color
                pad_timer = 0
        # Reset the pad every 30 time intervals
            elif obj.color == disabled_pad_color and pad_timer%3 == 0:
                obj.color = score_color2
    
    telecheck = generate_contact(save_ball_tele_entr, ball_in_play)
    if telecheck.overlap() > 2 and score >= 1000 and save_ball_tele_entr.color == obj_color1:
        ball_in_play.pos = Vector2(width/2 + 250, height-700)
        ball_in_play.vel=Vector2(ball_in_play.vel.x,0)
        save_ball_tele_entr.color = score_color1


    # Check for multi-ball play
    if score > 300 and no_bonus_ball:
        ball_in_play2 = Circle(mass=1, pos=Vector2(width/2+100, 400), radius=9, color=ball_color2, width=0)
        balls.append(ball_in_play2)
        objects.append(ball_in_play2)
        ball_in_play2.vel = Vector2(0,0)
        no_bonus_ball = False
    
    # Calculate any ball on ball collisions
    if not no_bonus_ball:
        c = generate_contact(ball_in_play, ball_in_play2)
        resolve_contact(c, restitution=0.1)        

    # PHYSICS
    # Clear force from all particles
    for obj in objects:
        obj.clear_force()
    
    # Add forces
    gravity.apply()

    # Update particles
    for obj in objects:
        obj.update(dt)

    # Checking if pinball has fallen out of the game
        if ball_in_play.pos.y > height:
            # Reset the ball and the teleporter
            balls_left-=1
            if balls_left >= 0:
                reset_ball()
                save_ball_tele_entr.color = obj_color1
            else:
                ball_in_play.pos = Vector2(0,0)
                ball_in_play.vel = Vector2(0,0)

    # GRAPHICS
    ## Clear window
    window.fill([0,0,0])
    # Draw a background
    pygame.draw.rect(window, bg_color1, [0, 0, width, height])

    ## Draw objects
    # Draw walls
    for obj in walls:
        obj.draw(window)
    
    # Draw Objects
    for obj in objects:
        obj.draw(window)

    ## Changing GFX
    # Set up a timer for changing GFX
    gfx_timer += dt
    if gfx_timer > 4:
        gfx_timer = 0
    
    # Set any moving GFX
    ball_arm.pos = ball_in_play.pos
    ball_arm.angle = ball_in_play.angle

    for i in range(len(flashing_gfx)):
        if gfx_timer > 1:
            flashing_gfx[0].color = score_color4
        if gfx_timer > 2:
            flashing_gfx[1].color = score_color4
        if gfx_timer > 3:
            flashing_gfx[2].color = score_color4
        else:
            flashing_gfx[i].color = score_color3

    # Draw any overlay graphics
    for obj in gfx_objs:
        obj.update(dt)
        obj.draw(window)

    ## Draw Text
    attempts_left_text = font.render(f"BALLS REMAINING: {balls_left}", True, [255,255,255])
    attempts_left_text_rect = attempts_left_text.get_rect(center = (width/2, 90))
    window.blit(attempts_left_text, attempts_left_text_rect)

    score_display_text = font.render(f"SCORE: {score}", True, [255, 255, 255])    
    score_display_text_rect = score_display_text.get_rect(center = (width/2, 120))
    window.blit(score_display_text, score_display_text_rect)

    if game_over:
        game_over_text = font.render(f"GAME OVER", True, [255, 10, 100])
        game_over_text_rect = game_over_text.get_rect(center = (width/2, height/2-100))
        window.blit(game_over_text, game_over_text_rect)

    
    pygame.display.update()
    clock.tick(fps)