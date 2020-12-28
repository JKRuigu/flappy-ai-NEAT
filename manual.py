import pygame
import os
import random

WIDTH,HEIGHT = 400,500

# LOAD ASSETS
BG_IMG = pygame.image.load(os.path.join("imgs", "bg.png"))
BIRD_IMGS = [pygame.image.load(os.path.join("imgs","bird" + str(x) + ".png")) for x in range(1,4)]
PIPE_IMG = pygame.image.load(os.path.join("imgs", "pipe.png"))
BASE_IMG = pygame.image.load(os.path.join("imgs", "base.png"))
pygame.font.init()
font = pygame.font.SysFont("comicsans", 20)

class Bird:
	IMGS = BIRD_IMGS
	def __init__(self,img):
		self.pos = [40,250]
		self.state = 0
		self.surface = self.IMGS[self.state]
		self.mask = pygame.mask.from_surface(self.surface)

	def update(self,win):
		self.surface = self.IMGS[self.state] #
		win.blit(self.surface, (self.pos[0], self.pos[1]))	

	def animate(self):
		self.state +=1
		if self.state  >2:
			self.state=0
	def jump(self):
		self.pos[1]-=8

	def collideTop(self, obj2):
		offset_x = obj2.x - self.pos[0]
		offset_y = obj2.top - self.pos[1]
		return self.mask.overlap(obj2.PIPE_TOP_MASK, (offset_x, offset_y)) != None

	def collideButtom(self, obj2):
		offset_x = obj2.x - self.pos[0]
		offset_y = obj2.bottom - self.pos[1]
		return self.mask.overlap(obj2.PIPE_BUTTOM_MASK, (offset_x, offset_y)) != None

	def collideBase(self, obj2):
		offset_x = obj2.x - self.pos[0]
		offset_y = obj2.y - self.pos[1]
		return self.mask.overlap(obj2.mask, (offset_x, offset_y)) != None	

	def move(self):
		self.pos[1] += 3



class Base:
	base_img = BASE_IMG
	vel = 1
	def __init__(self, x,y):
		self.x = x
		self.y = y
		self.vel = self.vel
		self.img = self.base_img
		self.mask = pygame.mask.from_surface(self.img)


	def draw(self,win):
		win.blit(self.img,(self.x,self.y))
	
	def move(self):
		self.x-=self.vel

class Pipe():
	GAP = 200
	VEL = 1

	def __init__(self, x):
		self.x = x
		self.height = 0
		self.top = 0
		self.bottom = 0
		self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)
		self.PIPE_BOTTOM = PIPE_IMG
		self.PIPE_TOP_MASK = pygame.mask.from_surface(self.PIPE_TOP)
		self.PIPE_BUTTOM_MASK = pygame.mask.from_surface(self.PIPE_BOTTOM)
		self.passed = False

		self.set_height()

	def set_height(self):
		self.height = random.randrange(50, 350)
		self.top = self.height - self.PIPE_TOP.get_height()
		self.bottom = self.height + self.GAP

	def move(self):
		self.x -= self.VEL

	def draw(self, win):
		win.blit(self.PIPE_TOP, (self.x, self.top))
		win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))
		

def background_update(win,bird,bases,pipes,distance,score):	
	bird.animate()		
	bird.move()		
	bird.update(win)

	for pipe in pipes:
		pipe.draw(win)

	for base in bases:
		base.move()
		base.draw(win)	

	win.blit(font.render(f"Score: {score}", 1, (255,255,255)), (50, 0))	
	win.blit(font.render(f"Distance: {distance}", 1, (255,255,255)), (50, 20))	
	pygame.display.update()

def run():
	# SETUP GAME
	pygame.font.init()
	WIN = pygame.display.set_mode((WIDTH, HEIGHT))
	WIN.blit(pygame.transform.scale(BG_IMG, (WIDTH,HEIGHT)), (0,0))	
	pygame.display.set_caption("Flappy Game")
	bird = Bird(BIRD_IMGS[0])
	pipes = [Pipe(300)]
	bases = [Base(-50,480),Base(200,480),Base(400,480),Base(600,480)]
	run = True
	distance = 0
	score = 0
	FPS = 60
	clock = pygame.time.Clock()
	
	while run:
		clock.tick(FPS)
		distance+=1
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False

		keys = pygame.key.get_pressed()

		if keys[pygame.K_UP]:
			bird.jump()
		if bird.pos[1] < 0:
			run = False
		add = False
		for base in bases:
			if base.x < -200:
				bases.pop(bases.index(base))
				add = True
			
		if add == True:
			bases.append(Base(550,480))		
			add = False

		rem = []
		add_pipe = False
		for pipe in pipes:
			pipe.move()
			if (bird.collideTop(pipe)) == True or (bird.collideButtom(pipe)) == True or bird.collideBase(bases[0]):
				run = False

			if pipe.x + pipe.PIPE_TOP.get_width() < 0:
				rem.append(pipe)

			if not pipe.passed and pipe.x < bird.pos[0]:
				pipe.passed = True
				add_pipe = True
				score +=10

		if add_pipe:
			pipes.append(Pipe(WIDTH))	

		WIN.blit(pygame.transform.scale(BG_IMG, (WIDTH,HEIGHT)), (0,0))				
		background_update(WIN,bird,bases,pipes,distance,score)	


if __name__ == '__main__':
	run()