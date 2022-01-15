import pygame as pg
from math import pi, sin, cos, sqrt, exp

from pygame.version import ver


class Vertex:
    def __init__(self, pos, velocity, m):
        self.pos = pos
        self.velocity = velocity
        self.velocity_s1 = velocity
        self.velocity_s2 = velocity
        self.velocity_pr = velocity
        self.velocity_g = velocity
        self.accel = pg.Vector2()
        self.force = pg.Vector2()
        self.force_s1 = pg.Vector2()
        self.force_s2 = pg.Vector2()
        self.force_pr = pg.Vector2()
        self.force_g = pg.Vector2()
        self.m = m


class Spring:
    def __init__(self, A, B, k):
        self.A = A
        self.B = B
        self.k = k
        self.length = (self.A.pos - self.B.pos).length()


class Body:
    def __init__(self, pos_center, r, n):
        self.pos_center = pos_center
        self.pressure = 1
        self.volume = 1

        self.friction = 10
        self.n = 0
        self.nRT = self.n*8.31*300
        self.p0 = 0
        self.g = pg.Vector2()

        self.vertexes = []
        self.springs = []
        self.generate_vertexes(r, n)
    
    def generate_vertexes(self, r, n):
        phi = 2*pi/n
        # Создание вершин
        for v in range(n):
            self.vertexes.append(Vertex(self.pos_center + r*pg.Vector2(cos(-phi*v), sin(-phi*v)), pg.Vector2(), 10))
        
        # Создание пружин
        for s in range(len(self.vertexes)):
            self.springs.append(Spring(self.vertexes[s], self.vertexes[s-1], 2*10**4))

    def update(self, dt):
        self.restore()
        self.recalc_pos_center()
        self.recalc_volume()

        self.pressure = (self.nRT/self.volume - self.p0)

        for v in self.vertexes:
            self.collide(v)

        for s in self.springs:
            dir = s.B.pos - s.A.pos
            dist = dir.length()

            # Сила упругости
            '''
            s.A.force_s1 += s.k*(dist - s.length)*dir/dist
            s.B.force_s2 += -s.k*(dist - s.length)*dir/dist
            '''
            s.A.force += s.k*(dist - s.length)*dir/dist
            s.B.force += -s.k*(dist - s.length)*dir/dist
            
            # Сила давления
            if dir.y != 0:
                norm = pg.Vector2(1, -dir.x/dir.y)
                norm /= norm.length()
            else:
                norm = pg.Vector2(0, 1)
            if norm.dot(s.A.pos + dir/2 - self.pos_center) < 0:
                norm *= -1

            '''
            s.A.force_pr += norm*self.pressure*dist
            s.B.force_pr += norm*self.pressure*dist
            '''
            s.A.force += norm*self.pressure*dist
            s.B.force += norm*self.pressure*dist

        for v in self.vertexes:
            '''
            v.velocity += (v.force_s1 - self.friction*v.velocity_s1 + 
                           v.force_s2 - self.friction*v.velocity_s2 + 
                           v.force_pr + v.m*self.g)*dt/v.m
            '''
            v.velocity += (v.force - self.friction*v.velocity + v.m*self.g)*dt/v.m
            #v.velocity += (v.force - self.friction*v.velocity)*dt/v.m
            #v.velocity_g += self.g*dt
            
            v.pos += v.velocity*dt
    
    def recalc_pos_center(self):
        self.pos_center = pg.Vector2()
        mass = 0
        for v in self.vertexes:
            self.pos_center += v.pos*v.m
            mass += v.m
        self.pos_center /= mass

    def recalc_volume(self):
        self.volume = 0
        for i in range(len(self.vertexes)):
            a = (self.vertexes[i-1].pos - self.vertexes[i].pos).length()
            b = (self.vertexes[i-1].pos - self.pos_center).length()
            c = (self.vertexes[i].pos - self.pos_center).length()
            p = (a + b + c)/2
            self.volume += sqrt(p*(p-a)*(p-b)*(p-c))
        #print('vol', self.volume)

    def restore(self):
        for v in self.vertexes:
            #v.accel = pg.Vector2()
            v.force = pg.Vector2()
            v.force_s1 = pg.Vector2()
            v.force_s2 = pg.Vector2()
            v.force_pr = pg.Vector2()

    
    def collide(self, v):
        if v.pos.y > HEIGHT - 30:
            v.pos.y = HEIGHT - 30
            #v.velocity_s1.y *= -1
            #v.velocity_s2.y *= -1
            #v.velocity_pr.y *= -1

            v.velocity.y *= -1
            #v.velocity_g.y *= -1

    def draw(self):
        for i in range(len(self.vertexes)):
            pg.draw.line(screen, WHITE, self.vertexes[i-1].pos, self.vertexes[i].pos)


WIDTH, HEIGHT = 600, 400
FPS = 60
time = 0

WHITE = (255, 255, 255)
BG = (0, 0, 0)

pg.init()
screen = pg.display.set_mode((WIDTH, HEIGHT))
clock = pg.time.Clock()
font = pg.font.Font(None, 20)


# Здесь создается само тело, предпоследний параметр - это радиус, а 
# последний - это количество вершин
body = Body(pg.Vector2(WIDTH/2, HEIGHT/2-100), 50, 30)

running = True
while running:
    pg.display.set_caption(str(int(clock.get_fps())))
    clock.tick(FPS)
    screen.fill(BG)
    
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_g:
                body.g = pg.Vector2(0, 1)*9.81*18
                #body.friction = 2
            if event.key == pg.K_ESCAPE:
                pg.quit()
    
    keys = pg.key.get_pressed()
    if keys[pg.K_UP]:
        body.n += 10
        body.nRT = body.n*8.31*300
    elif keys[pg.K_DOWN]:
        body.n -= 10
        body.nRT = body.n*8.31*300


    body.update(pg.time.get_ticks()/1000 - time)
    body.draw()

    pg.draw.line(screen, WHITE, (0, HEIGHT-30), (WIDTH, HEIGHT-30), 2)

    screen.blit(font.render('n: '+str(body.n), True, WHITE), (10, 10))
    screen.blit(font.render('volume: '+str(int(body.volume)), True, WHITE), (10, 30))

    pg.display.flip()

    time = pg.time.get_ticks()/1000
