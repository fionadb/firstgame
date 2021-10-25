import pygame
from sys import exit, get_asyncgen_hooks
from pygame import color
from pygame.constants import HAT_RIGHTDOWN, KEYUP, MOUSEBUTTONDOWN
from pygame.sprite import collide_rect
import random

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
MOUSERIGHT='mousey.png'
TICTAC_IMAGE='star.png'
CAT1='cat1.png'
CAT2='cat2.png'
CAT3='cat3.png'
HEART='heart.png'
PACMAN_SPEED=5
GRID_WIDTH=50
GRID_HEIGHT=50 #this is the size of individual game elements eg pacman and the tictacs
STARTING_X=50
STARTING_Y=50
PACMAN_SIZE=(30,30)
CAT1X=WIN_WIDTH/2
CAT1Y=WIN_HEIGHT/2
CAT2X= (WIN_WIDTH/2)+GRID_WIDTH
CAT2Y= (WIN_HEIGHT/2)+GRID_HEIGHT
CAT3X= (WIN_WIDTH/2)+2*GRID_WIDTH
CAT3Y= (WIN_HEIGHT/2)+GRID_HEIGHT

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

class image ():
    def __init__(self,fileLocation,x=0,y=0,size='na'):
        self.surface=pygame.image.load(fileLocation).convert_alpha()
        if size != 'na':
            self.surface=pygame.transform.scale(self.surface,size)
        self.x=x
        self.y=y

    def appear(self):
        window.blit(self.surface,(self.x,self.y))
        
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
    def __init__(self, text, buttonColour='None', textColour='white',location='default',point='center'):
        super().__init__(x=0,y=0,text=text, font='body',colour=textColour)
        if location=='default': self.rect=self.surface.get_rect(center=(WIN_WIDTH/2,WIN_HEIGHT/2))
        elif point=='center': self.rect=self.surface.get_rect(center=location)
        elif point=='topLeft': self.rect=self.surface.get_rect(topleft=location)
        self.buttonColour=buttonColour
        
    def appear(self):
        if self.buttonColour!='None':
                pygame.draw.rect(window,self.buttonColour,self.rect)
        window.blit(self.surface,self.rect)

class sprite():
    def __init__(self, fileLocation, x, y):
        super().__init__()
        self.surface=pygame.image.load(fileLocation).convert_alpha()
        self.x=x
        self.y=y
        self.rect=self.surface.get_rect(topleft=(self.x,self.y))
        self.speed=0 #by default the sprite's speed is set to 0
        self.right=0
        self.left=0
        self.up=0
        self.down=0
        self.cornerInd=0
        self.livesLeft=3

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

    def moveSet(self):
        self.up=1
        self.down=1
        self.right=1
        self.left=1

class ghost (sprite):
    global ghosts
    ghosts=[]

    def __init__(self, fileLocation, x, y):
        super().__init__(fileLocation, x, y)
        ghosts.append(self)
        self.livesLeft=1

    def upBias(self):
        if self.up==1:
            self.down=0
            self.right=0
            self.left=0
        if self.right==1 and self.left==1: self.right=0
        if self.down==1 and self.left==1: self.down=0
        if self.down==1 and self.right==1: self.down=0

    def leftBias(self):
        if self.left==1:
            self.down=0
            self.right=0
            self.up=0
        if self.up==1 and self.down==1: self.down=0
        if self.right==1 and self.down==1: self.right=0
        if self.right==1 and self.up==1: self.right=0

    def downBias(self):
        if self.down==1:
            self.up=0
            self.right=0
            self.left=0
        if self.right==1 and self.left==1: self.right=0
        if self.up==1 and self.left==1: self.up=0
        if self.up==1 and self.right==1: self.up=0
    
    def rightBias(self):
        if self.right==1:
            self.down=0
            self.left=0
            self.up=0
        if self.up==1 and self.down==1: self.down=0
        if self.left==1 and self.down==1: self.left=0
        if self.left==1 and self.up==1: self.left=0

class obsticle(surface):
    global allObsticles
    allObsticles=[]

    def __init__(self, x, y, width, height, colour='blue'):
        super().__init__(x=x, y=y, width=width-1, height=height-1)
        self.colour=colour
        self.rect=self.surface.get_rect(topleft=(self.x,self.y))
        allObsticles.append(self)
        self.surface.fill(colour)

    @classmethod
    def show(obsticle):
        for each in allObsticles:
            each.appear()

    @classmethod
    def intagabilityOff(obsticle, object):
        global right
        global left
        global up
        global down
        collisions=0
        if object.right==1:
            futurex=object.rect.right+object.speed
            for each in allObsticles:
                    if each.x <= futurex <= (each.x+each.width) and ((each.y <= object.rect.top <= (each.y+each.height)) or (each.y <= object.rect.bottom <= (each.y+each.height))):
                        object.right=0
                        collisions=collisions+1
        if object.left==1:
            futurex=object.rect.left-object.speed
            for each in allObsticles:
                if each.x <= futurex <= each.x+each.width and ((each.y <= object.rect.top <= (each.y+each.height)) or (each.y <= object.rect.bottom <= (each.y+each.height))):
                    object.left=0
                    collisions=collisions+1
        if object.down==1:
            futurey=object.rect.bottom+object.speed
            for each in allObsticles:
                if each.y <= futurey <= each.y+each.height and ((each.x <= object.rect.left <= (each.x+each.width)) or (each.x <= object.rect.right <= (each.x+each.width))):
                    object.down=0
                    collisions=collisions+1
        if object.up==1:
            futurey=object.rect.top-object.speed
            for each in allObsticles:
                if each.y <= futurey <= each.y+each.height and ((each.x <= object.rect.left <= (each.x+each.width)) or (each.x <= object.rect.right <= (each.x+each.width))):
                    object.up=0
                    collisions=collisions+1
        if collisions>=2:
            object.cornerInd=object.cornerInd+1
            

class tictac(surface):
    global allTictacs
    allTictacs=[]

    def __init__(self,x,y):
        super().__init__(x,y)
        self.surface=pygame.image.load(TICTAC_IMAGE).convert_alpha()
        self.rect=self.surface.get_rect(topleft=(self.x,self.y))
        allTictacs.append(self)
        self.show=True

    @classmethod
    def generate(tictac):
        grid()
        for x in xValues:
            for y in  yValues:
                make=1
                for each in allObsticles:
                    if each.x <= x <= each.x+each.width and each.y <= y <= each.y+each.height:
                        make=0
                    elif (WIN_WIDTH/2) <= x <= (WIN_WIDTH/2)+150 and (WIN_HEIGHT/2)-50 <= y <= (WIN_HEIGHT/2)+50:
                        make=0
                    else: pass
                if make==1: a=tictac(x,y)

    @classmethod
    def show(tictac):
        for each in allTictacs:
            if each.show==True:
                each.appear()

    @classmethod
    def getsEaten(tictac):
        global score
        for each in allTictacs:
            if each.rect.colliderect(pacman.rect):
                if each.show==True:
                    each.show=False
                    score+=1

class lives(surface):
    global allLives
    allLives=[]

    def __init__(self,x,y):
        super().__init__(x,y)
        self.surface=pygame.image.load(HEART).convert_alpha()
        self.rect=self.surface.get_rect(topleft=(self.x,self.y))
        allLives.append(self)
        self.show=True

    @classmethod
    def loseLife(lives):
        pacman.livesLeft=pacman.livesLeft-1
        lifeLost = allLives[pacman.livesLeft]
        lifeLost.show=False
        if pacman.livesLeft==0:
            gameover()

    @classmethod
    def reset(lives):
        pacman.livesLeft=3
        for each in allLives:
            each.show=True

    @classmethod
    def show(lives):
        for each in allLives:
            if each.show==True:
                each.appear()


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
    pacman.left=0
    pacman.right=0
    pacman.up=0
    pacman.down=0
    #these values must be initialised again to prevent errors
    while paused==1:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit() #this is needed so can still quit while game is paused
            mousePosition=pygame.mouse.get_pos()
            if pausedButton.rect.collidepoint(mousePosition):
                if event.type==MOUSEBUTTONDOWN:
                    paused=0

def gameover():
    over=1
    global start
    gameOverButton.appear()
    pygame.display.update()
    while over==1:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit() #this is needed so can still quit
            mousePosition=pygame.mouse.get_pos()
            if gameOverButton.rect.collidepoint(mousePosition):
                if event.type==MOUSEBUTTONDOWN:
                    over=0
                    start=0

def gameWon():
    won=1
    global start
    gameWonButton.appear()
    pygame.display.update()
    while won==1:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit() #this is needed so can still quit
            mousePosition=pygame.mouse.get_pos()
            if gameWonButton.rect.collidepoint(mousePosition):
                if event.type==MOUSEBUTTONDOWN:
                    won=0
                    start=0
    

#defines background image
#background=image(BG_IMAGE)
background=surface(0,0,WIN_WIDTH,WIN_HEIGHT)

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
underF=obsticle(F1.rect.right+GRID_WIDTH,F3.rect.bottom+GRID_HEIGHT,2*GRID_WIDTH,2*GRID_HEIGHT,'green')
line5=obsticle(underF.x,underF.rect.bottom+GRID_HEIGHT,GRID_WIDTH*3,GRID_HEIGHT)


#creates pacman
pacman=sprite(MOUSERIGHT,STARTING_X,STARTING_Y)
pacman.setSpeed(PACMAN_SPEED)

#creates ghosts
ghost1=ghost(CAT1,WIN_WIDTH/2,WIN_HEIGHT/2)
ghost2=ghost(CAT2, (WIN_WIDTH/2)+GRID_WIDTH, (WIN_HEIGHT/2)+GRID_HEIGHT)
ghost3=ghost(CAT3, (WIN_WIDTH/2)+2*GRID_WIDTH, (WIN_HEIGHT/2)+GRID_HEIGHT)
for ghost in ghosts:
    ghost.setSpeed(PACMAN_SPEED)

#creates buttons
pausedButton=button('Click to unpause','red')
gameOverButton=button('Game over - click to play again','red')
gameWonButton=button('Game Won! - Would you like to play again?', 'pink')

#creates tictacs
tictac.generate()

n=1
while n<4:
    a=lives(WIN_WIDTH-n*GRID_WIDTH,0)
    n=n+1

start=0
startText=button('Choose an option to start','green','white',(WIN_WIDTH/2, (WIN_HEIGHT/2)-2*GRID_HEIGHT), 'center')
hardMode=button('Hard - game is over if you get eaten by a cat','red')
easyMode=button('Easy - survive 2 times before you get eaten','blue', 'white',(WIN_WIDTH/2, (WIN_HEIGHT/2)+2*GRID_HEIGHT),'center')

while True:
    while start==0:
        background.appear()
        time=0
        score=-1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit() #this is needed so can still quit while game is paused
            startText.appear()
            hardMode.appear()
            easyMode.appear()
            pygame.display.update()
            mousePosition=pygame.mouse.get_pos()
            if hardMode.rect.collidepoint(mousePosition):
                if event.type==MOUSEBUTTONDOWN:
                    start=1
                    easy=0
                    hard=1
            if easyMode.rect.collidepoint(mousePosition):
                if event.type==MOUSEBUTTONDOWN:
                    start=1
                    easy=1
                    hard=0

    pacman.rect.x=STARTING_X
    pacman.rect.y=STARTING_Y
    ghost1.rect.x=CAT1X
    ghost1.rect.y=CAT1Y
    ghost2.rect.x=CAT1X
    ghost2.rect.y=CAT2Y
    ghost3.rect.x=CAT3X
    ghost3.rect.y=CAT3Y
    #resets all sprites to their starting positions

    pacman.right=0
    pacman.left=0
    pacman.up=0
    pacman.down=0
    #these values need to be reinitialised to prevent errors

    for each in allTictacs:
        each.show=True
    #resets tictacs

    lives.reset()

    #contains the code which updates the game continuously
    while start==1:
        for event in pygame.event.get():
            #allows window to be closed by pressing button in upper right corner
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            #pauses game if player presses right mouse button
            if event.type==MOUSEBUTTONDOWN:
                pausedButton.appear()
                pygame.display.update()
                pause()
            #defines pacman's movements
            if event.type==pygame.KEYDOWN:
                if event.key==pygame.K_DOWN:
                    pacman.down=1
                if event.key==pygame.K_UP:
                    pacman.up=1
                if event.key==pygame.K_LEFT:
                    pacman.left=1
                if event.key==pygame.K_RIGHT:
                    pacman.right=1
            if event.type==pygame.KEYUP:
                if event.key==pygame.K_DOWN:
                    pacman.down=0
                if event.key==pygame.K_UP:
                    pacman.up=0
                if event.key==pygame.K_LEFT:
                    pacman.left=0
                if event.key==pygame.K_RIGHT:
                    pacman.right=0

        obsticle.intagabilityOff(pacman)
        if pacman.down==1: pacman.movedown()
        if pacman.up==1: pacman.moveup()
        if pacman.left==1: pacman.moveleft()
        if pacman.right==1: pacman.moveright()

        for ghost in ghosts:
            ghost.moveSet()
            obsticle.intagabilityOff(ghost)

        if ghost1.cornerInd % 4 == 3: ghost1.downBias()
        if ghost1.cornerInd % 4 == 2: ghost1.rightBias()
        if ghost1.cornerInd % 4 == 1: ghost1.upBias()
        if ghost1.cornerInd % 4 == 0: ghost1.leftBias()
        if time % 150 == 0 : ghost1.cornerInd=ghost1.cornerInd+1

        if ghost2.cornerInd % 4 == 3: ghost2.rightBias()
        if ghost2.cornerInd % 4 == 2: ghost2.upBias()
        if ghost2.cornerInd % 4 == 1: ghost2.leftBias()
        if ghost2.cornerInd % 4 == 0: ghost2.downBias()
        if time % 150 == 0 : ghost2.cornerInd=ghost2.cornerInd+1

        if ghost3.cornerInd % 4 == 3: ghost3.upBias()
        if ghost3.cornerInd % 4 == 2: ghost3.rightBias()
        if ghost3.cornerInd % 4 == 1: ghost3.downBias()
        if ghost3.cornerInd % 4 == 0: ghost3.leftBias()
        if time % 150 == 0 : ghost3.cornerInd=ghost2.cornerInd+1

        for ghost in ghosts:
            if ghost.down==1: ghost.movedown()
            if ghost.up==1: ghost.moveup()
            if ghost.left==1: ghost.moveleft()
            if ghost.right==1: ghost.moveright()
            if ghost.rect.colliderect(pacman.rect):
                if hard==1:
                    gameover()
                if easy==1:
                    lives.loseLife()
                    pacman.rect.x=STARTING_X
                    pacman.rect.y=STARTING_Y

        #the order things will appear on screen
        background.appear()
        obsticle.show()
        pacman.surface=pygame.transform.scale(pacman.surface,PACMAN_SIZE)
        pacman.appear()
        for ghost in ghosts:
            ghost.appear()
        tictac.getsEaten()
        tictac.show()
        # if time > 0:
        #     pacman.surface=pygame.image.load(PACMAN_OPEN).convert_alpha()
        #     pacman.surface=pygame.transform.scale(pacman.surface,PACMAN_SIZE)
        # else:
        #     pacman.surface=pygame.image.load(PACMAN_CLOSED).convert_alpha()
        #     pacman.surface=pygame.transform.scale(pacman.surface,PACMAN_SIZE)
        time=time+1
        scoreShow=button('score:' + str(score),'None','white',(0,0),'topLeft')
        scoreShow.appear()
        if easy==1:
            lives.show()

        n=0
        for each in allTictacs:
            if each.show==False:
                n=n+1

        if n==len(allTictacs):
            gameWon()

        #causes display window to continually update at chosen framerate
        pygame.display.update()
        clock.tick(FRAMERATE)
