'''
Integrantes:
Carlos Gustavo Ramirez Rodriguez
Davi Cavalcante dos Santos
Jimi Tombolatto Gantinis
Paulo Fernando da Silva
'''

import pygame
import math
import random
from random import randint
from pygame.locals import *

screenWidth = 700
screenHeight = 500
pygame.init()
surface = pygame.display.set_mode((screenWidth, screenHeight))

pygame.display.set_caption('Space Invaders')

class InputBox:
    def __init__(self, x, y, w, h, font, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.font = font
        self.color = (0, 0, 150)
        self.text = text
        self.returnText = ''
        self.txt_surface = self.font.render(text, True, self.color)
        self.active = False

    def handleInputBoxEvent(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = (0, 100, 255) if self.active else (0, 0, 200)
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    self.returnText = self.text
                    self.text = ''
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                self.txt_surface = self.font.render(self.text, True, self.color)

    def updateInputBox(self):
        width = max(200, self.txt_surface.get_width()+10)
        self.rect.w = width

    def drawInputBox(self, surface):
        surface.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        pygame.draw.rect(surface, self.color, self.rect, 2)

    def getInputBoxText(self):
        return self.returnText

class Animacao:
    def __init__(self, surface, pathImg, totalFramesLargura, totalFramesAltura, framesBrancos, frameInicial, fps):
        '''DEFINE VARIÁVEIS DO CONSTRUTOR'''
        self.surface = surface # A surface que a imagem será aplicada
        self.pathImg = pathImg # O caminho da imagem a ser carregada
        self.totalFramesLargura = totalFramesLargura # Quantidade de frames por coluna
        self.totalFramesAltura = totalFramesAltura # Quantidade de frames por linha
        self.framesBrancos = framesBrancos # Quantidade de frames brancos
        self.frame = frameInicial # Em qual frame começa a animação
        self.timeAnimation = TimeStep(fps) # Controla FPS da animação em 60
        self.imagem = pygame.image.load(self.pathImg).convert_alpha() # Carrega a imagem
        self.imgInvertidaX = pygame.transform.flip(self.imagem, 1, 0) # Inverte no eixo X a imagem carregada e armazena para uso posterior
        self.rect = self.imagem.get_rect() # Obtém o retângulo com as dimensões da imagem
        self.totalFrames = self.totalFramesLargura * self.totalFramesAltura - self.framesBrancos # Calcula a quantidade total de frames
        self.larguraFrame = self.rect.width / self.totalFramesLargura # Calcula a largura de cada frame
        self.alturaFrame = self.rect.height / self.totalFramesAltura # Calcula a altura de cada frame      
        
    ''' DEFINE A FUNÇÃO DE DESENHO '''
    def desenha(self, posicaoXY, inverter):    
        ''' CARREGA LISTA COM OS FRAMES '''
        # Define se a animação sera invertida ou não no eixo x:
        self.posicaoX, self.posicaoY = posicaoXY # Define as posições x,y da animação (lembrando que x,y é o pixel superior esquerdo de cada imagem)
        self.inverter = inverter # Define se a animação sera invertidade (-1 para invertida, qualquer outro valor para não invertida)
        self.frames = [] # Define uma lista para armazenar os frames
        
        # Cada elemento da lista frames representa uma parte da imagem, e é composto por: (posiçãoX, posiçãoY, largura, altura), que será usada
        # no terceiro parâmetro da chamada de surface.blit para indicar que queremos desenhar apenas uma fração da imagem.
        # posiçãoX e posiçãoY são os pontos a partir de onde será desenhado um retângulo que terá tal largura e tal altura (lembrando que a altura é invertida).
        for i in range(0, self.totalFramesAltura):
            if self.inverter == -1:
                    for j in range(self.totalFramesLargura - 1, -1, -1): # Caso haja inversão, o for das colunas vai de trás para frente.
                        self.frames += list([(self.larguraFrame * j, self.alturaFrame * i, self.rect.width / self.totalFramesLargura, self.rect.height / self.totalFramesAltura)])
                        self.img = self.imgInvertidaX # Caso haja inversão, a imagem que será blitada na tela é a invertida
            else:
                    for j in range(0, self.totalFramesLargura):
                        self.frames += list([(self.larguraFrame * j, self.alturaFrame * i, self.rect.width / self.totalFramesLargura, self.rect.height / self.totalFramesAltura)])
                        self.img = self.imagem # Caso não haja inversão, a imagem que será blitada na tela é a que foi carregada anteriormente
                        
        self.surface.blit(self.img, (self.posicaoX, self.posicaoY), self.frames[int(self.frame)]) # "Blita um frame (fração da imagem) na surface, nas posições dadas.
        self.frame += self.timeAnimation.step() # O frame "blitado" depende da taxa de fps da animação.
        if self.frame >= self.totalFrames: # Se a posição do frame for maior ou igual o total de frames, a animação começa de novo.
            self.frame = 0

''''''
def rectAroundCircle(circlePos, circleRadius):
    circlePosX, circlePosY = circlePos
    rectPosX, rectPosY = circlePosX - circleRadius, circlePosY - circleRadius
    return rectPosX, rectPosY, circleRadius*2, circleRadius*2
''''''

''' PARTÍCULAS '''
class TimeStep:
    def __init__(self, fps):
        self.currentTime = pygame.time.get_ticks()/1000
        self.fps = fps
    def step(self):
        renderTime = 0
        newTime = pygame.time.get_ticks()/1000 
        frameTime = newTime - self.currentTime 
        self.currentTime = newTime
        renderTime += frameTime
        return renderTime * self.fps   

class Particle:
    def __init__(self, surface, pos, vel, color, size, lifeTime):
        self.surfaceWidth = pygame.Surface.get_size(surface)[0]
        self.surfaceHeight = pygame.Surface.get_size(surface)[1]   
        self.xPosition = pos[0]
        self.yPosition = pos[1]
        self.xVelocity = vel[0]
        self.yVelocity  = vel[1]
        self.color = list(color)
        self.originalColor = color
        self.size = size
        self.originalSize = size
        self.timeStep = TimeStep(60)
        self.lifeTime = lifeTime
        self.renderTime = 0
        self.dead = False

    def advance(self, changeSize, changeSizeVelocity, changeColor, changeColorVelocity):
        self.renderTime += self.timeStep.step()     
        self.xPosition += self.xVelocity
        self.yPosition += self.yVelocity
        self.changeSize = changeSize
        self.changeSizeVelocity = changeSizeVelocity
        newSize = abs(self.changeSize - self.originalSize)
        if self.originalSize < newSize:
            if int(self.originalSize + newSize * self.renderTime * self.changeSizeVelocity) >= self.changeSize:
                self.size = self.changeSize
            else:
                self.size = int(self.originalSize + newSize * self.renderTime * self.changeSizeVelocity)
        else:
            if int(self.originalSize - newSize * self.renderTime * self.changeSizeVelocity) <= self.changeSize:
                self.size = self.changeSize
            else:
                self.size = int(self.originalSize - newSize * self.renderTime * self.changeSizeVelocity)
                
        self.changeColor = changeColor
        self.changeColorVelocity = changeColorVelocity
     
        RGB = self.color
        for color in range(0, len(RGB)):
            newColor = abs(self.changeColor[color] - self.originalColor[color])
            if self.originalColor[color] < self.changeColor[color]:
                if int(self.originalColor[color] + newColor * self.renderTime * self.changeColorVelocity[color]) >= self.changeColor[color]:
                    self.color[color] = self.changeColor[color]
                else:
                    self.color[color] = int(self.originalColor[color] + newColor * self.renderTime * self.changeColorVelocity[color])
            else:
                if int(self.originalColor[color] - newColor * self.renderTime * self.changeColorVelocity[color]) <= self.changeColor[color]:
                    self.color[color] = self.changeColor[color]
                else:
                    self.color[color] = int(self.originalColor[color] - newColor * self.renderTime * self.changeColorVelocity[color])
                    
        if self.lifeTime - (self.renderTime / self.timeStep.fps) <= 0:       
            self.dead = True
        if self.xPosition < 0 - self.size or self.xPosition > self.surfaceWidth + self.size:
            self.dead = True
        if self.yPosition < 0 - self.size or self.yPosition > self.surfaceHeight + self.size:
            self.dead = True

    def addVelocity(self, xAccl, yAccl):
        self.xVelocity += xAccl
        self.yVelocity += yAccl

    def isDead(self):
        return self.dead

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.xPosition), int(self.yPosition)), self.size, 0)

class ParticleEmitter:
    def __init__(self):
        self.currentParticle = None
        self.timer = TimeStep(60)
        self.counter = 0
        self.emissionTime = 0
        self.originalEmissionTime = 0
        self.firstRun = False
        self.posCurrentParticle = 0, 0
        self.particlesList = []
        self.lifeTime = 0
        
    def emit(self, surface, particlesList, pos, velocity, color, size, lifeTime, totalParticles, emissionTime, changeSize, changeSizeVelocity, changeColor, changeColorVelocity):
        self.particleInfo = [pos, velocity, color, size, lifeTime]
        self.particlesList = particlesList
        if not self.firstRun:
            self.originalEmissionTime = emissionTime
            self.firstRun = True
        if self.originalEmissionTime != emissionTime:
            self.counter = 0
            self.emissionTime = emissionTime
            self.firstRun = False
        else:
            self.counter += self.timer.step()
            self.emissionTime = emissionTime - (self.counter / self.timer.fps)
            
        self.changeSize = changeSize
        self.changeSizeVelocity = changeSizeVelocity
        if len(self.particlesList) <= totalParticles and self.emissionTime > 0:
            self.particlesList.append(Particle(surface, pos, velocity, color, size, lifeTime))
        for i in range(len(self.particlesList)-1, 0, -1):
            self.currentParticle = self.particlesList[i]
            #self.currentParticle.addVelocity(round(random.uniform(0.01, -0.01),4), 0)
            self.currentParticle.advance(changeSize, changeSizeVelocity, changeColor, changeColorVelocity)
            if self.currentParticle.isDead():
                self.particlesList.remove(self.particlesList[i])
        for i in range(1, len(self.particlesList)):
            self.particlesList[i].draw(surface)
            
    def addVelocity(self, xAccl, yAccl):
        for i in range(len(self.particlesList)-1, 0, -1):
            self.currentParticle = self.particlesList[i]
            self.currentParticle.addVelocity(xAccl, yAccl)

    def addRandVelocity(self, xAccl, yAccl):
        xMinAccl, xMaxAccl = xAccl
        yMinAccl, yMaxAccl = yAccl
        for i in range(len(self.particlesList)-1, 0, -1):
            self.currentParticle = self.particlesList[i]
            self.currentParticle.addVelocity(random.uniform(xMinAccl, xMaxAccl), random.uniform(yMinAccl, yMaxAccl))
            
    def getParticleInfo(self):
        for i in range(len(self.particlesList)-1, 0, -1):
            self.currentParticle = self.particlesList[i]
            self.particleInfo = (self.currentParticle.xPosition, self.currentParticle.yPosition), (self.currentParticle.xVelocity, self.currentParticle.yVelocity), self.currentParticle.color, \
            self.currentParticle.size, self.currentParticle.lifeTime
        return self.particleInfo

''' PARTÍCULAS '''

def keyPressed(inputKey):
    keysPressed = pygame.key.get_pressed()
    if keysPressed[inputKey]:
        return True
    else:
        return False

def approach(g, c, dt):
    dif = g - c
    if dif > dt:
        return c + dt
    if dif < -dt:
        return c - dt
    else:
        return g

class MoveObj:
    def __init__(self, velocity, dt, posX):
        self.spdX = 0
        self.velocity = velocity
        self.dt = dt
        self.posX = posX
        
    def move_keys(self):
        if keyPressed(pygame.K_LEFT):
            self.spdX = approach(-self.velocity, self.spdX, self.dt)

        if keyPressed(pygame.K_RIGHT):    
            self.spdX = approach(self.velocity, self.spdX, self.dt)
            
        if not keyPressed(pygame.K_LEFT) and not keyPressed(pygame.K_RIGHT):
            self.spdX = approach(0, self.spdX, dt)
            
        self.posX = self.posX + self.spdX
        return int(self.posX)

    def move(self, spdX, spdY):
        self.posX = self.posX + spdX
        return int(self.posX)


def chkCollisionRect2(rectPos1, rectSize1, rectPos2, rectSize2):
    rectPos1X, rectPos1Y = rectPos1
    rectSize1X, rectSize1Y = rectSize1
    rectPos2X, rectPos2Y = rectPos2
    rectSize2X, rectSize2Y = rectSize2
    '''
       p1 ### p3
          ###
       p2 ### p4
    '''
    rect1P1 = rectPos1X, rectPos1Y
    rect1P2 = rectPos1X, rectPos1Y + rectSize1Y
    rect1P3 = rectPos1X + rectSize1X, rectPos1Y
    rect1P4 = rectPos1X + rectSize1X,  rectPos1Y + rectSize1Y
    rect1 = [rect1P1, rect1P2, rect1P3, rect1P4]
    
    rect2P1 = rectPos2X, rectPos2Y
    rect2P2 = rectPos2X, rectPos2Y + rectSize2Y
    rect2P3 = rectPos2X + rectSize2X, rectPos2Y
    rect2P4 = rectPos2X + rectSize2X,  rectPos2Y + rectSize2Y
    rect2 = [rect2P1, rect2P2, rect2P3, rect2P4]

    for i in range(0, 4):
        if (rect1[0][0] <= rect2[i][0] and rect2[i][0] <= rect1[3][0]) and (rect1[0][1] <= rect2[i][1] and rect2[i][1] <= rect1[3][1]):
            return True
        if (rect2[0][0] <= rect1[i][0] and rect1[i][0] <= rect2[3][0]) and (rect2[0][1] <= rect1[i][1] and rect1[i][1] <= rect2[3][1]):
            return True
    return False

def getGetHigherScorer():
    strings = []
    names = []
    scores = []
    higherScore = 0
    higherScorer = ''
    with open('HigherScorer.txt', 'r') as f:
        for i in range(0, 10):
            line = f.readline()
            strings.append(line)

    for i in range(len(strings)):
        if strings[i] != '':
            nextLine = strings[i].find('\n')
            comma = strings[i].find(',')
            names.append(strings[i][ 0 : comma])
            if nextLine != -1:
                scores.append(strings[i][comma + 1: nextLine])
            else: 
                scores.append(strings[i][comma + 1: len(strings[i])])

    for i in range(0, len(scores)):
        if int(scores[i]) > int(higherScore):
            higherScore = scores[i]
            higherScorer = names[i]        
    if higherScorer == '':
        higherScorer = 'none'
        higherScore = '0'
            
    return higherScorer, higherScore


''' INICIALIZA PLAYER E INIMIGOS '''
# Background
animBackground = Animacao(surface,'spaceBackGround.png', 1, 1, 0, 0, 1)

# Interface
matchTimerFont = pygame.font.SysFont('Comic Sans MS', 40)
scoreFont = pygame.font.SysFont('Comic Sans MS', 20)
victoryOrDefeatFont = pygame.font.SysFont('Comic Sans MS', 40)

# Player
score = 0
hiScorer = getGetHigherScorer()[0]
hiScore = getGetHigherScorer()[1]
lives = 3
defeat = False
victory = False
velocity = 0.5
dt = 0.006
playerPosX = 400 
playerPosY  = 450 
playerSizeX = 30
playerSizeY = 35
movePlayer = MoveObj(velocity, dt, playerPosX)
animPlayer = Animacao(surface,'playerStarship.png', 1, 1, 0, 0, 1)

# Player Missile             
playerMissileEmitter = ParticleEmitter()
plrMissileSurface = surface
plrMissileListParticles = []
plrMissilePos = playerPosX, playerPosY
plrMissileVelocity = (0, -1)
plrMissileColor = (220, 220, 0)
plrMissileTotalParticles = 1
plrMissileLifeTime = 20
plrMissileSize = 10
plrMissileEmissionTime = 0
plrMissileChangeSize = 1
plrMissileChangeSizeVelocity = 0.04
plrMissileChangeColor = (220, 0, 0)
plrMissileChangeColorVelocity = (0, 0.02, 0)
plrMissileHitBox = rectAroundCircle((0,0), 0)

# Enemy and Player Explosion
explosionEmitter = ParticleEmitter()
explosionSurface = surface
explosionListParticles = []
explosionPos = 0, 0
explosionVelocity = (0, 0.1)
explosionColor = (255, 0, 0)
explosionTotalParticles = 100
explosionLifeTime = 1.5
explosionSize = 15
explosionEmissionTime = 0
explosionChangeSize = 0
explosionChangeSizeVelocity = 0.015
explosionChangeColor = (255, 255, 0)
explosionChangeColorVelocity = (0, 0.05, 0.05)

# Enemy
EnemyblockSize = 25, 30
distanceSize = 12
enemyLines = 5
enemyColumns = 12
initDistance = 144, 50
enemies = []
enemiesType1 = 24
enemiesType2 = 24
enemiesType3 = 12
movEnemyVelX = 0.03
movEnemyVelY = 10
animEnemy1 = Animacao(surface,'enemySpaceship1.png', 1, 1, 0, 0, 1)
animEnemy2 = Animacao(surface,'enemySpaceship2.png', 1, 1, 0, 0, 1)
animEnemy3 = Animacao(surface,'enemySpaceship3.png', 1, 1, 0, 0, 1)

# Enemy Missile
enemyMissileEmitter = ParticleEmitter()
enmyMissileSurface = surface
enmyMissileListParticles1 = []
enmyMissileListParticles2 = []
enmyMissilePos = 0, 0
enmyMissileVelocity = (0, 1)
enmyMissileColor = (0, 220, 0)
enmyMissileTotalParticles = 1
enmyMissileLifeTime = 20
enmyMissileSize = 10
enmyMissileEmissionTime = 0
enmyMissileChangeSize = 1
enmyMissileChangeSizeVelocity = 0.04
enmyMissileChangeColor = (255, 100, 0)
enmyMissileChangeColorVelocity = (0, 0.02, 0)
enmyMissileHitBox1 = rectAroundCircle((0,0), 0)
enmyMissileHitBox2 = rectAroundCircle((0,0), 0)

# Player Propeller
playerPropellerEmitter = ParticleEmitter()
plrPropellerSurface = surface
plrPropellerListParticles = []
plrPropellerPos = 0, 0
plrPropellerVelocity = (0, 1)
plrPropellerColor = (220, 220, 0)
plrPropellerTotalParticles = 15
plrPropellerLifeTime = 1
plrPropellerSize = 8
plrPropellerEmissionTime = 5000
plrPropellerChangeSize = 0
plrPropellerChangeSizeVelocity = 0.06
plrPropellerChangeColor = (220, 0, 0)
plrPropellerChangeColorVelocity = (0.05, 0.05, 0.05)

# MotherShips
motherShip1 = Animacao(surface,'motherShip1.png', 1, 1, 0, 0, 1)
motherShip1SizeX = 70
motherShip1SizeY = 50
motherShip1PosX, motherShip1PosY = -1500, 0
motherShip1VelocityX = 0.2
motherShip1IsDestroyed = False

motherShip2 = Animacao(surface,'motherShip2.png', 8, 8, 2, 0, 60)
motherShip2SizeX = 70
motherShip2SizeY = 50
motherShip2PosX, motherShip2PosY = -1500, 0
motherShip2VelocityX = 0.4
motherShip2IsDestroyed = False

# Player and Enemy Missiles Handler
def shot(shooter):
    global plrMissileEmissionTime
    global enmyMissileEmissionTime
    if keyPressed(pygame.K_SPACE):
        if shooter == 'plr':
                plrMissileEmissionTime = 5000          
    if shooter == 'enmy':
        enmyMissileEmissionTime = 5000

''' INICIALIZA PLAYER E INIMIGOS '''
for i in range(0, enemyLines):
    for j in range(0, enemyColumns):
        rectPosX = initDistance[0] + EnemyblockSize[0] * j + distanceSize * j
        rectPosY = initDistance[1] + EnemyblockSize[1] * i + distanceSize * i
        rectSizeX = EnemyblockSize[0]
        rectSizeY = EnemyblockSize[1]
        enemies.append([rectPosX, rectPosY, rectSizeX, rectSizeY])

# Inicia InputBox
nameFont = pygame.font.Font(None, 32)
playerNameIB = InputBox(int(screenWidth / 2) - 100, int(screenHeight / 2), 140, 32, nameFont)

# Tela para digitar o nome
nameTyped = False
while not nameTyped:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
           nameTyped = True 
        playerNameIB.handleInputBoxEvent(event)
    playerNameIB.updateInputBox()
    animBackground.desenha((0, 0), 1)
    surface.blit(scoreFont.render('Enter Your Name: ', False, (255, 255, 255)), (int(screenWidth / 2) - 280, int(screenHeight / 2)))
    playerNameIB.drawInputBox(surface)
    
    if playerNameIB.getInputBoxText() != '':
        nameTyped = True
        playerName = playerNameIB.getInputBoxText()
    pygame.display.update() 

matchTimer = TimeStep(1)
matchClock = int(matchTimer.step())

while matchClock < 3:
    matchClock += matchTimer.step()
    animBackground.desenha((0, 0), 1)
    surface.blit(matchTimerFont.render('Match is Starting in: ' + str(3 - int(matchClock)) + '...', False, (255, 255, 255)), (int(screenWidth / 2) - 200, int(screenHeight / 2)))
    pygame.display.update() 
end = False
while not end:
    animBackground.desenha((0, 0), 1)

    if not defeat:
        plrMissilePos = playerPosX, playerPosY - playerSizeY
        playerMissileEmitter.emit(plrMissileSurface, plrMissileListParticles, plrMissilePos, plrMissileVelocity, plrMissileColor, plrMissileSize, plrMissileLifeTime, plrMissileTotalParticles, plrMissileEmissionTime, plrMissileChangeSize, plrMissileChangeSizeVelocity, \
        plrMissileChangeColor, plrMissileChangeColorVelocity)    
        plrMissileHitBox = rectAroundCircle(playerMissileEmitter.getParticleInfo()[0], playerMissileEmitter.getParticleInfo()[3])
        plrPropellerPos = playerPosX, playerPosY 
        playerPropellerEmitter.emit(plrPropellerSurface, plrPropellerListParticles, plrPropellerPos, (random.uniform(-0.02, 0.02), random.uniform(0.4, 0.5)), plrPropellerColor, plrPropellerSize, plrPropellerLifeTime, plrPropellerTotalParticles, plrPropellerEmissionTime, plrPropellerChangeSize, plrPropellerChangeSizeVelocity, \
        plrPropellerChangeColor, plrPropellerChangeColorVelocity)
        upperLeftXY = [screenWidth, screenHeight]
        lowerRightXY = [0, 0]
        playerPosX = movePlayer.move_keys()
        animPlayer.desenha((playerPosX - (playerSizeX / 2), playerPosY - playerSizeY), 1)
        hitBorder = False
   
        for i in range(0, len(enemies)):
                rectPosX = enemies[i][0]
                rectPosY = enemies[i][1]
                rectSizeX = enemies[i][2]
                rectSizeY = enemies[i][3]
                
                if i < enemiesType3:
                    animEnemy1.desenha((rectPosX, rectPosY), 1)
                elif i < enemiesType2 + enemiesType3:
                    animEnemy2.desenha((rectPosX, rectPosY), 1)
                else:
                    animEnemy3.desenha((rectPosX, rectPosY), 1)
                  
                if chkCollisionRect2((rectPosX, rectPosY), (rectSizeX, rectSizeY), (plrMissileHitBox[0], plrMissileHitBox[1]), (plrMissileHitBox[2], plrMissileHitBox[3])):
                    del(enemies[i])
                    if i < enemiesType3:
                        enemiesType3 -= 1
                        score += 40
                    elif i < enemiesType2 + enemiesType3:
                        enemiesType2 -= 1
                        score += 20
                    else:
                        enemiesType1 -= 1
                        score += 10
                    if enemiesType1 == 0 and enemiesType2 == 0 and enemiesType3 == 0:
                        victory = True

                    explosionEmissionTime = random.uniform(0.1, 0.2)
                    explosionPos = rectPosX + (rectSizeX / 2), rectPosY + (rectSizeY / 2) #(playerPosX - (playerSizeX / 2), playerPosY - (playerSizeY / 2))
                    explosionSize = 15
                    explosionColor = (220, 0, 0)
                    plrMissileListParticles = []
                    plrMissileEmissionTime = 0
                    break
                
                if chkCollisionRect2((playerPosX - (playerSizeX / 2), playerPosY - playerSizeY), (playerSizeX, playerSizeY), (enmyMissileHitBox1[0], enmyMissileHitBox1[1]), (enmyMissileHitBox1[2], enmyMissileHitBox1[3])):
                    explosionEmissionTime = random.uniform(0.1, 0.2)
                    explosionPos = (playerPosX - (playerSizeX / 2), playerPosY - (playerSizeY / 2))
                    explosionSize = 15
                    explosionColor = (0, 0, 0)
                    enmyMissileListParticles1 = []
                    lives -= 1
                    break

                if chkCollisionRect2((playerPosX - (playerSizeX / 2), playerPosY - playerSizeY), (playerSizeX, playerSizeY), (enmyMissileHitBox2[0], enmyMissileHitBox2[1]), (enmyMissileHitBox2[2], enmyMissileHitBox2[3])):
                    explosionEmissionTime = random.uniform(0.1, 0.2)
                    explosionPos = (playerPosX - (playerSizeX / 2), playerPosY - (playerSizeY / 2))
                    explosionSize = 15
                    explosionColor = (0, 0, 0)
                    enmyMissileListParticles2 = []
                    lives -= 1
                    break


                if chkCollisionRect2((playerPosX - (playerSizeX / 2), playerPosY - playerSizeY), (playerSizeX, playerSizeY), (upperLeftXY[0], upperLeftXY[1]), (abs(lowerRightXY[0] - upperLeftXY[0]), abs(lowerRightXY[1] - upperLeftXY[1]))):
                    defeat = True
                    

                if chkCollisionRect2((motherShip1PosX, motherShip1PosY),(motherShip1SizeX, motherShip1SizeY) , (plrMissileHitBox[0], plrMissileHitBox[1]), (plrMissileHitBox[2], plrMissileHitBox[3])) and not motherShip1IsDestroyed:
                    explosionEmissionTime = random.uniform(0.1, 0.2)
                    explosionPos = (motherShip1PosX + (motherShip1SizeX / 2), motherShip1PosY + motherShip1SizeY / 2)
                    explosionSize = 30
                    explosionColor = (220, 0, 0)
                    plrMissileListParticles = []
                    plrMissileEmissionTime = 0
                    motherShip1IsDestroyed = True
                    score += 500

                if chkCollisionRect2((motherShip2PosX, motherShip2PosY),(motherShip2SizeX, motherShip2SizeY) , (plrMissileHitBox[0], plrMissileHitBox[1]), (plrMissileHitBox[2], plrMissileHitBox[3])) and not motherShip2IsDestroyed:
                    explosionEmissionTime = random.uniform(0.1, 0.2)
                    explosionPos = (motherShip2PosX + (motherShip2SizeX / 2), motherShip2PosY + motherShip2SizeY / 2)
                    explosionSize = 30
                    explosionColor = (220, 0, 0)
                    plrMissileListParticles = []
                    plrMissileEmissionTime = 0
                    motherShip2IsDestroyed = True
                    score += 1000
                    
                if plrMissileHitBox[1] < 0:
                    plrMissileEmissionTime = 0         
                     
                if enemies[i][0] <= upperLeftXY[0]:
                    upperLeftXY[0] = enemies[i][0] 
                if enemies[i][1] <= upperLeftXY[1]:
                    upperLeftXY[1] = enemies[i][1] 
                if enemies[i][0] >= lowerRightXY[0]:
                    lowerRightXY[0] = enemies[i][0] + EnemyblockSize[0]
                if enemies[i][1] >= lowerRightXY[1]:
                    lowerRightXY[1] = enemies[i][1] + EnemyblockSize[1]
                              
                if upperLeftXY[0] + movEnemyVelX < 0:
                    movEnemyVelX += movEnemyVelX/4
                    movEnemyVelX = -movEnemyVelX
                    hitBorder = True
                if lowerRightXY[0] + movEnemyVelX  > screenWidth:
                    movEnemyVelX += movEnemyVelX/4
                    movEnemyVelX = -movEnemyVelX
                    hitBorder = True
    
    if not motherShip1IsDestroyed:
        motherShip1.desenha((motherShip1PosX, motherShip1PosY), 1)

    if not motherShip2IsDestroyed:
        motherShip2.desenha((motherShip2PosX, motherShip2PosY), 1)  

    if abs(motherShip1PosX + motherShip1VelocityX) > 2000 or (motherShip1PosX + motherShip1VelocityX) < -2000:
        motherShip1VelocityX = -motherShip1VelocityX
    
    if not motherShip2IsDestroyed:
        motherShip2.desenha((motherShip2PosX, motherShip2PosY), 1)
    
    if abs(motherShip2PosX + motherShip2VelocityX) > 2000 or (motherShip2PosX + motherShip2VelocityX) < -2000:
        motherShip2VelocityX = -motherShip2VelocityX
  
    motherShip1PosX += motherShip1VelocityX
    motherShip2PosX += motherShip2VelocityX
                
    if hitBorder:
        for i in range(0, len(enemies)):
            enemies[i][1] += movEnemyVelY
    
    if len(enemies) > 0:
        enemyShooter1 = randint(0, len(enemies)-1)
        enemyShooter2 = randint(0, len(enemies)-1)  
    
    for i in range(0, len(enemies)):
        enemies[i][0] += movEnemyVelX

        enmyMissilePos = enemies[enemyShooter1][0] + (EnemyblockSize[0] / 2), enemies[enemyShooter1][1] + EnemyblockSize[1]
        enmyMissilePos2 = enemies[enemyShooter2][0] + (EnemyblockSize[0] / 2), enemies[enemyShooter2][1] + EnemyblockSize[1]
        
    if len(enemies) > 0:
        if not defeat:
            shot('plr')
            shot('enmy')
            enemyMissileEmitter.emit(enmyMissileSurface, enmyMissileListParticles1, enmyMissilePos, enmyMissileVelocity, enmyMissileColor, enmyMissileSize, enmyMissileLifeTime, enmyMissileTotalParticles, enmyMissileEmissionTime, enmyMissileChangeSize, enmyMissileChangeSizeVelocity, \
            enmyMissileChangeColor, enmyMissileChangeColorVelocity)
            enmyMissileHitBox1 = rectAroundCircle(enemyMissileEmitter.getParticleInfo()[0], enemyMissileEmitter.getParticleInfo()[3])
            enemyMissileEmitter.emit(enmyMissileSurface, enmyMissileListParticles2, enmyMissilePos2, enmyMissileVelocity, enmyMissileColor, enmyMissileSize, enmyMissileLifeTime, enmyMissileTotalParticles, enmyMissileEmissionTime, enmyMissileChangeSize, enmyMissileChangeSizeVelocity, \
            enmyMissileChangeColor, enmyMissileChangeColorVelocity)
            enmyMissileHitBox2 = rectAroundCircle(enemyMissileEmitter.getParticleInfo()[0], enemyMissileEmitter.getParticleInfo()[3])

        explosionVelocity = (round(random.uniform(-0.1, 0.1),4), round(random.uniform(0.1, -0.1),4))
        explosionEmitter.emit(explosionSurface, explosionListParticles, explosionPos, explosionVelocity, explosionColor, explosionSize, explosionLifeTime, explosionTotalParticles, explosionEmissionTime, explosionChangeSize, explosionChangeSizeVelocity, \
        explosionChangeColor, explosionChangeColorVelocity)
        explosionXAcceleration = 0.01, -0.01
        explosionYAcceleration = 0.01, -0.01
        explosionNewVelocity = (explosionXAcceleration, explosionYAcceleration)
        explosionEmitter.addRandVelocity(explosionNewVelocity[0], explosionNewVelocity[1])
    
    if lives < 0:
        defeat = True

    if victory == True:
        surface.blit(victoryOrDefeatFont.render('You Won!', False, (255, 255, 255)), (int(screenWidth / 2.5), screenHeight / 2))
        
    surface.blit(scoreFont.render('SCORE: ' + str(score), False, (255, 255, 255)), (0, 0))
    if defeat:
        surface.blit(victoryOrDefeatFont.render('You Were Destroyed!', False, (255, 255, 255)), (screenWidth / 4, screenHeight / 2))
        lives = 0 

    surface.blit(scoreFont.render('HI-SCORE: ' + str(hiScore) + ' (' + str(hiScorer) + ')', False, (255, 255, 255)), (180, 0))

    surface.blit(scoreFont.render('LIVES: ' + str(lives), False, (255, 255, 255)), (500, 0))


    pygame.display.update() 
    for event in pygame.event.get():
        if (event.type == QUIT):
            end = True

pygame.display.quit()

# Exporta arquivo com o score atual
with open('HigherScorer.txt', 'r') as fr:
    with open('HigherScorer.txt', 'a+') as fw:
        fw.write(playerName + ',' + str(score) + '\n')
