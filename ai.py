import pygame
import os
import random
import neat
import pickle

WIDTH,HEIGHT = 400,500
gen  =0

# LOAD ASSETS
BG_IMG = pygame.image.load(os.path.join("imgs", "bg.png"))
BIRD_IMGS = [pygame.image.load(os.path.join("imgs","bird" + str(x) + ".png")) for x in range(1,4)]
PIPE_IMG = pygame.image.load(os.path.join("imgs", "pipe.png"))
BASE_IMG = pygame.image.load(os.path.join("imgs", "base.png"))
pygame.font.init()
font = pygame.font.SysFont("comicsans", 20)
WIN = pygame.display.set_mode((WIDTH, HEIGHT))

class Bird:
	IMGS = BIRD_IMGS
	def __init__(self,img):
		self.pos = [100,250]
		self.state = 0
		self.surface = self.IMGS[self.state]
		self.mask = pygame.mask.from_surface(self.surface)

	def update(self,win):
		self.surface = self.IMGS[self.state] #
		win.blit(self.surface, (self.pos[0], self.pos[1]))	

	def animate(self,distance):
		if distance%10 == 0:
			self.state +=1
		if self.state  >2:
			self.state=0
	def jump(self,energy):
		self.pos[1]-=energy

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
	def move(self,gravity):
		self.pos[1] += gravity

class Base:
	base_img = BASE_IMG
	def __init__(self, x,y):
		self.x = x
		self.y = y
		self.img = self.base_img
		self.mask = pygame.mask.from_surface(self.img)


	def draw(self,win):
		win.blit(self.img,(self.x,self.y))
	
	def move(self,vel):
		self.x-=vel

class Pipe():
	GAP = 150

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
		self.height = random.randrange(50, 300)
		self.top = self.height - self.PIPE_TOP.get_height()
		self.bottom = self.height + self.GAP

	def move(self,vel):
		self.x -= vel


	def draw(self, win):
		win.blit(self.PIPE_TOP, (self.x, self.top))
		win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))		
		
def background_update(win,birds,bases,pipes,distance,score,gen,vel,limit):	
	for bird in birds:
		bird.animate(distance)			
		bird.update(win)

	for index,pipe in enumerate(pipes):
		pipe.draw(win)

	for base in bases:
		base.move(vel)
		base.draw(win)	

	win.blit(font.render(f"Score: {score}", 1, (255,255,255)), (20, 0))	
	win.blit(font.render(f"Distance: {distance}", 1, (255,255,255)), (20, 20))	
	win.blit(font.render(f"Alive: {len(birds)}", 1, (255,255,255)), (20, 40))	
	win.blit(font.render(f"GEN: {gen}", 1, (255,255,255)), (20, 60))	
	win.blit(font.render(f"Speed: {vel}", 1, (255,255,255)), (20, 80))	
	win.blit(font.render(f"Target: {limit}", 1, (255,255,255)), (20, 100))	
	pygame.display.update()

def eval_genomes(genomes, config):

	global WIN,gen
	win = WIN
	gen += 1

	# GET THE NEAT ALGORITHM READY
	nets = [] 
	birds = []
	ge = []
	vel = 3

	for genome_id, genome in genomes:
		genome.fitness = 0  # start with fitness level of 0
		net = neat.nn.FeedForwardNetwork.create(genome, config)
		nets.append(net)
		birds.append(Bird(BIRD_IMGS[0]))
		ge.append(genome)

	# SETUP GAME
	win.blit(pygame.transform.scale(BG_IMG, (WIDTH,HEIGHT)), (0,0))	
	pygame.display.set_caption("Flappy Bird AI")
	pipes = [Pipe(300)]
	bases = [Base(-50,480),Base(200,480),Base(400,480),Base(600,480)]
	run = True
	distance = 0
	score = 0
	FPS = 60
	clock = pygame.time.Clock()
	limit = 2000
	reaward = 0.1
	index = 0
	energy = 10
	gravity = 5
	
	while run:
		clock.tick(FPS)
		distance+=1

		if distance==limit:
			vel+=1
			index +=1
			limit+=limit
			gravity+=index
			energy+=index
			reaward = index*10
		else:
			if index == 0:
				reaward =0.1
			else:		
				reaward = index*0.1

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False

		# Update base
		add = False
		for base in bases:
			if base.x < -200:
				bases.pop(bases.index(base))
				add = True
			
		if add == True:
			bases.append(Base(550,480))		
			add = False

		pipe_ind = 0
		for x,pipe in enumerate(pipes):
			if not pipe.x < 0 :
				pipe_ind = x
				break

		for x, bird in enumerate(birds):  # give each bird a fitness of 0.1 for each frame it stays alive
			ge[x].fitness += reaward
			bird.move(gravity)

			# send bird location, top pipe location and bottom pipe location and determine from network whether to jump or not
			output = nets[birds.index(bird)].activate((bird.pos[1], abs(bird.pos[1] - pipes[pipe_ind].height), abs(bird.pos[1] - pipes[pipe_ind].bottom)))

			if output[0] > 0.5:  # we use a tanh activation function so result will be between -1 and 1. if over 0.5 jump
				bird.jump(energy)

		rem = []
		add_pipe = False
		for pipe in pipes:
			pipe.move(vel)

			if pipe.x + pipe.PIPE_TOP.get_width() < 0:
				rem.append(pipe)
			for bird in birds:	
				if not pipe.passed and pipe.x < bird.pos[0]:
					pipe.passed = True
					add_pipe = True
					score +=10
					ge[birds.index(bird)].fitness += 2


		if add_pipe:
			pipes.append(Pipe(WIDTH))	
			
		for r in rem:
			pipes.remove(r)

		#CHECK COLLIDE
		for bird in birds:
			if (bird.collideTop(pipe)) == True or (bird.collideButtom(pipe)) == True or bird.collideBase(bases[0]) or bird.pos[1] <0:
				ge[birds.index(bird)].fitness -= 10
				nets.pop(birds.index(bird))
				ge.pop(birds.index(bird))
				birds.pop(birds.index(bird))
		if len(birds) == 0:
			run = False		
		 #break if score gets large enough
		if score > 10000:
			pickle.dump(nets[0],open("best.pickle", "wb"))
			break
		win.blit(pygame.transform.scale(BG_IMG, (WIDTH,HEIGHT)), (0,0))				
		background_update(win,birds,bases,pipes,distance,score,gen,vel,limit)	

def run(config_file):
	"""
	runs the NEAT algorithm to train a neural network to play flappy car.
	:param config_file: location of config file
	:return: None
	"""
	config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
						 neat.DefaultSpeciesSet, neat.DefaultStagnation,
						 config_file)

	# Create the population, which is the top-level object for a NEAT run.
	p = neat.Population(config)

	# Add a stdout reporter to show progress in the terminal.
	p.add_reporter(neat.StdOutReporter(True))
	stats = neat.StatisticsReporter()
	p.add_reporter(stats)
	#p.add_reporter(neat.Checkpointer(5))

	# Run for up to 20 generations.
	winner = p.run(eval_genomes, 20)

	with open("winner.pkl","wb") as f:
		pickle.dump(winner,f)
		f.close()

	# show final stats
	print('\nBest genome:\n{!s}'.format(winner))

if __name__ == '__main__':
	local_dir = os.path.dirname(__file__)
	config_path = os.path.join(local_dir, 'config.txt')
	run(config_path)