#!/usr/bin/python3
from math import sin,cos,sqrt,dist
from copy import copy
from tkinter import filedialog as fd
import pygame
import sys
import time

################################################################################
#display
FOV_X = 1.5
FOV_Y = 1.0
RES_X = 1500
RES_Y = 1000
#theme
TRIANGLE_COLOR = [255,255,255]
WIREFRAME_COLOR = [128,128,128]
VERTICES_COLOR = [0,255,0]
NORMALS_COLOR = [255,255,0]
BACKGROUND_COLOR = [0,0,0]
UI_COLOR = [100,100,100]
TEXT_COLOR = [255,255,255]
#movement
ROTATION_SPEED = 2
MOVE_SPEED = 5
################################################################################

running = True
DIST = 1.0
last_time = 0
delta = 0
is_mouse_pressed = False
is_mouse_just_pressed = False

class V:
    def __init__(self, x,y,z):
        self.x = x
        self.y = y
        self.z = z

    def __repr__(self):
        return "("+str(self.x)+","+str(self.y)+","+str(self.z)+")"
    #calculate 2D coordinates for the screen
    def project2D(self):
        x = (self.x/self.z*DIST+FOV_X/2.0)*RES_X/FOV_X
        y = -(self.y/self.z*DIST-FOV_Y/2.0)*RES_Y/FOV_Y
        return(x,y)
    #calculate rotation using some black magic
    def rotZ(self,xc,yc,angle):
        (self.x, self.y) = ((self.x-xc)*cos(angle)-(self.y-yc)*sin(angle)+xc,
                            (self.x-xc)*sin(angle)+(self.y-yc)*cos(angle)+yc)

    def rotX(self,zc,yc,angle):
        (self.z, self.y) = ((self.z-zc)*cos(angle)-(self.y-yc)*sin(angle)+zc,
                            (self.z-zc)*sin(angle)+(self.y-yc)*cos(angle)+yc)

    def rotY(self,xc,zc,angle):
        (self.x, self.z) = ((self.x-xc)*cos(angle)-(self.z-zc)*sin(angle)+xc,
                            (self.x-xc)*sin(angle)+(self.z-zc)*cos(angle)+zc)
    #calculate simple movement
    def move(self,dx,dy,dz):
        self.x += dx
        self.y += dy
        self.z += dz

    def draw(self,screen):
        pygame.draw.circle(screen,VERTICES_COLOR,self.project2D(),3)


class L:
    def __init__(self,p1,p2):
        self.p1 = p1
        self.p2 = p2

    def rotZ(self,xc,yc,angle):
        self.p1.rotZ(xc,yc,angle)
        self.p2.rotZ(xc,yc,angle)

    def rotX(self,zc,yc,angle):
        self.p1.rotX(zc,yc,angle)
        self.p2.rotX(zc,yc,angle)

    def rotY(self,xc,zc,angle):
        self.p1.rotY(xc,zc,angle)
        self.p2.rotY(xc,zc,angle)

    def move(self,dx,dy,dz):
        self.p1.move(dx,dy,dz)
        self.p2.move(dx,dy,dz)

    def draw(self,screen):
        pygame.draw.line(screen,'white',self.p1.project2D(),self.p2.project2D(),2)


class T:
    def __init__(self,p1,p2,p3):
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3

    def __repr__(self):
        return "T["+str(self.p1)+","+str(self.p2)+","+str(self.p3)+"]"

    def rotZ(self,xc,yc,angle):
        self.p1.rotZ(xc,yc,angle)
        self.p2.rotZ(xc,yc,angle)
        self.p3.rotZ(xc,yc,angle)

    def rotX(self,zc,yc,angle):
        self.p1.rotX(zc,yc,angle)
        self.p2.rotX(zc,yc,angle)
        self.p3.rotX(zc,yc,angle)

    def rotY(self,xc,zc,angle):
        self.p1.rotY(xc,zc,angle)
        self.p2.rotY(xc,zc,angle)
        self.p3.rotY(xc,zc,angle)

    def move(self,dx,dy,dz):
        self.p1.move(dx,dy,dz)
        self.p2.move(dx,dy,dz)
        self.p3.move(dx,dy,dz)

    def draw(self,screen):
        normal = self.normal()
        c = self.center()
        #from now we treat c as vector, not point
        #it now points from camera to triangle
        #get length of c
        l = sqrt(c.x*c.x+c.y*c.y+c.z*c.z)
        #normalize c to length 1 + invert direction
        c.x = -c.x / l
        c.y = -c.y / l
        c.z = -c.z / l
        #calculate dot product between two vectors
        #this will return between 1.0 (if angle is 0) and 0.0 (if angle is 90)
        #source = https://www.wikihow.com/Find-the-Angle-Between-Two-Vectors
        dotproduct = normal.x * c.x + normal.y * c.y + normal.z * c.z

        #shorten nomal so it looks better
        normal.x = normal.x / 2
        normal.y = normal.y / 2
        normal.z = normal.z / 2

        if set.hidden_triangles.state:
            light = abs(155*dotproduct)+100
            if set.triangles.state:
                color = (light*TRIANGLE_COLOR[0]/255,
                        light*TRIANGLE_COLOR[1]/255,
                        light*TRIANGLE_COLOR[2]/255)
                pygame.draw.polygon(screen,color,[self.p1.project2D(),self.p2.project2D(),self.p3.project2D()])
            if set.wireframe.state:
                pygame.draw.polygon(screen,WIREFRAME_COLOR,[self.p1.project2D(),self.p2.project2D(),self.p3.project2D()],1)
            if set.verticies.state:
                self.p1.draw(screen)
                self.p2.draw(screen)
                self.p3.draw(screen)
                c.draw(screen)
            if set.normals.state:
                point1 = self.center()
                point2 = V((point1.x + normal.x),(point1.y + normal.y),(point1.z + normal.z))
                pygame.draw.line(screen,NORMALS_COLOR,point1.project2D(),point2.project2D(),1)

        else:
            if (dotproduct>=0):
                light = abs(155*dotproduct)+100
                if set.triangles.state:
                    color = (light*TRIANGLE_COLOR[0]/255,
                             light*TRIANGLE_COLOR[1]/255,
                             light*TRIANGLE_COLOR[2]/255)
                    pygame.draw.polygon(screen,color,[self.p1.project2D(),self.p2.project2D(),self.p3.project2D()])
                if set.wireframe.state:
                    pygame.draw.polygon(screen,WIREFRAME_COLOR,[self.p1.project2D(),self.p2.project2D(),self.p3.project2D()],1)
                if set.verticies.state:
                    self.p1.draw(screen)
                    self.p2.draw(screen)
                    self.p3.draw(screen)
                    c.draw(screen)
                if set.normals.state:
                    point1 = self.center()
                    point2 = V((point1.x + normal.x),(point1.y + normal.y),(point1.z + normal.z))
                    pygame.draw.line(screen,NORMALS_COLOR,point1.project2D(),point2.project2D(),1)

    def center(self):
        #calculate the center of the triangle
        return V((self.p1.x+self.p2.x+self.p3.x)/3.0,
                 (self.p1.y+self.p2.y+self.p3.y)/3.0,
                 (self.p1.z+self.p2.z+self.p3.z)/3.0)

    def normal(self):
        #calculate vector between p1 and p2
        ux = self.p2.x-self.p1.x
        uy = self.p2.y-self.p1.y
        uz = self.p2.z-self.p1.z
        #calculate vector between p1 and p3
        vx = self.p3.x-self.p1.x
        vy = self.p3.y-self.p1.y
        vz = self.p3.z-self.p1.z
        # calculate normal vector
        # source = https://www.khronos.org/opengl/wiki/Calculating_a_Surface_Normal
        x=uy*vz-uz*vy
        y=uz*vx-ux*vz
        z=ux*vy-uy*vx
        # calculate length of normal vector so it can be shortend in the next step to 1
        l=sqrt((x*x)+(y*y)+(z*z))
        # return normal vector normalized to length=1
        return V(x/l, y/l, z/l)

class Mesh:
    def __init__(self):
        self.verticies = []
        self.triangles = []
        #load the .obj file
        try:
            file = open(sys.argv[1],'r')
        except Exception as e:
            file = open(fd.askopenfilename(),'r')
        
        for line in file.readlines():
            #remove last character "/n"
            line = line[:-1]
            #change window name, to name found in .obj file
            if line[0] == "o":
                pygame.display.set_caption(line[2:])
            #read verticies from the file and create them
            if line[0] == "v":
                line = line[2:]
                (x,y,z)=line.split(' ')
                self.verticies.append(V(float(x),float(y),float(z)))
            #read triangle from file and create it
            if line[0] == "f":
                line = line[2:]
                (p1,p2,p3)=line.split(' ')
                self.triangles.append(T(copy(self.verticies[int(p1)-1]),
                                        copy(self.verticies[int(p2)-1]),
                                        copy(self.verticies[int(p3)-1])))

    def rotZ(self,xc,yc,angle):
        for t in self.triangles:
            t.rotZ(xc,yc,angle)

    def rotX(self,zc,yc,angle):
        for x in self.triangles:
            x.rotX(zc,yc,angle)

    def rotY(self,xc,zc,angle):
        for x in self.triangles:
            x.rotY(xc,zc,angle)

    def move(self,dx,dy,dz):
        for t in self.triangles:
            t.move(dx,dy,dz)
    #calculate center of object by getting the average of all triangle positions
    def center(self):
        x = 0
        y = 0
        z = 0
        for p in self.triangles:
            nc = p.center()
            x+=nc.x
            y+=nc.y
            z+=nc.z
        return(V(x/len(self.triangles),
                 y/len(self.triangles),
                 z/len(self.triangles)))


    def __repr__(self):
        return "Mesh:"+" ".join(str(t) for t in self.triangles)

    def draw(self, screen):
        list = []
        for i in range(len(self.triangles)):
            pos = self.triangles[i].center()
            list.append([i,pos.z])
        list = sorted(list, reverse=True, key=lambda pair:pair[1])
        for i in list:
            self.triangles[i[0]].draw(screen)

class Option:
    def __init__(self,name,pos,state):
        self.name = name
        self.pos = pos
        self.state = state

    def update_state(self):
        if is_mouse_pressed:
            if dist(self.pos,pygame.mouse.get_pos())<7:
                if self.state:
                    self.state = False
                else:
                    self.state = True

    def update(self):
        self.update_state()
        if self.state:
            pygame.draw.circle(screen,TEXT_COLOR,self.pos,7)
        else:
            pygame.draw.circle(screen,TEXT_COLOR,self.pos,7,2)
        screen.blit(font.render(self.name, False, TEXT_COLOR), [self.pos[0]-178,self.pos[1]-15])

class Settings:
    def __init__(self):
        self.hidden = True
        self.wireframe = Option("Wireframe",[188,50],True)
        self.triangles = Option("Triangles",[188,75],True)
        self.verticies = Option("Vertices",[188,100],False)
        self.normals = Option("Normals",[188,125],False)
        self.hidden_triangles = Option("hidden Triangles",[188,150],False)

    def update_state(self):
        if is_mouse_pressed:
            pos = pygame.mouse.get_pos()
            if pos[0] > 5 and pos[0] < 205:
                if pos[1] > 5 and pos[1] < 40:
                    if self.hidden:
                        self.hidden = False
                    else:
                        self.hidden = True
    def update(self):
        self.update_state()
        if self.hidden:
            pygame.draw.rect(screen,UI_COLOR,[5,5,200,35])
            screen.blit(font.render("Settings", False, TEXT_COLOR), (10,10))
            pygame.draw.polygon(screen,TEXT_COLOR,[(183,15),(188.5,25),(193,15)])
        else:
            pygame.draw.rect(screen,UI_COLOR,[5,5,200,160])
            screen.blit(font.render("Settings", False, TEXT_COLOR), (10,10))
            pygame.draw.polygon(screen,TEXT_COLOR,[(183,25),(188.5,15),(193,25)])

            self.wireframe.update()
            self.triangles.update()
            self.verticies.update()
            self.normals.update()
            self.hidden_triangles.update()


def get_input(object):
    keys = pygame.key.get_pressed()
    center = object.center()

    if keys[pygame.K_UP]:
        object.rotX(center.z,center.y,ROTATION_SPEED*delta)
    if keys[pygame.K_DOWN]:
        object.rotX(center.z,center.y,-ROTATION_SPEED*delta)

    if keys[pygame.K_LEFT]:
        object.rotY(center.x,center.z,-ROTATION_SPEED*delta)
    if keys[pygame.K_RIGHT]:
        object.rotY(center.x,center.z,ROTATION_SPEED*delta)

    if keys[pygame.K_PAGEUP]:
        object.rotZ(center.x,center.y,ROTATION_SPEED*delta)
    if keys[pygame.K_PAGEDOWN]:
        object.rotZ(center.x,center.y,-ROTATION_SPEED*delta)

    if keys[pygame.K_e]:
        object.move(0,-MOVE_SPEED*delta,0)
    if keys[pygame.K_q]:
        object.move(0,MOVE_SPEED*delta,0)

    if keys[pygame.K_d]:
        object.move(-MOVE_SPEED*delta,0,0)
    if keys[pygame.K_a]:
        object.move(MOVE_SPEED*delta,0,0)

    if keys[pygame.K_w]:
        object.move(0,0,-MOVE_SPEED*delta)
    if keys[pygame.K_s]:
        object.move(0,0,MOVE_SPEED*delta)

def get_mouse_input():
    global is_mouse_pressed
    global is_mouse_just_pressed
    mouse_presses = pygame.mouse.get_pressed()

    if mouse_presses[0]:
        if is_mouse_pressed == False and is_mouse_just_pressed == False:
            is_mouse_pressed = True
            is_mouse_just_pressed = True
        else:
            is_mouse_pressed = False
    else:
        is_mouse_pressed = False
        is_mouse_just_pressed = False

pygame.init()
screen = pygame.display.set_mode([RES_X, RES_Y],pygame.RESIZABLE)
font = pygame.font.Font('font.ttf', 20)

obj = Mesh()
set = Settings()
obj.move(0,0,10)

while running:
    RES_X,RES_Y = screen.get_size()
    FOV_X = RES_X / 1000
    FOV_Y = RES_Y / 1000

    delta = time.time() - last_time
    last_time = time.time()

    screen.fill(BACKGROUND_COLOR)
    obj.draw(screen)
    set.update()
    get_input(obj)
    get_mouse_input()
    pygame.display.update()
    for event in pygame.event.get():
        keys = pygame.key.get_pressed()
        if event.type == pygame.QUIT or keys[pygame.K_ESCAPE]:
            running = False
