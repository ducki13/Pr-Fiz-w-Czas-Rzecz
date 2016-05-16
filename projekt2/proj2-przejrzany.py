#!/usr/bin/python
#-*- coding: utf-8 -*-

u"""Na podstawie kursu H. S. Kinsley, z kanału sentdex, YouTube.

Na tym kanale można znaleźć dodatkowa pomoc w instalacji PyOpenGL na Windowsa."""

import pygame
import math
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *


class Vector:
    def __init__(self, **kwargs):
        if 'x' in kwargs:
            self.x = kwargs['x']
        if 'y' in kwargs:
            self.y = kwargs['y']
        if 'z' in kwargs:
            self.z = kwargs['z']
        if 't' in kwargs:
            self.x, self.y, self.z = kwargs['t']
        if 'l' in kwargs:
            l = kwargs['l']
            self.x = l[0]
            self.y = l[1]
            self.z = l[2]
        self.xlen = 1
        self.ylen = 3

    def __getitem__(self, item):
        if item == 0:
            return self.x
        if item == 1:
            return self.y
        return self.z

    def add(self, other):
        return Vector(x=self.x+other.x, y=self.y+other.y, z=self.z+other.z)

    def sub(self, other):
        return Vector(x=self.x-other.x, y=self.y-other.y, z=self.z-other.z)

    def mult(self, a):
        return Vector(x=self.x*a, y=self.y*a, z=self.z*a)

    @staticmethod
    def dot_product(A, B):
        Acoord = A.get_coord()
        Bcoord = B.get_coord()
        ret = 0
        for i in range(0, 3):
            ret += Acoord[i]*Bcoord[i]
        return ret

    @staticmethod
    def vector_product(A, B):
        return Vector(x=A.y*B.z - A.z*B.y,
                      y=-(A.x*B.z - A.z*B.x),
                      z=A.x*B.y - A.y*B.x)

    def get_coord(self):
        return self.x, self.y, self.z

    @staticmethod
    def get_vector_with_direction_and_len(V, len):
        coord = V.get_coord()
        lenV = math.sqrt(Vector.dot_product(V, V))
        return Vector(x=len*coord[0]/lenV, y=len*coord[1]/lenV, z=len*coord[2]/lenV)

    def normalize(self):
        len = 1.0/math.sqrt(Vector.dot_product(self, self))
        return Vector(x=self.x/len, y=self.y/len, z=self.z/len)

    def __str__(self):
        return "[" + str(self.x) + ", " + str(self.y) + ", " + str(self.z) + "]"


class Matrix:
    M = ((0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, 0.0, 0.0))

    def __init__(self, **kwargs):
        if 't' in kwargs:
            self.M = kwargs['t']
        if 'v' in kwargs:
            v = kwargs['v']
            self.M = (v[0].get_coord(), v[1].get_coord(), v[2].get_coord())
        if 'l' in kwargs:
            l = kwargs['l']
            self.M = (tuple(l[0]), tuple(l[1]), tuple(l[2]))
        self.xlen = 3
        self.ylen = 3

    def __getitem__(self, item):
        x, y = item
        return self.M[x][y]

    def add(self, other):
        ret = [list(self.M[0]), list(self.M[1]), list(self.M[2])]
        for i, row in enumerate(self.M):
            for j, _ in enumerate(row):
                ret[i][j] += other.M[i][j]

        return Matrix(l=ret)

    def mult(self, other):
        if other.xlen == 1:
            ret = [0.0, 0.0, 0.0]
            for i in range(0, 3):
                for j in range(0, 3):
                    ret[i] += self.M[i][j]*other[j]

            return Vector(x=ret[0], y=ret[1], z=ret[2])

        ret = [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]
        for i in range(0, self.xlen):
            for j in range(0, other.ylen):
                for k in range(0, self.ylen):
                    ret[i][j] += self.M[i][k] * other.M[k][j]

        return Matrix(l=ret)

    def mult_number(self, number):
        ret = [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]
        for i in range(0, 3):
            for j in range(0, 3):
                ret[i][j] = number * self.M[i][j]

        return Matrix(l=ret)

    def transpose(self):
        ret = [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]
        for i in range(0, 3):
            for j in range(0, 3):
                ret[i][j] = self.M[j][i]

        return Matrix(l=ret)

    def det(self):
        a, b, c = self.M
        a11, a12, a13 = a
        a21, a22, a23 = b
        a31, a32, a33 = c
        return a11*a22*a33 + a21*a32*a13 + a31*a12*a23 - a11*a32*a23 - a31*a22*a13 - a21*a12*a33

    def inverse(self):
        a, b, c = self.M
        a11, a12, a13 = a
        a21, a22, a23 = b
        a31, a32, a33 = c
        det_inv = 1.0/self.det()
        res = [[a22*a33-a23*a32, a13*a32-a12*a33, a12*a23-a13*a22],
               [a23*a31-a21*a33, a11*a33-a13*a31, a13*a21-a11*a23],
               [a21*a32-a22*a32, a12*a31-a11*a32, a11*a22-a12*a21]]

        for i in range(0, 3):
            for j in range(0, 3):
                res[i][j] *= det_inv

        return Matrix(l=res)

    def gramm_schmidt(self):
        res = [Vector(x=0.0, y=0.0, z=0.0), Vector(x=0.0, y=0.0, z=0.0),
               Vector(x=0.0, y=0.0, z=0.0)]
        R = [Vector(t=self.M[0]), Vector(t=self.M[1]),
             Vector(t=self.M[2])]

        res[0] = Vector.normalize(R[0])

        res[1] = Vector.normalize(R[1].sub(res[0].mult(
            Vector.dot_product(R[1], res[0]))))

        res[2] = Vector.normalize(R[2].sub(res[0].mult(
            Vector.dot_product(R[2], res[0])).add(
                res[1].mult(Vector.dot_product(R[2], res[1])))))

        return Matrix(v=res)

    def __str__(self):
        return str(self.M)


class SceneObject:
    vertices = []
    edges = []

    def __init__(self, **kwargs):
        if 'vertices' in kwargs:
            self.vertices = kwargs['vertices']
        if 'masses' in kwargs:
            self.masses = kwargs['masses']

    def get_vertices_coord(self):
        return [x.get_coord() for x in self.vertices]

    def get_vertices(self):
        return self.vertices

    def get_edges(self):
        return self.edges


class CoordinateSystem(SceneObject):
    vertices = [Vector(x=-10, y=0, z=0), Vector(x=10, y=0, z=0),
                Vector(x=0, y=-10, z=0), Vector(x=0, y=10, z=0),
                Vector(x=0, y=0, z=-10), Vector(x=0, y=0, z=10)]

    edges = [(0, 1), (2, 3), (4, 5)]


class Triangle(SceneObject):
    L = Vector(x=0.0, y=0.0, z=0.0)
    R = Matrix(t=((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)))
    R_trans = Matrix()
    W = Matrix()
    w = Vector(x=0.0, y=0.0, z=0.0)
    I = Matrix()
    I_zero_inv = Matrix()
    I_inv = Matrix()
    F = 0.0

    t = 0.0
    dt = 1.0/30.0

    surfaces = [(0, 1, 2, 0)]
    edges = [(0, 1), (1, 2), (2, 0)]

    def get_masses(self):
        return [x.m for x in self.vertices]

    def get_surfaces(self):
        return self.surfaces

    def set_omega(self, w):
        self.w = w

    def set_dt(self, dt):
        self.dt = dt

    def set_force(self, F):
        self.F = F

    ###
    def get_xx(self, p, m):
        return m*(math.sqrt(p.y*p.y + p.z*p.z))

    def get_yy(self, p, m):
        return m*(math.sqrt(p.x*p.x + p.z*p.z))

    def get_zz(self, p, m):
        return m*(math.sqrt(p.x*p.x + p.y*p.y))

    def get_xy(self, p, m):
        return -m*p.x*p.y

    def get_xz(self, p, m):
        return -m*p.x*p.z

    def get_yz(self, p, m):
        return -m*p.y*p.z

    ###
    def countR(self, angle):
        self.R = [[math.cos(angle), -math.sin(angle), 0],
                  [math.sin(angle), math.cos(angle), 0],
                  [0, 0, 1]]

    def countI(self):
        ret = [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]
        a = self.vertices[0]
        b = self.vertices[1]
        c = self.vertices[2]
        ma = self.masses[0]
        mb = self.masses[1]
        mc = self.masses[2]
        ret[0][0] = self.get_xx(a, ma) + self.get_xx(b, mb) + self.get_xx(c, mc)
        ret[1][1] = self.get_yy(a, ma) + self.get_yy(b, mb) + self.get_yy(c, mc)
        ret[2][2] = self.get_zz(a, ma) + self.get_zz(b, mb) + self.get_zz(c, mc)
        ret[0][1] = ret[1][0] = self.get_xy(a, ma) + self.get_xy(b, mb) + self.get_xy(c, mc)
        ret[0][2] = ret[2][0] = self.get_xz(a, ma) + self.get_xz(b, mb) + self.get_xz(c, mc)
        ret[1][2] = ret[2][1] = self.get_yz(a, ma) + self.get_yz(b, mb) + self.get_yz(c, mc)
        self.I = Matrix(l=ret)

    def countW(self):
        x, y, z = self.w.get_coord()
        self.W = Matrix(t=((0, -z, y), (z, 0, -x), (-y, x, 0)))

    def countM(self):
        self.M = self.M

    ###
    def zad1(self):
        for i, x in enumerate(self.vertices):
            v = Vector.vector_product(x, self.w)
            v = v.mult(self.dt)
            self.vertices[i] = self.vertices[i].add(v)
            #self.vertices[i].mult(self.dt)

    def zad2(self):
        #new omega := normalized(omega) -> scale new omega so that it's len := t + 1.0
        self.w = Vector.get_vector_with_direction_and_len(self.w, self.t+1.0)
        self.zad1()
        self.t += self.dt

    #def init_zad3(self, F, p):
    def zad3(self, nr, nrs):
        # print("t")
        # print(str(self.t))
        # #print("@@@@@@@@@@@@@")
        # print("v["+str(nr)+"]")
        # print(str(self.vertices[nr]))
        # print("L")
        # print(str(self.L))
        # print("R")
        # print(str(self.R))
        # print("W")
        # print(str(self.W))
        # print("w")
        # print(str(self.w))

        #W - omega matrix, w - omega vector
        for x in nrs:
            self.vertices[x] = self.R.mult(self.vertices[x])
        #    print "Wierzcholek", self.vertices[x]
        #print "Macierz", self.R
        
        #L_{n+1} = L_{n} + vertex x F * dt
        self.L = self.L.add(Vector.vector_product(self.vertices[nr], self.F).mult(self.dt))

        #R_{n+1} = R_{n} + W_{n} * R_{n} * dt
        self.R = self.R.add(self.W.mult(self.R).mult_number(self.dt))
        #orthogonalize new R_{n+1}
        self.R = self.R.gramm_schmidt()

        #R_trans_{n+1} = transpose(R_{n+1})
        self.R_trans = self.R.transpose()

        #I_inversed_{n+1} = R_{n+1} * I_zero_inv * R_trans_{n+1}, where I_zero_inv is inversed in time 0 matrix I
        self.I_inv = self.R.mult(self.I_zero_inv).mult(self.R_trans)

        #omega vector w_{n+1} = I_inv_{n+1} * L_{n+1}
        self.w = self.I_inv.mult(self.L)

        #change counted vector omega to matrix W
        self.countW()

        #add timestep
        self.t += self.dt

        #orthogonalize R
        #self.R = self.R.gramm_schmidt()
        #self.R_trans = self.R.gramm_schmidt()

        m = self.R.mult(self.R.transpose())
        #print("###############")
        #print(m.M)
        #print("###############")
        #self.I_inv = self.I_inv.gramm_schmidt()

    def zad4(self, stable, nr, nrs):
        v1 = self.vertices[stable].sub(self.vertices[nrs[0]])
        v2 = self.vertices[stable].sub(self.vertices[nrs[1]])
        force = Vector.vector_product(v1, v2)
        self.set_force(force.normalize())
        self.zad3(nr, nrs)


def display_triangle(csys, t):
    #triangle surfaces
    glBegin(GL_QUADS)
    glColor3fv((0, 1, 0))
    for surface in t.get_surfaces():
        for vertex in surface:
            glVertex3fv(t.get_vertices_coord()[vertex])
    glEnd()

    #triangle edges
    glBegin(GL_LINES)
    glColor3fv((1, 0, 0))
    for edge in t.get_edges():
        for vertex in edge:
            glVertex3fv(t.get_vertices_coord()[vertex])
    glEnd()

    #coordinate system
    glBegin(GL_LINES)
    glColor3fv((0, 0, 1))
    for edge in csys.get_edges():
        for vertex in edge:
            glVertex3fv(csys.get_vertices_coord()[vertex])
    glEnd()


def main():
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

    #zakres widzenia, aspect ratio, obszar w którym mogą sie pojawic obiekty
    gluPerspective(70, (display[0]/display[1]), -10.0, 10.0)

    glTranslatef(0.0, 0.0, -15.0) # Przesuwa kamerę w stosunku
    # do środka układu współrzędnych.

    glRotatef(150.0, 0.0, 1.0, 0.0) # Funkcja obracająca kamerę. Pierwsze
    # zmienna to kąt obrotu, pozostałe jego oś.

    #counterclowise
    tri = Triangle(vertices=[Vector(x=0, y=0, z=0), Vector(x=0, y=-1, z=1), Vector(x=0, y=2, z=1)], masses=(1, 3, 5))
    csys = CoordinateSystem()

    #set values
    tri.set_dt(1.0/60.0)
    tri.set_omega(Vector(x=1.0, y=1.0, z=0.0))
    tri.set_force(Vector(x=0, y=1.0, z=0.0))

    #initial I matrix
    tri.countI()
    tri.I_zero_inv = tri.I.inverse()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        display_triangle(csys, tri)
        pygame.display.flip()
        pygame.time.wait(120)
        #for zad 1-2 pygame.time.wait(60)
        #for zad 3-6 pygame.time.wait(120)

        #zad1
        #tri.zad1()
        #zad2
        #tri.zad2()
        #zad3
        #tri.zad3(1, [1, 2])
        #zad4
        #tri.zad3(2, [1, 2])
        #zad5
        #tri.zad3(0, [0, 1])
        #zad6
        tri.zad4(0, 2, [1, 2])


main()
