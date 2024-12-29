import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import sys
import pygame

def distance(x1, y1, x2, y2):
    return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

MOUSEDOWN:bool = False
CONTROLHELD:bool = False
ZOOMING:bool = False
ZOOMINGOUT:bool = False
CAM:list[2] = [0, 0]
MOVEMENT:list = [0, 0]
circles:list = []
zoom:int = 1
size:int = 5
stabilizer:int = 5
TRANSPARENT:bool = False

pygame.init()

WIDTH, HEIGHT = 640, 480

pixels = {}

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption("Paint")

canvas = pygame.Surface((WIDTH, HEIGHT))
canvas.fill((255,255,255))

def clearImg():
    global circles
    circles = []
    updateScreen()

def save(filename):
    updateScreen()
    pygame.image.save(canvas, filename)

def drawItems():
    for item in objects:
        item.tick()

def transpBg():
    global TRANSPARENT
    TRANSPARENT = not(TRANSPARENT)
    transpBackground.text = "Transparent background ON" if TRANSPARENT else "Transparent background OFF"

objects = []
class Item:
    def __init__(self, x, y, width, height, text):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.hide = False

class Button(Item):
    def __init__(self, x, y, width, height, color, text, func, *args, **kwargs):
        super().__init__(x, y, width, height, text)
        self.color = color
        self.func = func
        self.hover = False
        self.args = args
        self.kwargs = kwargs
        self.dc = color
        objects.append(self)
    
    def tick(self, doDraw:bool=True):
        global MOUSEDOWN
        if not self.hide:
            mouse = pygame.mouse.get_pos()
            self.dc = list(self.color)
            if mouse[0] < self.x+self.width and mouse[0] > self.x and mouse[1] < self.y+self.height and mouse[1] > self.y:
                self.dc[0] *= 0.9
                self.dc[1] *= 0.9
                self.dc[2] *= 0.9

                
                if MOUSEDOWN:
                    self.hover = True
                elif self.hover:
                    self.hover = False
                    MOUSEDOWN = False
                    self.func(*self.args, **self.kwargs)
            if doDraw:
                self.draw()
            
    def draw(self):
        pygame.draw.rect(screen, self.dc, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, (0, 0, 0), (self.x, self.y, self.width, self.height), 1)
        text_surface = pygame.font.Font('freesansbold.ttf', round(self.height/1.5)).render(self.text, True, (0, 0, 0))
        screen.blit(text_surface, (self.x + (self.width / 2) - (text_surface.get_width() / 2), self.y + (self.height / 2) - (text_surface.get_height() / 2)))

class Dropdown(Item):
    def __init__(self, x:int, y:int, width:int, height:int, color:tuple[3], text:str, options:list[Item]):
        super().__init__(x, y, width, height, text)
        self.color = color
        self.options = options
        self.dropped:bool = False
        self.hover:bool = False
        self.main:bool = True
        self.dc = color
        for obj in options:
            obj.hide = True
        objects.append(self)
    
    def tick(self, doDraw:bool=True):
        global MOUSEDOWN
        if not self.hide:
            mouse = pygame.mouse.get_pos()
            self.dc = list(self.color)
            if mouse[0] < self.x+self.width and mouse[0] > self.x and mouse[1] < self.y+self.height and mouse[1] > self.y:
                self.dc[0] *= 0.9
                self.dc[1] *= 0.9
                self.dc[2] *= 0.9
                
                if MOUSEDOWN:
                    self.hover = True
                elif self.hover:
                    self.dropped = not(self.dropped)
                    self.hover = False
                    MOUSEDOWN = False
                    if self.main:
                        y = self.y + self.height
                        x = self.x
                    else:
                        y = self.y
                        x = self.x + self.width
                    for obj in self.options:
                        obj.hide = not(self.dropped)
                        obj.y = y
                        obj.x = x
                        if type(obj) == Dropdown:
                            obj.main = False
                        y += obj.height
                    updateScreen()
            else:
                self.hover = False
            
        if doDraw:
            self.draw()
    
    def draw(self):
        if not(self.hide):
            pygame.draw.rect(screen, self.dc, (self.x, self.y, self.width, self.height))
            pygame.draw.rect(screen, (0, 0, 0), (self.x, self.y, self.width, self.height), 1)
            text_surface = pygame.font.Font('freesansbold.ttf', round(self.height/1.5)).render(self.text, True, (0, 0, 0))
            screen.blit(text_surface, (self.x + (self.width / 2) - (text_surface.get_width() / 2), self.y + (self.height / 2) - (text_surface.get_height() / 2)))

            if self.dropped:
                if self.main:
                    y = self.y + self.height
                    x = self.x
                else:
                    y = self.y
                    x = self.x + self.width
                for obj in self.options:
                    obj.y = y
                    obj.x = x
                    if type(obj) == Dropdown:
                        obj.main = False
                    y += obj.height
                    if not(obj.hide):
                        obj.tick()

savePng = Button(0, 0, 128, 16, (0, 51, 204), "Save as PNG", save, "image.png")
saveJpeg = Button(0, 0, 128, 16, (0, 51, 204), "Save as JPEG", save, "image.jpeg")
saveSvg = Button(0, 0, 128, 16, (0, 51, 204), "Save as SVG", save, "image.svg")
saveAs = Dropdown(0, 0, 56, 16, (63,177,211), "Save as >", [savePng, saveJpeg, saveSvg])
clearImage = Button(0, 0, 36, 16, (0, 51, 204), "Clear", clearImg)
transpBackground = Button(0, 0, 164, 16, (0, 51, 204), "Transparent background OFF", transpBg)
fileDrop = Dropdown(0, 0, 64, 16, (0, 51, 204), "File", [transpBackground, saveAs, clearImage])

def updateScreen(items=True):
    global canvas
    canvas.fill((255, 255, 255))
    canvas = canvas.convert_alpha()
    screen.fill((255, 255, 255))
    for c in circles:
        if c[1]*zoom >= 1:
            s = c[1]*zoom
        else:
            s = 1
        p = ((c[0][0]-WIDTH/2+CAM[0])*zoom+WIDTH/2, (c[0][1]-HEIGHT/2+CAM[1])*zoom+HEIGHT/2)
        pygame.draw.circle(canvas, (0, 0, 0), p, s)
    screen.blit(canvas, (0, 0))
    if items:
        drawItems()
    pygame.draw.rect(screen, (0, 0, 0), (CAM[0]*zoom, CAM[1]*zoom, WIDTH*zoom, HEIGHT*zoom), 2)
    pygame.display.update()

def getWorldPos(pos:tuple[2]):
    return (pos[0]-WIDTH/2)/zoom+WIDTH/2-CAM[0], (pos[1]-HEIGHT/2)/zoom+HEIGHT/2-CAM[1]

screen.fill((255, 255, 255))

pygame.draw.rect(screen, (0, 0, 0), (CAM[0], CAM[1], WIDTH, HEIGHT), 2)
pygame.display.update()

while True:
    SPEED = 5
    CAM[0] += SPEED*MOVEMENT[0]/zoom
    CAM[1] += SPEED*MOVEMENT[1]/zoom
    if MOVEMENT[0] != 0 or MOVEMENT[1] != 0:
        updateScreen()

    if MOUSEDOWN:
        pos = pygame.mouse.get_pos()
        if pos != last_pos:
            maxi = len(range(int(distance(pos[0], pos[1], last_pos[0], last_pos[1]))))
            po = pos
            for i in range(round(maxi/stabilizer)):
                circlePos = (last_pos[0]+(pos[0]-last_pos[0])*(i/maxi),
                                last_pos[1]+(pos[1]-last_pos[1])*(i/maxi))
                po = circlePos
                circles.append((getWorldPos((circlePos[0], circlePos[1])), size))
                pygame.draw.circle(canvas, (0, 0, 0), circlePos, 5*zoom)
            screen.blit(canvas, (0, 0))
            pygame.draw.rect(screen, (0, 0, 0), (CAM[0], CAM[1], WIDTH, HEIGHT), 2)
            last_pos = po

    if ZOOMING and False:
        if ZOOMINGOUT:
            zoom += 0.025*zoom
        else:
            zoom -= 0.025*zoom
        updateScreen()

    drawItems()
    pygame.display.update()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            MOUSEDOWN = True
            pos = pygame.mouse.get_pos()
            last_pos = (pos[0], pos[1]-1)

        elif event.type == pygame.MOUSEBUTTONUP:
            MOUSEDOWN = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LCTRL:
                CONTROLHELD = True
            elif event.key == pygame.K_r and CONTROLHELD:
                screen.fill((255, 255, 255))
                pygame.display.update()
                circles = []
            elif (event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS or event.key == pygame) and CONTROLHELD:
                ZOOMING = True
                ZOOMINGOUT = True
            elif (event.key == pygame.K_MINUS or event.key == pygame.K_UNDERSCORE) and CONTROLHELD:
                ZOOMING = True
                ZOOMINGOUT = False
            elif event.key == pygame.K_UP:
                MOVEMENT[1] = 1
            elif event.key == pygame.K_DOWN:
                MOVEMENT[1] = -1
            elif event.key == pygame.K_LEFT:
                MOVEMENT[0] = 1
            elif event.key == pygame.K_RIGHT:
                MOVEMENT[0] = -1
            elif event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_LCTRL:
                CONTROLHELD = False
            if event.key == pygame.K_MINUS or event.key == pygame.K_UNDERSCORE or event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                ZOOMING = False
            if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                MOVEMENT[1] = 0
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                MOVEMENT[0] = 0
    clock.tick(60)