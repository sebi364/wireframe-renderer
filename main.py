#!/usr/bin/python3
from math import sin,cos,sqrt
from copy import copy
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
MESH_COLOR = [255,255,255]
WIREFRAME_COLOR = [128,128,128]
#visibility
RENDER_WIREFRAME = True
RENDER_TRIANGLES = True
RENDER_HIDDEN_TRIANGLES = False
#movement
ROTATION_SPEED = 2
MOVE_SPEED = 5
################################################################################

running = True
DIST = 1.0
last_time = 0
delta = 0

class V:
    def __init__(self, x,y,z):
        self.x = x
        self.y = y
        self.z = z

    def __repr__(self):
        return "("+str(self.x)+","+str(self.y)+","+str(self.z)+")"

    def project2D(self):
        x = (self.x/self.z*DIST+FOV_X/2.0)*RES_X/FOV_X
        y = -(self.y/self.z*DIST-FOV_Y/2.0)*RES_Y/FOV_Y
        return(x,y)

    def rotZ(self,xc,yc,angle):
        (self.x, self.y) = ((self.x-xc)*cos(angle)-(self.y-yc)*sin(angle)+xc,
                            (self.x-xc)*sin(angle)+(self.y-yc)*cos(angle)+yc)

    def rotX(self,zc,yc,angle):
        (self.z, self.y) = ((self.z-zc)*cos(angle)-(self.y-yc)*sin(angle)+zc,
                            (self.z-zc)*sin(angle)+(self.y-yc)*cos(angle)+yc)

    def rotY(self,xc,zc,angle):
        (self.x, self.z) = ((self.x-xc)*cos(angle)-(self.z-zc)*sin(angle)+xc,
                            (self.x-xc)*sin(angle)+(self.z-zc)*cos(angle)+zc)
    def move(self,dx,dy,dz):
        self.x += dx
        self.y += dy
        self.z += dz

    def draw(self,screen):
        pygame.draw.circle(screen,'red',self.project2D(),10,2)


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
        l = sqrt(c.x*c.x+c.y*c.y+c.z*c.z)
        c.x = -c.x / l
        c.y = -c.y / l
        c.z = -c.z / l
        dot = normal.x * c.x + normal.y * c.y + normal.z * c.z
        if RENDER_HIDDEN_TRIANGLES:
            light = abs(155*dot)+100
            color = (light*MESH_COLOR[0]/255, light*MESH_COLOR[1]/255, light*MESH_COLOR[2]/255)
            if RENDER_TRIANGLES:
                pygame.draw.polygon(screen,color,[self.p1.project2D(),self.p2.project2D(),self.p3.project2D()])
            if RENDER_WIREFRAME:
                pygame.draw.polygon(screen,WIREFRAME_COLOR,[self.p1.project2D(),self.p2.project2D(),self.p3.project2D()],1)
        else:
            if (dot>=0):
                light = abs(155*dot)+100
                color = (light*MESH_COLOR[0]/255, light*MESH_COLOR[1]/255, light*MESH_COLOR[2]/255)
                if RENDER_TRIANGLES:
                    pygame.draw.polygon(screen,color,[self.p1.project2D(),self.p2.project2D(),self.p3.project2D()])
                if RENDER_WIREFRAME:
                    pygame.draw.polygon(screen,WIREFRAME_COLOR,[self.p1.project2D(),self.p2.project2D(),self.p3.project2D()],1)


    def center(self):
        return V((self.p1.x+self.p2.x+self.p3.x)/3.0, (self.p1.y+self.p2.y+self.p3.y)/3.0, (self.p1.z+self.p2.z+self.p3.z)/3.0)

    def normal(self):
        ux = self.p2.x-self.p1.x
        uy = self.p2.y-self.p1.y
        uz = self.p2.z-self.p1.z

        vx = self.p3.x-self.p1.x
        vy = self.p3.y-self.p1.y
        vz = self.p3.z-self.p1.z

        x=uy*vz-uz*vy
        y=uz*vx-ux*vz
        z=ux*vy-uy*vx
        l=sqrt((x*x)+(y*y)+(z*z))
        return V(x/l, y/l, z/l)

class Mesh:
    def __init__(self):
        self.verticies = []
        self.triangles = []

        file = open(sys.argv[1],'r')
        for line in file.readlines():
            line = line[:-1]
            if line[0] == "o":
                pygame.display.set_caption(line[2:])
            if line[0] == "v":
                line = line[2:]
                (x,y,z)=line.split(' ')
                self.verticies.append(V(float(x),float(y),float(z)))
            if line[0] == "f":
                line = line[2:]
                (p1,p2,p3)=line.split(' ')
                self.triangles.append(T(copy(self.verticies[int(p1)-1]),copy(self.verticies[int(p2)-1]),copy(self.verticies[int(p3)-1])))

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

    def center(self):
        x = 0
        y = 0
        z = 0
        for p in self.triangles:
            nc = p.center()
            x+=nc.x
            y+=nc.y
            z+=nc.z
        return(V(x/len(self.triangles),y/len(self.triangles),z/len(self.triangles)))


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

pygame.init()
screen = pygame.display.set_mode([RES_X, RES_Y])


obj = Mesh()

obj.move(0,0,10)

while running:
    delta = time.time() - last_time
    last_time = time.time()

    screen.fill('black')
    obj.draw(screen)
    get_input(obj)
    pygame.display.update()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
