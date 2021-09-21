import pygame
from sys import exit
from pygame import color
from pygame.constants import KEYUP, MOUSEBUTTONDOWN

#constants
WIN_WIDTH=1300
WIN_HEIGHT=600
FRAMERATE=60
BG_IMAGE='Drawing.png'
TITLE_FONT='font/titlefont.ttf'
BODY_FONT='font/bodyfont.ttf'
TEXT_COLOUR='white'
PACMAN_OPEN='pacmanOpen.png'
PACMAN_CLOSED='pacmanClosed.png'
TICTAC_IMAGE='star.png'
PACMAN_SPEED=5
GRID_WIDTH=50
GRID_HEIGHT=50 #this is the size of individual game elements eg pacman and the tictacs
STARTING_X=GRID_WIDTH
STARTING_Y=GRID_HEIGHT

#initialisation
pygame.init ()
window=pygame.display.set_mode((WIN_WIDTH,WIN_HEIGHT))
pygame.display.set_caption("Pacman game by Fiona and Harry")
clock=pygame.time.Clock()
gameActive=True

class surface:
    def __init__(self,x=0,y=0, width=100, height=100):
        self.surface=pygame.Surface((width,height))
        self.x=x
        self.y=y
        self.width=width
        self.height=height

    def setColor(self,colour='orange'):
        self.surface.fill(colour)

    def appear(self):
        window.blit(self.surface,(self.x,self.y))

class image (surface):
    def __init__(self,fileLocation,x=0,y=0):
        super().__init__(x,y)
        self.surface=pygame.image.load(fileLocation).convert_alpha()
        
class text (surface):
    def __init__(self,x,y,text='test',font='body',colour='white'):
        super().__init__(x,y)
        titleFont=pygame.font.Font(TITLE_FONT,100)
        bodyFont=pygame.font.Font(BODY_FONT,50)

        if font=='title':
            self.surface=titleFont.render(text,False,colour)

        if font=='body':
            self.surface=bodyFont.render(text,False,colour)
        
        if font != 'title' and font != 'body':
            raise Exception (f'{font} is not a valid font type')

class button(text):
    def __init__(self, text, buttonColour='None', textColour='white'):
        super().__init__(x=0,y=0,text=text, font='body',colour=textColour)
        self.rect=self.surface.get_rect(center=(WIN_WIDTH/2,WIN_HEIGHT/2))
        self.buttonColour=buttonColour
        
    def appear(self):
        window.blit(self.surface,self.rect)

class sprite(image):
    def __init__(self, fileLocation, x, y):
        super().__init__(fileLocation, x, y)
        self.rect=self.surface.get_rect(center=(self.x,self.y))
        self.speed=0 #by default the sprite's speed is set to 0

    def appear(self):
        window.blit(self.surface,self.rect)

    def setSpeed(self,speed):
        self.speed=speed

    def moveright(self):
        self.rect.x+=self.speed

    def moveleft(self):
        self.rect.x-=self.speed

    def moveup(self):
        self.rect.y-=self.speed
    
    def movedown(self):
        self.rect.y+=self.speed

class obsticle(surface):
    global allObsticles
    allObsticles=[]

    def __init__(self, x, y, width, height, colour='blue'):
        super().__init__(x=x, y=y, width=width-1, height=height-1)
        self.rect=self.surface.get_rect(topleft=(self.x,self.y))
        allObsticles.append(self)
        self.surface.fill(colour)

    @classmethod
    def show(obsticle):
        for each in allObsticles:
            each.appear()
            
    @classmethod
    def checkCollisions(obsticle, object):
        for each in allObsticles:
            if each.rect.colliderect(object.rect):
                print('cant move into object')

    @classmethod
    def intagabilityOff(obsticle, object):
        global down
        global right
        global left
        global up
        global down
        if right==1:
            futurex=object.rect.right+object.speed
            for each in allObsticles:
                if each.x <= futurex <= each.x+each.width and each.y <= object.y <= each.y+each.height:
                    right=0
        if left==1:
            futurex=object.rect.left-object.speed
            for each in allObsticles:
                if each.x <= futurex <= each.x+each.width and each.y <= object.y <= each.y+each.height:
                    left=0
        if down==1:
            futurey=object.rect.bottom+object.speed
            for each in allObsticles:
                if each.x <= object.x <= each.x+each.width and each.y <= futurey <= each.y+each.height:
                    down=0
        if up==1:
            futurey=object.rect.top-object.speed
            for each in allObsticles:
                if each.x <= object.x <= each.x+each.width and each.y <= futurey <= each.y+each.height:
                    up=0
            


class tictac(surface):
    global allTictacs
    allTictacs=[]

    def __init__(self,x,y):
        super().__init__(x,y)
        self.surface=pygame.image.load(TICTAC_IMAGE).convert_alpha()
        self.rect=self.surface.get_rect(topleft=(self.x,self.y))
        allTictacs.append(self)

    @classmethod
    def generate(tictac):
        grid()
        for x in xValues:
            for y in  yValues:
                make=1
                for each in allObsticles:
                    if each.x <= x <= each.x+each.width and each.y <= y <= each.y+each.height:
                        make=0
                    else: pass
                if make==1: a=tictac(x,y)

    @classmethod
    def show(tictac):
        for each in allTictacs:
            each.appear()

    @classmethod
    def number(tictac):
        print(str(len(allTictacs)))
                

def grid():
    global xValues
    global yValues
    xValues=[]
    yValues=[]
    area=WIN_WIDTH*WIN_HEIGHT
    gridarea=GRID_WIDTH*GRID_HEIGHT
    gridsPerRow=int(WIN_WIDTH/GRID_WIDTH)
    gridsPerColoumn=int(WIN_HEIGHT/GRID_HEIGHT)
    nGrids=int(area/gridarea)
    for n in range(gridsPerRow):
        xValues.append(n*GRID_WIDTH)
    for n in range(gridsPerColoumn):
        yValues.append(n*GRID_HEIGHT)
    return nGrids

#allows user to pause the game
def pause():
    paused=1
    #these values must be initialised again to prevent errors
    up=0
    down=0
    left=0
    right=0
    while paused==1:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit() #this is needed so can still quit while game is paused
            mousePosition=pygame.mouse.get_pos()
            if pausedButton.rect.collidepoint(mousePosition):
                if event.type==MOUSEBUTTONDOWN:
                    paused=0

#defines background image
background=image(BG_IMAGE)

#defines where the obsticals are
leftBoundary=obsticle(0,0,GRID_WIDTH,WIN_HEIGHT)
rightBoundary=obsticle(WIN_WIDTH-GRID_WIDTH,0, GRID_WIDTH, WIN_HEIGHT)
upperBoundary=obsticle(0,0,WIN_WIDTH,GRID_HEIGHT)
lowerBoundary=obsticle(0,WIN_HEIGHT-GRID_HEIGHT,WIN_WIDTH,GRID_HEIGHT)
H1=obsticle(leftBoundary.rect.right+GRID_WIDTH,upperBoundary.rect.bottom+GRID_HEIGHT,GRID_WIDTH,GRID_HEIGHT*6,'red')
H2=obsticle(H1.x+GRID_WIDTH,H1.y+3*GRID_HEIGHT,GRID_WIDTH*4,GRID_HEIGHT,'red')
H3=obsticle(H2.rect.right,H1.y,GRID_WIDTH,H1.height,'red')
underH=obsticle(H2.x+GRID_WIDTH,H2.y+2*GRID_HEIGHT,2*GRID_WIDTH,GRID_HEIGHT,'green')
line1=obsticle(H1.x,H1.rect.bottom+GRID_HEIGHT,6*GRID_WIDTH,GRID_HEIGHT)
onH1=obsticle(H1.x+2*GRID_WIDTH,H1.y,GRID_WIDTH,2*GRID_HEIGHT,'green')
onH2=obsticle(onH1.rect.right,onH1.y+GRID_HEIGHT,2*GRID_WIDTH,GRID_HEIGHT,'green')
line2=obsticle(H3.rect.right+GRID_WIDTH,H3.y,2*GRID_WIDTH,H3.height)
line3=obsticle(line1.rect.right+2*GRID_WIDTH,line1.y,line1.width,line1.height)
line4=obsticle(line2.rect.right+2*GRID_WIDTH,line2.y,4*GRID_WIDTH,line3.height,'orange')
F1=obsticle(line4.rect.right+2*GRID_WIDTH,H1.y,GRID_WIDTH,H1.height+GRID_HEIGHT,'pink')
F2=obsticle(F1.rect.right,F1.y,3*GRID_WIDTH,GRID_HEIGHT,'pink')
F3=obsticle(F1.rect.right,F2.rect.bottom+GRID_HEIGHT,3*GRID_WIDTH,GRID_HEIGHT,'pink')
#line6=obsticle(F1.x,F1.rect.bottom+GRID_HEIGHT,GRID_WIDTH,2*GRID_HEIGHT,'yellow')
underF=obsticle(F1.rect.right+GRID_WIDTH,F3.rect.bottom+GRID_HEIGHT,2*GRID_WIDTH,2*GRID_HEIGHT,'green')
line5=obsticle(underF.x,underF.rect.bottom+GRID_HEIGHT,GRID_WIDTH*3,GRID_HEIGHT)


#creates pacman
pacman=sprite(PACMAN_CLOSED,STARTING_X,STARTING_Y)
pacman.setSpeed(PACMAN_SPEED)

#creates buttons
pausedButton=button('Click to unpause','blue')

#initialises movement values
up=0
down=0
left=0
right=0

#creates tictacs
tictac.generate()
print(str(len(allTictacs)))

#contains the code which updates the game continuously
while True: 
    for event in pygame.event.get():
        #allows window to be closed by pressing button in upper right corner
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        #pauses game if player presses right mouse button
        if event.type==MOUSEBUTTONDOWN:
            if pausedButton.buttonColour!='None':
                pygame.draw.rect(window,pausedButton.buttonColour,pausedButton.rect)
            pausedButton.appear()
            pygame.display.update()
            pause()
        #defines pacman's movements
        if event.type==pygame.KEYDOWN:
            if event.key==pygame.K_DOWN:
                down=1
            if event.key==pygame.K_UP:
                up=1
            if event.key==pygame.K_LEFT:
                left=1
            if event.key==pygame.K_RIGHT:
                right=1
        if event.type==pygame.KEYUP:
            if event.key==pygame.K_DOWN:
                down=0
            if event.key==pygame.K_UP:
                up=0
            if event.key==pygame.K_LEFT:
                left=0
            if event.key==pygame.K_RIGHT:
                right=0

    obsticle.checkCollisions(pacman)
    obsticle.intagabilityOff(pacman)
    if down==1: pacman.movedown()
    if up==1: pacman.moveup()
    if left==1: pacman.moveleft()
    if right==1: pacman.moveright()

    # if pacman.rect.y<=upperBoundary.rect.bottom: pacman.rect.y=upperBoundary.rect.bottom
    # if pacman.rect.bottom>=lowerBoundary.rect.top: pacman.rect.bottom=lowerBoundary.rect.top
    # if pacman.rect.x<=leftBoundary.rect.right: pacman.rect.x=leftBoundary.rect.right
    # if pacman.rect.right>=rightBoundary.rect.left: pacman.rect.right=rightBoundary.rect.left

    #the order things will appear on screen
    background.appear()
    obsticle.show()
    pacman.appear()
    tictac.show()

    #causes display window to continually update at chosen framerate
    pygame.display.update()
    clock.tick(FRAMERATE)
