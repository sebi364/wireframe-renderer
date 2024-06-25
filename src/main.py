import pygame
import asyncio
import time
from copy import copy
from math import sin,cos,sqrt

#####################################################################################################################
BACKGROUND_COLOR = [0,0,0]
VERTICES_COLOR = [0,255,0]
TRIANGLE_COLOR = [255,255,255]
WIREFRAME_COLOR = [128,128,128]
NORMALS_COLOR = [255,255,0]

ROTATION_SPEED = 2
MOVE_SPEED = 5
#####################################################################################################################
last_time = 0
delta = 0

draw_Vertices = False
draw_Triangels = True
draw_Normals = False
draw_Wireframe = True
draw_Hidden_Triangels = False

class V:
    def __init__(self, x,y,z):
        self.x = x
        self.y = y
        self.z = z

    def __repr__(self):
        return "("+str(self.x)+","+str(self.y)+","+str(self.z)+")"
    #calculate 2D coordinates for the screen

    def project2D(self, screen):
        FOV_X = 1.5
        FOV_Y = 1.0
        RES_X, RES_Y = screen.get_size()
        DIST = 1.0

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
        pygame.draw.circle(screen,VERTICES_COLOR,self.project2D(screen),3)

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

        if draw_Hidden_Triangels:
            light = abs(155*dotproduct)+100
            if draw_Triangels:
                color = (light*TRIANGLE_COLOR[0]/255,
                        light*TRIANGLE_COLOR[1]/255,
                        light*TRIANGLE_COLOR[2]/255)
                pygame.draw.polygon(screen,color,[self.p1.project2D(screen),self.p2.project2D(screen),self.p3.project2D(screen)])
            if draw_Wireframe:
                pygame.draw.polygon(screen,WIREFRAME_COLOR,[self.p1.project2D(screen),self.p2.project2D(screen),self.p3.project2D(screen)],1)
            if draw_Vertices:
                self.p1.draw(screen)
                self.p2.draw(screen)
                self.p3.draw(screen)
                c.draw(screen)
            if draw_Normals:
                point1 = self.center()
                point2 = V((point1.x + normal.x),(point1.y + normal.y),(point1.z + normal.z))
                pygame.draw.line(screen,NORMALS_COLOR,point1.project2D(screen),point2.project2D(screen),1)

        else:
            if (dotproduct>=0):
                light = abs(155*dotproduct)+100
                if draw_Triangels:
                    color = (light*TRIANGLE_COLOR[0]/255,
                             light*TRIANGLE_COLOR[1]/255,
                             light*TRIANGLE_COLOR[2]/255)
                    pygame.draw.polygon(screen,color,[self.p1.project2D(screen),self.p2.project2D(screen),self.p3.project2D(screen)])
                if draw_Wireframe:
                    pygame.draw.polygon(screen,WIREFRAME_COLOR,[self.p1.project2D(screen),self.p2.project2D(screen),self.p3.project2D(screen)],1)
                if draw_Vertices:
                    self.p1.draw(screen)
                    self.p2.draw(screen)
                    self.p3.draw(screen)
                    c.draw(screen)
                if draw_Normals:
                    point1 = self.center()
                    point2 = V((point1.x + normal.x),(point1.y + normal.y),(point1.z + normal.z))
                    pygame.draw.line(screen,NORMALS_COLOR,point1.project2D(screen),point2.project2D(screen),1)

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

class M:
    def __init__(self):
        self.verticies = []
        self.triangles = []
        self.loadfile('Models/plane.obj')

    def loadfile(self, filedir):
        self.verticies = []
        self.triangles = []
        file = open(filedir,'r')
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
        self.move(0,0,10)

    def draw(self, screen):
        list = []
        for i in range(len(self.triangles)):
            pos = self.triangles[i].center()
            list.append([i,pos.z])
        list = sorted(list, reverse=True, key=lambda pair:pair[1])
        for i in list:
            self.triangles[i[0]].draw(screen)
    
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
    
    if keys[pygame.K_b]:
        global draw_Vertices
        if draw_Vertices:
            draw_Vertices = False
        else:
            draw_Vertices = True
        time.sleep(0.2)

    if keys[pygame.K_c]:
        global draw_Triangels
        if draw_Triangels:
            draw_Triangels = False
        else:
            draw_Triangels = True
        time.sleep(0.2)


    if keys[pygame.K_n]:
        global draw_Normals
        if draw_Normals:
            draw_Normals = False
        else:
            draw_Normals = True
        time.sleep(0.2)


    if keys[pygame.K_v]:
        global draw_Wireframe
        if draw_Wireframe:
            draw_Wireframe = False
        else:
            draw_Wireframe = True
        time.sleep(0.2)


    if keys[pygame.K_m]:
        global draw_Hidden_Triangels
        if draw_Hidden_Triangels:
            draw_Hidden_Triangels = False
        else:
            draw_Hidden_Triangels = True
        time.sleep(0.2)
    
    if keys[pygame.K_1]:
        object.loadfile('Models/cube.obj')
        time.sleep(0.2)
    
    if keys[pygame.K_2]:
        object.loadfile('Models/plane.obj')
        time.sleep(0.2)
    
    if keys[pygame.K_3]:
        object.loadfile('Models/monkey.obj')
        time.sleep(0.2)
    
    if keys[pygame.K_4]:
        object.loadfile('Models/porsche.obj')
        time.sleep(0.2)


async def main():
    global delta
    global last_time

    screen = pygame.display.set_mode()
    pygame.display.flip()

    running = True

    Mesh = M()

    while running:
        delta = time.time() - last_time
        last_time = time.time()
        get_input(Mesh)
        screen.fill(BACKGROUND_COLOR)
        Mesh.draw(screen)
        pygame.display.update()
        await asyncio.sleep(0)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

asyncio.run(main())