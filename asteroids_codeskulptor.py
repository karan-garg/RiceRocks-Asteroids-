#Karan Garg

#Supported Browsers: Chrome 18+ (Preferred), Firefox 11+, and Safari 6+ 
# CLICK ON THE PLAY BUTTON ON THE TOP LEFT CORNER TO PLAY
#CONTROLS- UP,LEFT,RIGHT TO STEER
          #SPACEBAR TO SHOOT

import simplegui
import math
import random

# globals for user interface
hs_sound_played = False
life_sound_played = False
hs_time_lim = True
life_color = "White"
score_color = "White"
high_score = 40
hs_bool = False
width = 850
control_width = 10
height = 500
score = 0
lives = 3
time = 0
started = False
explosion_group = set([])
missile_group_remove = set([])

class ImageInfo:
    def __init__(self, center, size, radius = 0, lifespan = None, animated = False):
        self.center = center
        self.size = size
        self.radius = radius
        if lifespan:
            self.lifespan = lifespan
        else:
            self.lifespan = float('inf')
        self.animated = animated

    def get_center(self):
        return self.center

    def get_size(self):
        return self.size

    def get_radius(self):
        return self.radius

    def get_lifespan(self):
        return self.lifespan

    def get_animated(self):
        return self.animated

    
# art assets created by Kim Lathrop, may be freely re-used in non-commercial projects, please credit Kim
    
# debris images - debris1_brown.png, debris2_brown.png, debris3_brown.png, debris4_brown.png
#                 debris1_blue.png, debris2_blue.png, debris3_blue.png, debris4_blue.png, debris_blend.png
debris_info = ImageInfo([500, 252], [1000, 504])
debris_image = simplegui.load_image("https://dl.dropboxusercontent.com/s/2b840eq4ut8g2sr/debris2_blue.png")

# nebula images - nebula_brown.png, nebula_blue.png
nebula_info = ImageInfo([400, 300], [800, 600])
nebula_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/nebula_blue.png")

# splash image
splash_info = ImageInfo([200, 150], [400, 300])
splash_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/splash.png")

# ship image
ship_info = ImageInfo([45, 45], [90, 90], 35)
ship_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/double_ship.png")

# missile image - shot1.png, shot2.png, shot3.png
missile_info = ImageInfo([5,5], [10, 10], 3, 50)
missile_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/shot2.png")

# asteroid images - asteroid_blue.png, asteroid_brown.png, asteroid_blend.png
asteroid_info = ImageInfo([45, 45], [90, 90], 40)
asteroid_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/asteroid_blue.png")

# animated explosion - explosion_orange.png, explosion_blue.png, explosion_blue2.png, explosion_alpha.png
explosion_info = ImageInfo([64, 64], [128, 128], 17, 24, True)
explosion_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/explosion_alpha.png")

# sound assets purchased from sounddogs.com, please do not redistribute
# .ogg versions of sounds are also available, just replace .mp3 by .ogg
soundtrack = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/soundtrack.mp3")
missile_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/missile.mp3")
missile_sound.set_volume(.5)
ship_thrust_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/thrust.mp3")
explosion_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/explosion.mp3")
hs_sound = simplegui.load_sound("https://dl.dropboxusercontent.com/s/ypnvaesedb1y2th/Highscore.mp3")
life_sound = simplegui.load_sound("https://dl.dropboxusercontent.com/s/ar77l9x2ohqe95o/1life.mp3")
# helper functions to handle transformations
def angle_to_vector(ang):
    return [math.cos(ang), math.sin(ang)]

def dist(p,q):
    return math.sqrt((p[0]-q[0])**2+(p[1]-q[1])**2)



# Ship class
class Ship:

    def __init__(self, pos, vel, angle, image, info):
        self.pos = [pos[0],pos[1]]
        self.vel = [vel[0],vel[1]]
        self.thrust = False
        self.angle = angle
        self.angle_vel = 0
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        
    def draw(self,canvas):
        if self.thrust:
            canvas.draw_image(self.image, [self.image_center[0] + self.image_size[0], self.image_center[1]] , self.image_size,
                              self.pos, self.image_size, self.angle)
        else:
            canvas.draw_image(self.image, self.image_center, self.image_size,
                              self.pos, self.image_size, self.angle)
        # canvas.draw_circle(self.pos, self.radius, 1, "White", "White")

    def update(self):
        # update angle
        self.angle += self.angle_vel
        
        # update position
        self.pos[0] = (self.pos[0] + self.vel[0]) % width
        self.pos[1] = (self.pos[1] + self.vel[1]) % height

        # update velocity
        if self.thrust:
            acc = angle_to_vector(self.angle)
            self.vel[0] += acc[0] * .1
            self.vel[1] += acc[1] * .1
            
        self.vel[0] *= .99
        self.vel[1] *= .99

    def set_thrust(self, on):
        self.thrust = on
        if on:
            ship_thrust_sound.rewind()
            ship_thrust_sound.play()
        else:
            ship_thrust_sound.pause()
       
    def increment_angle_vel(self):
        self.angle_vel += .1
        
    def decrement_angle_vel(self):
        self.angle_vel -= .1
        
    def shoot(self):
        forward = angle_to_vector(self.angle)
        missile_pos = [self.pos[0] + self.radius * forward[0], self.pos[1] + self.radius * forward[1]]
        missile_vel = [self.vel[0] + 6 * forward[0], self.vel[1] + 6 * forward[1]]
        missile_group.add(Sprite(missile_pos, missile_vel, self.angle, 0, missile_image, missile_info, missile_sound))
    def get_pos(self):
        return self.pos
    def get_radius(self):
        return self.radius
    
    
# Sprite class
class Sprite:
    def __init__(self, pos, vel, ang, ang_vel, image, info, sound = None):
        self.pos = [pos[0],pos[1]]
        self.vel = [vel[0],vel[1]]
        self.angle = ang
        self.angle_vel = ang_vel
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        self.lifespan = info.get_lifespan()
        self.animated = info.get_animated()
        self.age = 0
        if sound:
            sound.rewind()
            sound.play()
   
    def draw(self, canvas):
        if self.animated:
            canvas.draw_image(explosion_image,
                    [self.image_center[0] + self.age * self.image_size[0],
                     self.image_center[1] ],
                     self.image_size, self.pos, self.image_size,self.angle)
        else:
            canvas.draw_image(self.image, self.image_center, self.image_size,
                          self.pos, self.image_size, self.angle)

    def get_pos(self):
        return self.pos
    def get_radius(self):
        return self.radius
    def update(self):
        # update angle
        self.angle += self.angle_vel
        
        # update position
        self.pos[0] = (self.pos[0] + self.vel[0]) % width
        self.pos[1] = (self.pos[1] + self.vel[1]) % height
        self.age += 1
        if self.age < self.lifespan:
            return True
        else:
            return False
    def collide(self, other_object):
        check_with = (self.radius + other_object.get_radius())
        check = math.sqrt((self.pos[0]-other_object.get_pos()[0])**2+(self.pos[1]-other_object.get_pos()[1])**2)
        if check <= check_with:
            return True
        else:
            return False
  
        
# key handlers to control ship   
def keydown(key):
    if key == simplegui.KEY_MAP['left']:
        my_ship.decrement_angle_vel()
    elif key == simplegui.KEY_MAP['right']:
        my_ship.increment_angle_vel()
    elif key == simplegui.KEY_MAP['up']:
        my_ship.set_thrust(True)
    elif key == simplegui.KEY_MAP['space']:
        my_ship.shoot()
        
def keyup(key):
    if key == simplegui.KEY_MAP['left']:
        my_ship.increment_angle_vel()
    elif key == simplegui.KEY_MAP['right']:
        my_ship.decrement_angle_vel()
    elif key == simplegui.KEY_MAP['up']:
        my_ship.set_thrust(False)
        
# mouseclick handlers that reset UI and conditions whether splash image is drawn
def click(pos):
    global life_sound_played, hs_sound_played, started, score, lives, hs_time_lim, life_color, score_color, hs_bool
    center = [width / 2, height / 2]
    size = splash_info.get_size()
    inwidth = (center[0] - size[0] / 2) < pos[0] < (center[0] + size[0] / 2)
    inheight = (center[1] - size[1] / 2) < pos[1] < (center[1] + size[1] / 2)
    if (not started) and inwidth and inheight:
        started = True
    timer.start()
    score = 0
    lives = 3
    hs_time_lim = True
    life_color = "White"
    score_color = "White"
    hs_bool = False
    hs_sound_played = False
    life_sound_played = False
    soundtrack.rewind()
    soundtrack.play()

def draw(canvas):
    global life_sound_played, hs_time_lim, life_color, time, started, lives, score, rock_group, score_color, hs_bool
    
    # animate background
    time += 1
    center = debris_info.get_center()  
    size = debris_info.get_size()
    wtime = (time / 8) % center[0]
    canvas.draw_image(nebula_image, nebula_info.get_center(), nebula_info.get_size(), [width/2, height/2], [width, height])
    canvas.draw_image(debris_image, [center[0]-wtime, center[1]], [size[0]-2*wtime, size[1]], 
                                [width/2+1.25*wtime, height/2], [width-2.5*wtime, height])
    canvas.draw_image(debris_image, [size[0]-wtime, center[1]], [2*wtime + 1, size[1]], 
                                [1.25*wtime, height/2], [2.5*wtime + 1, height])
   # draw UI
    canvas.draw_text("Lives", [50, 50], 22, life_color)
    canvas.draw_text("Score", [width - 100, 50], 22, "White")
    canvas.draw_text(str(lives), [50, 80], 22, life_color)
    canvas.draw_text(str(score), [width -100, 80], 22, score_color)
   
    # draw ship and sprites
    my_ship.draw(canvas)
    process_sprite_group(canvas, rock_group)
    process_sprite_group(canvas, missile_group)
    
    # update ship and sprites
    my_ship.update()
    lives -= group_collide(rock_group, my_ship)
    score += 10 * group_group_collide(missile_group, rock_group)
    if lives < 1:
        started = False
        rock_group = set([])
        
    #check for high score
    if hs(score) and hs_time_lim:
        score_color = "Red"
        if time % 400 == 0:
            hs_time_lim = False
        elif time % 40 < 20:
            canvas.draw_text("You have a new High Score!", [width/2 - 175,50], 24, "DarkRed", "monospace")
        
        else:
            canvas.draw_text("You have a new High Score!", [width/2 - 175, 50], 24, "Red", "monospace")
            
    #update life_color
    if lives == 1:
        if not life_sound_played:
            life_sound.play()
            life_sound_played = True
        if time % 30 < 15:
            life_color = "Red"
        else:
             life_color = "DarkRed"
        
        
    # draw splash screen if not started
    if not started:
        canvas.draw_image(splash_image, splash_info.get_center(), 
                          splash_info.get_size(), [width/2, height/2], 
                          splash_info.get_size())
        timer.stop()
        soundtrack.pause()

# timer handler that spawns a rock    
def rock_spawner():
    global rock_group
    rock_pos = [random.randrange(0, width), random.randrange(0, height)]
    rock_vel = [(random.random() * .6 - .3)* score/20, (random.random() * .6 - .3)*score/20]
    rock_avel = random.random() * .2 - .1
    rock = Sprite(rock_pos, rock_vel, 0, rock_avel, asteroid_image, asteroid_info)
    if len(rock_group) < 12 and not rock.collide(my_ship):
        rock_group.add(rock)
def process_sprite_group(canvas, set_name):
    global explosion_group
    remove_group = set([])
    for i in set_name:
        if i.update() == False:
            remove_group.add(i)           
        i.draw(canvas)
    set_name.difference_update(remove_group)
    
    # process explosions
    exploded = set([])
    for e in explosion_group:
        e.draw(canvas)
        keep = e.update()
        if keep == False:
            exploded.add(e)
    for e in exploded:
        explosion_group.remove(e)
        
        
        
        
def group_collide(group, other_object):
    global missile_group_remove, explosion_group
    group_remove = set([])
    missile_group_remove = set([])
    for i in group:
        if i.collide(other_object):
            group_remove.add(i)
            missile_group_remove.add(other_object)
    group.difference_update(group_remove)
    

    for r in group_remove:
        explosion = Sprite(r.get_pos(), [0,0], 0, 0, explosion_image, explosion_info, explosion_sound)
        explosion_group.add(explosion)
    return len(group_remove)

    
def group_group_collide(group1, group2):
    score_counter = 0
    for d in group1:
        score_counter += group_collide(group2, d)
        group1.difference_update(missile_group_remove)
    return score_counter

def hs(score):
    global high_score, hs_bool, hs_sound_played
    if score >= high_score:
        hs_bool = True
        high_score = score
        if not hs_sound_played:
            hs_sound.play()
            hs_sound_played = True
    else:
        hs_bool = False
    return hs_bool

# initialize stuff
frame = simplegui.create_frame("Asteroids", width, height, control_width)

# initialize ship and two sprites
my_ship = Ship([width / 2, height / 2], [0, 0], 0, ship_image, ship_info)
rock_group = set([])
missile_group = set([])

# register handlers
frame.set_keyup_handler(keyup)
frame.set_keydown_handler(keydown)
frame.set_mouseclick_handler(click)
frame.set_draw_handler(draw)

timer = simplegui.create_timer(1000.0, rock_spawner)

# get things rolling
timer.start()
frame.start()
