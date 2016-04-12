import breve
import random
import math
import copy
import cPickle
import time
import decimal
import os 
import sys

__author__ = 'Paulo Pereira'

decimal.getcontext().prec = 6

class Swarm( breve.Control ):
	def __init__( self ):
		breve.Control.__init__( self )

		self.date = time.strftime("%Y%m%d%H%M")

		# Random Number Generator
		random.seed( 5 )
		self.setRandomSeed( 5 )
		# self.setRandomSeedFromDevRandom()

		self.showCorpse = True
		self.isToLoad = False
		self.isToSave = False
		self.isToRecord = True
		self.movie = None

		# Evaluation
		self.isToEvaluate = False
		self.evaluatePrey = False
		self.evaluatePredator = False
		self.phase_portrait = False
		
		self.runs = 1
		self.current_run = 0
		self.preyID = 1
		self.predatorID = 1

		self.listPrey_BestFitness = []
		self.listPrey_AverageFitness = []
		self.listPrey_Diversity = []
		self.tempPrey_Best = 0
		self.tempPrey_Average= 0
		self.tempPrey_Diversity= 0
		self.listPredator_BestFitness = []
		self.listPredator_AverageFitness = []
		self.listPredator_Diversity = []
		self.tempPredator_Best = 0
		self.tempPredator_Average = 0
		self.tempPredator_Diversity = 0
		self.list_phase_portrait = []
		self.tempPrey_pp = 0
		self.tempPredator_pp = 0

		# Representation
		self.repr = 2
		self.reprType = ['ga', 'gp', 'push']

		# Simulation
		self.initialNumPreys = self.numPreys = 90
		self.initialNumPredators = self.numPredators = 30
		self.numDeadPreys = 0
		self.numDeadPredators = 0

		# World
		self.minX = -200
		self.maxX = 200
		self.minY = -100
		self.maxY = 100

		self.targetZone1 = 25
		self.targetZone2 = 30
		self.socialZone = 10
		self.separationZone = 2

		# Feeder
		self.feederMinDistance = 25
		self.maxFoodSupply = 300
		self.minCreatedFoodSupply = 7
		self.maxCreatedFoodSupply = 15
		self.totalFoodSupply = 0

		# List
		self.pollPreys = breve.objectList()
		self.pollPredators = breve.objectList()

		# Generation
		self.maxIteraction = 5000
		self.current_iteraction = 0
		self.save_generation = 25
		self.breeding_season = 50
		self.breeding_inc = 0.5
		self.max_pop_predators = 0.6
		self.prob_mutation = 0.1
		self.evaluation_survivor = 0.9
		self.initial_depth = 3
		self.endSimulation = False

		# Other thing
		Swarm.init( self )

		self.setDisplayText(self.reprType[self.repr].upper(), xLoc = -0.950000, yLoc = -0.400000, messageNumber = 6, theColor = breve.vector( 1, 1, 1 ))

	def descendingCmp(self, a, b):
		return - cmp(self.fitness(a), self.fitness(b))

	def createFeeder(self, num, rapid ):
		# Simple Sequential Inhibition
		dist = 0
		x = 0
		y = 0
		while dist < self.feederMinDistance:
			dist = 99999
			x = random.uniform(self.minX, self.maxX)
			y = random.uniform(self.minY, self.maxY)

			feeders = breve.allInstances( "Feeder" )
			if breve.length(feeders) == 0:
				break
			for feeder in feeders:
				norm = math.sqrt((x-feeder.pos_x)**2 + (y-feeder.pos_y)**2)
				if norm < dist:
					dist = norm
		temp_feed = breve.createInstances( breve.Feeder, 1)
		temp_feed.initializeRandomly(x,y,rapid)

	def createPreys(self, num):
		# latin hypercubes
		if num < 1:
			return

		size = (int) (math.ceil(num**0.5))
		num_segments_x = (self.maxX-self.minX)/size
		num_segments_y = (self.maxY-self.minY)/size
		created = 0

		for i in range(size):
			for j in range(size):
				if created == num:
					return

				x = random.uniform((float) (i*num_segments_x+self.minX), (float) ((i+1)*num_segments_x+self.minX))
				y = random.uniform((float)(j*num_segments_y+self.minY), (float)((j+1)*num_segments_y+self.minY))

				if breve.length(self.pollPreys) < 1:
					temp_prey = breve.createInstances( breve.Prey, 1)
					temp_prey.initializeRandomly(x,y)
				else:
					temp_prey = self.pollPreys[0]
					temp_prey.isAlive = True
					self.pollPreys.remove(temp_prey)
					temp_prey.initializeRandomly(x,y)
					
					if self.controller.repr == 2:
						temp_prey.createPush()

				temp_prey.energy = 0.5
				created += 1

				temp_prey.ID = self.preyID
				self.preyID += 1
				self.save_log( 'new prey created with ID=' + str(temp_prey.ID) )

	def createPredators(self, num):
		# latin hypercubes
		if num < 1:
			return

		size = (int) (math.ceil(num**0.5))
		num_segments_x = (self.maxX-self.minX)/size
		num_segments_y = (self.maxY-self.minY)/size
		created = 0

		for i in range(size):
			for j in range(size):
				if created == num:
					return

				x = random.uniform((float) (i*num_segments_x+self.minX), (float) ((i+1)*num_segments_x+self.minX))
				y = random.uniform((float)(j*num_segments_y+self.minY), (float)((j+1)*num_segments_y+self.minY))
				if breve.length(self.pollPredators) < 1:
					temp_predator = breve.createInstances( breve.Predator, 1)
					temp_predator.initializeRandomly(x,y)
				else:
					temp_predator = self.pollPredators[0]
					temp_predator.isAlive = True
					self.pollPredators.remove(temp_predator)
					temp_predator.initializeRandomly(x,y)

					if self.controller.repr == 2:
						temp_predator.createPush()
						
				temp_predator.energy = 0.5
				created += 1

				temp_predator.ID = self.predatorID
				self.predatorID += 1
				self.save_log( 'new predator created with ID=' + str(temp_predator.ID) )

	def revive(self, array, num):
		# immigrants
		if num < 1:
			return

		size = (int) (math.ceil(num**0.5))
		num_segments_x = (self.maxX-self.minX)/size
		num_segments_y = (self.maxY-self.minY)/size
		created = 0

		for i in range(size):
			for j in range(size):
				if created == num:
					return

				x = random.uniform((float) (i*num_segments_x+self.minX), (float) ((i+1)*num_segments_x+self.minX))
				y = random.uniform((float)(j*num_segments_y+self.minY), (float)((j+1)*num_segments_y+self.minY))

				newBird = array[-1]
				array.remove(newBird)
				
				newBird.changePos(x, y)
				vel_x = random.uniform(-newBird.maxVel, newBird.maxVel)
				vel_y = random.uniform(-newBird.maxVel, newBird.maxVel)
				newBird.changeVel(vel_x,vel_y)
				newBird.changeAccel(0,0)

				newBird.age = 0
				newBird.energy = 0.5
				newBird.isAlive = True
				newBird.setNewColor()
				created += 1

				kind = newBird.getType()
				self.save_log( kind + str(newBird.ID) + ' revived' )
			
	def add_new_agents( self ):
		self.save_log( '--- Started run ' + str(self.current_run) + ' ---\n' )

		if not self.isToLoad:
			self.addRandomFeederIfNecessary()

			self.createPreys(self.initialNumPreys)
			self.createPredators(self.initialNumPredators)

			if self.controller.evaluatePrey:
				self.load_metrics_predators()

			if self.controller.evaluatePredator:
				self.load_metrics_preys()
			
		else:
			self.load_data()

	def init( self ):
		self.setBackgroundColor( breve.vector( 0, 0, 0 ) )
		self.setDisplayTextColor( breve.vector( 1, 1, 1 ) )
		self.pointCamera( breve.vector( 0, 0, 0 ), breve.vector( 0, 0, 300 ) )
		self.setIterationStep(1.0)
		self.enableDrawEveryFrame()
		self.enableSmoothDrawing()

		if self.evaluatePrey or self.evaluatePredator:
			self.save_log( 'Representation: ' + self.controller.reprType[self.controller.repr], initiation=True )
			self.save_log( 'Initial Preys: ' + str(self.initialNumPreys), initiation=True )
			self.save_log( 'Initial Predators: ' + str(self.initialNumPredators), initiation=True )
			self.save_log( 'WorldX: [' + str(self.minX) + ', ' + str(self.maxX) + ']', initiation=True )
			self.save_log( 'WorldY: [' + str(self.minY) + ', ' + str(self.maxY) + ']', initiation=True )
			self.save_log( 'Target Zone1: ' + str(self.targetZone1), initiation=True )
			self.save_log( 'Target Zone2: ' + str(self.targetZone2), initiation=True )
			self.save_log( 'Social Zone: ' + str(self.socialZone), initiation=True )
			self.save_log( 'Separation Zone: ' + str(self.separationZone), initiation=True )
			self.save_log( 'Max Food Supplies: ' + str(self.maxFoodSupply), initiation=True )
			self.save_log( 'Feeder Min Distance: ' + str(self.feederMinDistance), initiation=True )

			self.save_log( 'Runs: ' + str(self.runs), initiation=True )
			self.save_log( 'Max Iteraction: ' + str(self.maxIteraction), initiation=True )
			self.save_log( 'Breeding Season: ' + str(self.breeding_season), initiation=True )
			self.save_log( 'Breeding Inc: ' + str(self.breeding_inc), initiation=True )
			self.save_log( 'Max Pop Predators: ' + str(self.max_pop_predators), initiation=True )
			self.save_log( 'Mutation Prob: ' + str(self.prob_mutation), initiation=True )
			self.save_log( 'Evaluation Survivor: ' + str(self.evaluation_survivor) + '\n\n\n', initiation=True )

		self.add_new_agents()

	def save_data(self):
		suffix = self.controller.reprType[self.controller.repr]

		# feeders
		f =  open('data/feeder_'+suffix+'.pkl', 'wb')
		for feeder in breve.allInstances( "Feeder" ):
			temp_feeder = Data_Stationary(feeder.pos_x, feeder.pos_y, feeder.energy, feeder.lastScale, feeder.rapid, feeder.VirtualEnergy)
			cPickle.dump(temp_feeder, f)
		f.close()

		# preys
		f =  open('data/prey_'+suffix+'.pkl', 'wb')
		for prey in breve.allInstances( "Prey" ):
			if prey.isAlive:
				if self.controller.repr == 2:
					geno = prey.pushCode.getList()
				else:
					geno = prey.geno

				temp_accel = prey.getAcceleration()
				temp_prey = Data_mobile(prey.pos_x, prey.pos_y, prey.vel_x, prey.vel_y, temp_accel.x, temp_accel.y, prey.energy, prey.age, prey.isAlive, prey.maxVel, prey.maxAccel, prey.visionAngle, prey.maxSteering, geno, prey.lastScale)
				cPickle.dump(temp_prey, f)
		for prey in self.pollPreys:
			if self.controller.repr == 2:
				geno = prey.pushCode.getList()
			else:
				geno = prey.geno

			temp_accel = prey.getAcceleration()
			temp_prey = Data_mobile(prey.pos_x, prey.pos_y, prey.vel_x, prey.vel_y, temp_accel.x, temp_accel.y, prey.energy, prey.age, prey.isAlive, prey.maxVel, prey.maxAccel, prey.visionAngle, prey.maxSteering, geno, prey.lastScale)
			cPickle.dump(temp_prey, f)
		f.close()

		# prepadors
		f =  open('data/predator_'+suffix+'.pkl', 'wb')
		for predator in breve.allInstances( "Predator" ):
			if predator.isAlive:
				if self.controller.repr == 2:
					geno = predator.pushCode.getList()
				else:
					geno = predator.geno

				temp_accel = predator.getAcceleration()
				temp_predator = Data_mobile(predator.pos_x, predator.pos_y, predator.vel_x, predator.vel_y, temp_accel.x, temp_accel.y, predator.energy, predator.age, predator.isAlive, predator.maxVel, predator.maxAccel, predator.visionAngle, predator.maxSteering, geno, predator.lastScale)
				cPickle.dump(temp_predator, f)
		for predator in self.pollPredators:
			if self.controller.repr == 2:
				geno = predator.pushCode.getList()
			else:
				geno = predator.geno

			temp_accel = predator.getAcceleration()
			temp_predator = Data_mobile(predator.pos_x, predator.pos_y, predator.vel_x, predator.vel_y, temp_accel.x, temp_accel.y, predator.energy, predator.age, predator.isAlive, predator.maxVel, predator.maxAccel, predator.visionAngle, predator.maxSteering, geno, predator.lastScale)
			cPickle.dump(temp_predator, f)
		f.close()

	def load_data(self):
		suffix = self.controller.reprType[self.controller.repr]

		# feeders
		f =  open('data/feeder_'+suffix+'.pkl', 'rb')
		while True:
			try:
				data_feeder = cPickle.load(f)
				temp_feed = breve.createInstances( breve.Feeder, 1)
				temp_feed.initializeFromData(data_feeder.pos_x, data_feeder.pos_y, data_feeder.energy, data_feeder.lastScale, data_feeder.rapid, data_feeder.VirtualEnergy)
			except EOFError:
				break
		f.close()

		# preys
		f =  open('data/prey_'+suffix+'.pkl', 'rb')
		while True:
			try:
				data_prey = cPickle.load(f)
				
				temp_prey = breve.createInstances( breve.Prey, 1)
				temp_prey.initializeFromData(data_prey.pos_x, data_prey.pos_y, data_prey.vel_x, data_prey.vel_y, data_prey.accel_x, data_prey.accel_y, data_prey.energy, data_prey.age, data_prey.isAlive, data_prey.maxVel, data_prey.maxAccel, data_prey.visionAngle, data_prey.maxSteering, data_prey.geno, data_prey.lastScale)

				temp_prey.ID = self.preyID
				self.preyID += 1
				if not temp_prey.isAlive:
					temp_prey.dropDead(False)
			except EOFError:
				break
		f.close()

		# prepadors
		f =  open('data/predator_'+suffix+'.pkl', 'rb')
		while True:
			try:
				data_predator = cPickle.load(f)
				temp_predator = breve.createInstances( breve.Predator, 1)
				temp_predator.initializeFromData(data_predator.pos_x, data_predator.pos_y, data_predator.vel_x, data_predator.vel_y, data_predator.accel_x, data_predator.accel_y, data_predator.energy, data_predator.age, data_predator.isAlive, data_predator.maxVel, data_predator.maxAccel, data_predator.visionAngle, data_predator.maxSteering, data_predator.geno, data_predator.lastScale)

				temp_predator.ID = self.predatorID
				self.predatorID += 1
				if not temp_predator.isAlive:
					temp_predator.dropDead(False)
			except EOFError:
				break
		f.close()

	def save_metrics(self):
		suffix = self.controller.reprType[self.controller.repr]

		preys_alive = []
		preys_dead = []
		predators_alive = []
		predators_dead = []

		# preys
		for prey in breve.allInstances( "Prey" ):
			if prey.isAlive:
				if self.controller.repr == 2:
					geno = prey.pushCode.getList()
				else:
					geno = prey.geno

				temp_accel = prey.getAcceleration()
				temp_prey = Data_mobile(prey.pos_x, prey.pos_y, prey.vel_x, prey.vel_y, temp_accel.x, temp_accel.y, prey.energy, prey.age, prey.isAlive, prey.maxVel, prey.maxAccel, prey.visionAngle, prey.maxSteering, geno, prey.lastScale)
				preys_alive.append(temp_prey)
		for prey in self.pollPreys:
			if self.controller.repr == 2:
				geno = prey.pushCode.getList()
			else:
				geno = prey.geno

			temp_accel = prey.getAcceleration()
			temp_prey = Data_mobile(prey.pos_x, prey.pos_y, prey.vel_x, prey.vel_y, temp_accel.x, temp_accel.y, prey.energy, prey.age, prey.isAlive, prey.maxVel, prey.maxAccel, prey.visionAngle, prey.maxSteering, geno, prey.lastScale)
			preys_dead.append(temp_prey)

		# prepadors
		for predator in breve.allInstances( "Predator" ):
			if predator.isAlive:
				if self.controller.repr == 2:
					geno = predator.pushCode.getList()
				else:
					geno = predator.geno

				temp_accel = predator.getAcceleration()
				temp_predator = Data_mobile(predator.pos_x, predator.pos_y, predator.vel_x, predator.vel_y, temp_accel.x, temp_accel.y, predator.energy, predator.age, predator.isAlive, predator.maxVel, predator.maxAccel, predator.visionAngle, predator.maxSteering, geno, predator.lastScale)
				predators_alive.append(temp_predator)
		for predator in self.pollPredators:
			if self.controller.repr == 2:
				geno = predator.pushCode.getList()
			else:
				geno = predator.geno

			temp_accel = predator.getAcceleration()
			temp_predator = Data_mobile(predator.pos_x, predator.pos_y, predator.vel_x, predator.vel_y, temp_accel.x, temp_accel.y, predator.energy, predator.age, predator.isAlive, predator.maxVel, predator.maxAccel, predator.visionAngle, predator.maxSteering, geno, predator.lastScale)
			predators_dead.append(temp_predator)


		# order and merge individuals of the same specie
		preys_final = list(preys_alive)
		preys_final.sort(self.descendingCmp)
		preys_final += preys_dead[::-1]

		predators_final = list(predators_alive)
		predators_final.sort(self.descendingCmp)
		predators_final += predators_dead[::-1]


		# save the data on files
		f =  open('metrics/data/prey_'+suffix+'.pkl', 'wb')
		for prey in preys_final:
			cPickle.dump(prey, f)
		f.close()

		f =  open('metrics/data/predator_'+suffix+'.pkl', 'wb')
		for predator in predators_final:
			cPickle.dump(predator, f)
		f.close()

	def load_metrics_preys(self):
		suffix = self.controller.reprType[self.controller.repr]

		preys = breve.allInstances( "Prey" )
		tam = len(preys)

		preys_list = []
		index_list = list(range(0, tam))

		# preys
		f =  open('metrics/data/prey_'+suffix+'.pkl', 'rb')
		while True:
			try:
				data_prey = cPickle.load(f)
				preys_list.append(data_prey.geno)
			except EOFError:
				break
		f.close()

		if tam < len(preys_list):
			preys_list = preys_list[0:tam]
		
		random.shuffle(preys_list)
		random.shuffle(index_list)
		index_list = index_list[0:len(preys_list)]
	
		for (index, geno) in zip(index_list, preys_list):
			temp_prey = preys[index]

			if self.controller.repr == 2:
				temp_prey.pushInterpreter.clearStacks()
				temp_prey.pushCode.setFrom(geno)
			else:
				temp_prey.geno = geno

	def load_metrics_predators(self):
		suffix = self.controller.reprType[self.controller.repr]

		predators = breve.allInstances( "Predator" )
		tam = len(predators)

		predators_list = []
		index_list = list(range(0, tam))

		# predators
		f =  open('metrics/data/predator_'+suffix+'.pkl', 'rb')
		while True:
			try:
				data_predator = cPickle.load(f)
				predators_list.append(data_predator.geno)
			except EOFError:
				break
		f.close()

		if tam < len(predators_list):
			predators_list = predators_list[0:tam]
		
		random.shuffle(predators_list)
		random.shuffle(index_list)
		index_list = index_list[0:len(predators_list)]
	
		for (index, geno) in zip(index_list, predators_list):
			temp_predator = predators[index]

			if self.controller.repr == 2:
				temp_predator.pushInterpreter.clearStacks()
				temp_predator.pushCode.setFrom(geno)
			else:
				temp_predator.geno = geno

	def addTotalFoodSupply(self, num):
		self.totalFoodSupply += num;

	def addRandomFeederIfNecessary( self, rapid=False):
		while (self.maxFoodSupply-self.totalFoodSupply) >= self.maxCreatedFoodSupply:
			self.createFeeder(1, rapid)

	# funcions used by breeding
	def selectNearParent( self, parent1, specie):
		# neighbour = parent1.getNeighbors()
		birds = breve.objectList()
		neighbour = breve.allInstances( specie )

		for item in neighbour:
			if item.isA( specie ) and item.isAlive:
				birds.append( item )
		parent2 = self.tournament(birds, 5)
		return parent2

	def selectParent( self, specie):
		birds = breve.objectList()
		for item in breve.allInstances( specie ):
			if item.isAlive:
				birds.append( item )
		parent = self.tournament(birds, 5)
		return parent

	def tournament(self, birds, dim):
		leng = breve.length(birds)
		if leng == 0:
			return None
		candidate = birds[random.randint(0,leng-1)]
		fit = self.fitness(candidate)
		for i in range(dim-1):
			temp_candidate = birds[random.randint(0,leng-1)]
			temp_fit = self.fitness(temp_candidate)
			if temp_fit > fit:
				candidate = temp_candidate
				fit = temp_fit
		return candidate

	def fitness(self, bird):
		return bird.energy * (1/float(1+math.exp(- ((bird.age-100)/12.0) )))
		#return bird.energy

	def duplicateGenes(self, newBird1, newBird2, parent1, parent2):
		if self.controller.repr == 0:
			newBird1.geno = list(parent1.geno)
			newBird2.geno = list(parent2.geno)

		elif self.controller.repr == 1:
			newBird1.geno = self.tree_copy(parent1.geno)
			newBird2.geno = self.tree_copy(parent2.geno)
			self.fill_parents(newBird1.geno)
			self.fill_parents(newBird2.geno)

		elif self.controller.repr == 2:
			newBird1.pushInterpreter.clearStacks()
			newBird2.pushInterpreter.clearStacks()

			c1 = breve.createInstances( breve.PushProgram, 1 )
			c2 = breve.createInstances( breve.PushProgram, 1 )

			parent1.pushInterpreter.copyCodeStackTop( c1 )
			parent2.pushInterpreter.copyCodeStackTop( c2 )

			newBird1.pushInterpreter.pushCode( c1 )
			newBird2.pushInterpreter.pushCode( c2 )

			breve.deleteInstances( c1 )
			breve.deleteInstances( c2 )

	def crossover(self, newBird1, newBird2, parent1, parent2):
		if self.controller.repr == 0:
			# one point crossover
			pos = random.randint(0, len(parent1.geno))
			newBird1.geno = parent1.geno[0:pos] + parent2.geno[pos:]
			newBird2.geno = parent2.geno[0:pos] + parent1.geno[pos:]

		elif self.controller.repr == 1:
			newBird1.geno, newBird2.geno = self.tree_crossover(parent1.geno, parent2.geno)

		elif self.controller.repr == 2:
			self.crossover_push(newBird1, parent1, parent2)
			self.crossover_push(newBird2, parent2, parent1)

	def crossover_push(self, newBird, parent1, parent2):
		newBird.pushInterpreter.clearStacks()
		error = True

		c1 = breve.createInstances( breve.PushProgram, 1 )
		c2 = breve.createInstances( breve.PushProgram, 1 )
		c3 = breve.createInstances( breve.PushProgram, 1 )
		parent1.pushInterpreter.copyCodeStackTop( c1 )
		if ( c1.getSize() > 0 ):
			parent2.pushInterpreter.copyCodeStackTop( c2 )
			if ( c2.getSize() > 0 ):
				c3.crossover( c1, c2, newBird.pushInterpreter )

				if len(c3.getList()) > 0:
					newBird.pushInterpreter.pushCode( c3 )
					a = newBird.pushCode
					newBird.pushCode = c3
					c3 = a
					error = False

		if error:
			newBird.pushInterpreter.pushCode( c1 )
			a = newBird.pushCode
			newBird.pushCode = c1
			c1 = a

		breve.deleteInstances( c1 )
		breve.deleteInstances( c2 )
		breve.deleteInstances( c3 )

	def mutate(self, newBird):
		if self.controller.repr == 0:
			# uniform mutation
			for i in range(len(newBird.geno)):
				prob = random.random()
				if prob <= self.prob_mutation:
					newBird.geno[i] += random.uniform(-0.5, 0.5)

		elif self.controller.repr == 1:
			prob = random.random()
			if prob <= self.prob_mutation:
				self.tree_mutation(newBird.geno, newBird.getType())

		elif self.controller.repr == 2:
			prob = random.random()
			if prob <= self.prob_mutation:

				c = breve.createInstances( breve.PushProgram, 1 )
				newBird.pushInterpreter.copyCodeStackTop( c )
				c.mutate( newBird.pushInterpreter )
				newBird.pushInterpreter.clearStacks()

				if len(c.getList()) > 0:
					newBird.pushInterpreter.pushCode( c )
					b = newBird.pushCode
					newBird.pushCode = c
					breve.deleteInstances( b )
				else:
					newBird.pushInterpreter.pushCode( newBird.pushCode )

	def createNewBird(self, newBird, parent1, parent2):
		p = random.uniform(0,1)
		v = random.uniform(0,1)
		newBird.changePos(p*parent1.pos_x+(1-p)*parent2.pos_x,p*parent1.pos_y+(1-p)*parent2.pos_y)
		newBird.changeVel(v*parent1.vel_x+(1-v)*parent2.vel_x,v*parent1.vel_y+(1-v)*parent2.vel_y)
		newBird.changeAccel(0,0)
		newBird.age = 0
		newBird.energy = 0.5
		newBird.isAlive = True
		newBird.setNewColor()
		
	def evolutionayAlgorithm(self, array):
		if breve.length(array) < 2:
			return

		newBird1 = array[0]
		newBird2 = array[1]
		kind = newBird1.getType()

		# classic evolutionay algorithm
		parent1 = self.selectParent(kind)
		if parent1 is not None:
			parent2 = self.selectNearParent(parent1, kind)
			if parent2 is not None:
				self.crossover(newBird1, newBird2, parent1, parent2)
				self.mutate(newBird1)
				self.mutate(newBird2)

				self.createNewBird(newBird1, parent2, parent1)
				self.createNewBird(newBird2, parent1, parent2)
				
				array.remove(newBird1)
				array.remove(newBird2)

				# update IDs
				if kind == 'Prey':
					newBird1.ID = self.preyID
					newBird2.ID = self.preyID+1
					self.preyID += 2
				else:
					newBird1.ID = self.predatorID
					newBird2.ID = self.predatorID+1
					self.predatorID += 2

				self.save_log( kind + str(parent1.ID) + ', ' + kind + str(parent2.ID) + '-->' + kind + str(newBird1.ID) + ', ' + kind + str(newBird2.ID))


	# GP code
	def create_random_tree(self, depth, specie):
		if depth < 1:
		    return None
		return Node(self.create_random_tree(depth-1, specie), self.create_random_tree(depth-1, specie), specie)


	def fill_parents(self, tree):
	    if tree.right is not None:
	        # node
	        tree.left.parent = tree
	        tree.right.parent = tree

	        self.fill_parents(tree.left)
	        self.fill_parents(tree.right)


	def compare_trees(self, tree1, tree2):
		temp = 0
		if tree1.data != tree2.data:
			temp = 1

		# Leaf
		if tree1.right is None or tree2.right is None:
			return temp, 1
		
		# Node
		v1, t1 = self.compare_trees(tree1.left, tree2.left)
		v2, t2 = self.compare_trees(tree1.right, tree2.right)
		v3 = v1 + v2 + temp
		t3 = t1 + t2 + 1
		return v3, t3

	def print_tree(self, tree):
	    if tree.right is None:
	        # leaf
	        print tree.data, 
	    else:
	        # node
	        print "(",
	        self.print_tree(tree.left)
	        print tree.data,
	        self.print_tree(tree.right)
	        print ")",


	def run_code(self, indiv, tree):
	    if tree.right is None:
	        # leaf
	        exec "x, y = " + tree.data
	        return [x, y]
	    else:
	        # node_list
	        # for some reason this don't work, probability it don't work in python 2.3
	        # return [0 if tree.data == "/" and y == 0 else eval('x'+tree.data+'y') for x, y in zip(self.run_code(indiv, tree.left), self.run_code(indiv, tree.right))]

	        result = []
	        for x, y in zip(self.run_code(indiv, tree.left), self.run_code(indiv, tree.right)):
	        	if tree.data == "/" and y == 0:
	        		result.append(0)
	        	else:
	        		result.append(eval('x'+tree.data+'y'))
	        return result


	def select_random_node(self, tree, list_nodes):
	    if tree.right is not None:
	        list_nodes.append(tree)
	        self.select_random_node(tree.left, list_nodes)
	        self.select_random_node(tree.right, list_nodes)


	def replace_tree(self, old_sub_tree, new_sub_tree):
	    parent = old_sub_tree.parent

	    if parent.left == old_sub_tree:
	        parent.left = new_sub_tree
	    else:
	        parent.right = new_sub_tree


	def tree_copy(self, parent1):
	    if parent1 is None:
	        return None

	    current_node = copy.deepcopy(parent1)
	    current_node.left = self.tree_copy(parent1.left)
	    current_node.right = self.tree_copy(parent1.right)
	    return current_node


	def tree_mutation(self, tree, specie):
		node_list = []
		self.select_random_node(tree, node_list)
		if len(node_list)-1 < 1:
			return
		index = random.randint(1, len(node_list)-1)
		depth = random.randint(1, 5)
		new_sub_tree = self.create_random_tree(depth, specie)
		self.replace_tree(node_list[index], new_sub_tree)
		self.fill_parents(tree)


	def tree_crossover(self, parent1, parent2):
	    tree_child1 = self.tree_copy(parent1)
	    tree_child2 = self.tree_copy(parent2)
	    self.fill_parents(tree_child1)
	    self.fill_parents(tree_child2)

	    node_list1 = []
	    self.select_random_node(tree_child1, node_list1)
	    if len(node_list1)-1 < 1:
	    	return tree_child1, tree_child2
	    index1 = random.randint(1, len(node_list1)-1)

	    node_list2 = []
	    self.select_random_node(tree_child2, node_list2)
	    if len(node_list2)-1 < 1:
	    	return tree_child1, tree_child2
	    index2 = random.randint(1, len(node_list2)-1)

	    subtree_parent1 = node_list1[index1]
	    subtree_parent2 = node_list2[index2]

	    self.replace_tree(subtree_parent1, subtree_parent2)
	    self.replace_tree(subtree_parent2, subtree_parent1)
	    self.fill_parents(tree_child1)
	    self.fill_parents(tree_child2)

	    return tree_child1, tree_child2

	# metric functions
	def averageFitness(self, specie):
		temp_list = breve.allInstances( specie )
		average = 0
		tam = 0
		for item in temp_list:
			if item.isAlive:
				average += self.fitness(item)
				tam += 1

		if tam == 0:
			return 0
		return average/(tam*1.0)

	def bestFitness(self, specie):
		temp_list = breve.allInstances( specie )
		best = -1
		for item in temp_list:
			if item.isAlive:
				temp_best = self.fitness(item)
				if temp_best > best:
					best = temp_best
		return best

	def diversity_genotype(self, specie):
		tam = 0
		result = 0

		boid_list = []
		temp_list = breve.allInstances( specie )
		for item in temp_list:
			if item.isAlive:
				boid_list.append(item)

		for i in range(0, len(boid_list)):
			for y in range(i+1, len(boid_list)):
				result += self.compare_genotype(boid_list[i], boid_list[y])
				tam += 1

		if tam == 0:
			return 0
		return result / (tam*1.0)

	def compare_genotype(self, item1, item2):
		result = 0

		if self.repr == 0:
			for i in range(len(item1.geno)):
				if abs(item1.geno[i]-item2.geno[i]) > 0.1:
					result += 1
			result /= (len(item1.geno)*1.0)
		elif self.repr == 1:
			result, tam = self.compare_trees(item1.geno, item2.geno)
			result /= (tam*1.0)
		elif self.repr == 2:
			result = item1.pushCode.getTopLevelDifference(item2.pushCode) / (max(item1.pushCode.getTopLevelSize(), item2.pushCode.getTopLevelSize())*1.0)
			
		return result

	def save_log( self, string, initiation=False ):
		if self.evaluatePrey or self.evaluatePredator:
			suffix = self.controller.reprType[self.controller.repr]

			# check folders
			directory = 'metrics/log'
			if not os.path.exists(directory):
				os.makedirs(directory)

			string_final = ''
			if not initiation:
				string_final += str(self.current_iteraction) + '\t'
			string_final += string + '\n'

			# save data
			f =  open( directory + '/' + self.date+'_'+suffix+'_prey_log.txt', 'a+' )
			f.write( string_final )
			f.close()


	def resetSimulation( self ):
		# clean data

		self.listPrey_BestFitness = []
		self.listPrey_AverageFitness = []
		self.listPrey_Diversity = []
		self.tempPrey_Best = 0
		self.tempPrey_Average= 0
		self.tempPrey_Diversity= 0
		self.listPredator_BestFitness = []
		self.listPredator_AverageFitness = []
		self.listPredator_Diversity = []
		self.tempPredator_Best = 0
		self.tempPredator_Average = 0
		self.tempPredator_Diversity = 0
		self.list_phase_portrait = []
		self.tempPrey_pp = 0
		self.tempPredator_pp = 0

		# Simulation
		self.initialNumPreys = self.numPreys = 90
		self.initialNumPredators = self.numPredators = 30
		self.numDeadPreys = 0
		self.numDeadPredators = 0

		# List
		self.pollPreys = breve.objectList()
		self.pollPredators = breve.objectList()

		# Generation
		self.current_iteraction = 0
		self.endSimulation = False
		self.preyID = 1
		self.predatorID = 1


		# remove all agents

		for prey in breve.allInstances( "Prey" ):
			prey.dropDead(corpse=False)

		for predator in breve.allInstances( "Predator" ):
			predator.dropDead(corpse=False)

		for corpse in breve.allInstances( "Corpse" ):
			breve.deleteInstances( corpse.shape )
			breve.deleteInstances( corpse )

		# add new agents

		self.add_new_agents()


	def iterate( self ):
		if self.current_iteraction < self.maxIteraction:
			preys_list = []
			predators_list = []

			# to record the simulation in a movie
			if self.isToRecord and not self.movie:
				suffix = self.controller.reprType[self.controller.repr].upper()
				self.movie = breve.createInstances( breve.Movie, 1 )
				self.movie.record( 'BOID_'+suffix+'.mpeg' )

			# remove dead agents
			for prey in breve.allInstances( "Prey" ):
				if prey.isAlive:
					if prey.energy <= 0:
						if self.evaluatePredator:
							prey.initializeRandomly2()
							preys_list.append(prey)
							self.save_log( 'one prey died and started again randomly with ID=' + str(prey.ID) )
						else:
							prey.dropDead(self.controller.showCorpse)
							self.save_log( 'one prey died with ID=' + str(prey.ID) )
					else:
						preys_list.append(prey)
			for predator in breve.allInstances( "Predator" ):
				if predator.isAlive:
					if predator.energy <= 0:
						if self.evaluatePrey:
							predator.initializeRandomly2()
							predators_list.append(predator)
							self.save_log( 'one predator died and started again randomly with ID=' + str(predator.ID) )
						else:
							predator.dropDead(self.controller.showCorpse)
							self.save_log( 'one predator died with ID=' + str(predator.ID) )
					else:
						predators_list.append(predator)

			# update neighborhoods
			self.updateNeighbors()

			# moviment of Prey
			self.numPreys = len(preys_list)
			for prey in preys_list:
				prey.fly()

			# moviment of Predator
			self.numPredators = len(predators_list)
			for predator in predators_list:
				predator.fly()

			# management of the energy from feeders
			self.totalFoodSupply = 0
			for feeder in breve.allInstances( "Feeder" ):
				if feeder.rapid:
					feeder.rapidGrow()
					self.totalFoodSupply += feeder.VirtualEnergy
				self.totalFoodSupply += feeder.energy
				if feeder.energy <= 0 and not feeder.rapid:
					breve.deleteInstances( feeder.shape )
					breve.deleteInstances( feeder )
			self.addRandomFeederIfNecessary(rapid=True)

			# vanish corpse
			for corpse in breve.allInstances( "Corpse" ):
				corpse.changeColor()
				if sum(corpse.getColor()) <= 0:	
					breve.deleteInstances( corpse.shape )
					breve.deleteInstances( corpse )

			if self.evaluatePrey:
				self.tempPrey_Average += self.averageFitness('Prey')
				self.tempPrey_Best += self.bestFitness('Prey')
				self.tempPrey_Diversity += self.diversity_genotype('Prey')
			if self.evaluatePredator:
				self.tempPredator_Average += self.averageFitness('Predator')
				self.tempPredator_Best += self.bestFitness('Predator')
				self.tempPredator_Diversity += self.diversity_genotype('Predator')
			if self.phase_portrait:
				self.tempPrey_pp += self.numPreys
				self.tempPredator_pp += self.numPredators

			self.current_iteraction += 1
			# breeding
			if self.current_iteraction % self.breeding_season == 0:
				if self.evaluatePrey:
					self.listPrey_AverageFitness.append(self.tempPrey_Average/(self.breeding_season*1.0))
					self.listPrey_BestFitness.append(self.tempPrey_Best/(self.breeding_season*1.0))
					self.listPrey_Diversity.append(self.tempPrey_Diversity/(self.breeding_season*1.0))
					self.tempPrey_Average = 0
					self.tempPrey_Best = 0
					self.tempPrey_Diversity = 0

				if self.evaluatePredator:
					self.listPredator_AverageFitness.append(self.tempPredator_Average/(self.breeding_season*1.0))
					self.listPredator_BestFitness.append(self.tempPredator_Best/(self.breeding_season*1.0))
					self.listPredator_Diversity.append(self.tempPredator_Diversity/(self.breeding_season*1.0))
					self.tempPredator_Average = 0
					self.tempPredator_Best = 0
					self.tempPredator_Diversity = 0

				if self.phase_portrait:
					self.list_phase_portrait.append([self.tempPrey_pp/(self.breeding_season*1.0), self.tempPredator_pp/(self.breeding_season*1.0)])
					self.tempPrey_pp = 0
					self.tempPredator_pp = 0

				# preys
				if not self.evaluatePredator:
					if self.evaluatePrey:
						tam_temp = (self.initialNumPreys*self.evaluation_survivor)
						if self.numPreys > tam_temp:
							preys_list.sort(self.descendingCmp)
							while self.numPreys != tam_temp:
								temp_boid = preys_list[-1]
								temp_boid.dropDead(False)
								preys_list.remove(temp_boid)
								self.numPreys -= 1
								self.save_log( 'one prey died with ID=' + str(temp_boid.ID) )
						tam_prey = int(math.ceil((self.initialNumPreys-self.numPreys)/2))
					else:
						tam_prey = int(math.ceil((self.breeding_inc*self.numPreys)/2))

					if breve.length(self.pollPreys) < tam_prey*2:
						new_prey = 2*tam_prey - breve.length(self.pollPreys)
						breve.createInstances( breve.Prey, new_prey).dropDead(False)
					
					for i in range(tam_prey):
						self.evolutionayAlgorithm(self.pollPreys)
						self.numPreys += 2

				# predators
				if not self.evaluatePrey:
					if self.evaluatePredator:
						tam_temp = (self.initialNumPredators*self.evaluation_survivor)
						if self.numPredators > tam_temp:
							predators_list.sort(self.descendingCmp)
							while self.numPredators != tam_temp:
								temp_boid = predators_list[-1]
								temp_boid.dropDead(False)
								predators_list.remove(temp_boid)
								self.numPredators -= 1
								self.save_log( 'one predator died with ID=' + str(temp_boid.ID) )
						tam_predator = int(math.ceil((self.initialNumPredators-self.numPredators)/2))
					else:
						predator_max = self.numPreys*self.max_pop_predators
						predator_breed = self.breeding_inc*self.numPredators
						tam_predator = int(math.ceil(min(predator_max, predator_breed)/2))
					
					if breve.length(self.pollPredators) < tam_predator*2:
						new_preds = 2*tam_predator - breve.length(self.pollPredators)
						breve.createInstances( breve.Predator, new_preds).dropDead(False)
					
					for i in range(tam_predator):
						self.evolutionayAlgorithm(self.pollPredators)
						self.numPredators += 2
					
			# immigrants
			else:
				if not self.evaluatePredator:
					if self.numPreys < 0.2*self.initialNumPreys:
						self.save_log( 'immigrant preys added' )
						self.revive(self.pollPreys, math.floor(0.15*self.initialNumPreys))
						self.createPreys(math.floor(0.05*self.initialNumPreys))
				if not self.evaluatePrey:
					if self.numPredators < 0.2*self.initialNumPredators:
						self.save_log( 'immigrant predators added' )
						self.revive(self.pollPredators, math.floor(0.15*self.initialNumPredators))
						self.createPredators(math.floor(0.05*self.initialNumPredators))
			
			# checkpoint
			if self.isToSave and self.current_iteraction % (self.breeding_season*self.save_generation) == 0:
				self.save_data()


			# to display on screen
			self.setDisplayText("Generation: "+str((int) (math.ceil(self.current_iteraction/self.breeding_season))), xLoc = -0.950000, yLoc = -0.550000, messageNumber = 5, theColor = breve.vector( 1, 1, 1 ))
			self.setDisplayText("Preys Alive: "+str(self.numPreys), xLoc = -0.950000, yLoc = -0.650000, messageNumber = 4, theColor = breve.vector( 1, 1, 1 ))
			self.setDisplayText("Predators Alive: "+str(self.numPredators), xLoc = -0.950000, yLoc = -0.750000, messageNumber = 3, theColor = breve.vector( 1, 1, 1 ))
			self.setDisplayText("Dead Preys: "+str(self.numDeadPreys), xLoc = -0.950000, yLoc = -0.850000, messageNumber = 2, theColor = breve.vector( 1, 1, 1 ))
			self.setDisplayText("Dead Predators: "+str(self.numDeadPredators), xLoc = -0.950000, yLoc = -0.950000, messageNumber = 1, theColor = breve.vector( 1, 1, 1 ))

			# needed to move the agents with velocity and acceleration
			# also needed to detect collisions
			# print str(self.numBirdsBirth)
			breve.Control.iterate( self )

		else:
			if not self.endSimulation:
				self.endSimulation = True

				# save simulation
				if self.isToSave:
					self.save_data()

				# save preys and predators
				if self.isToEvaluate:
					self.save_metrics()

				if self.evaluatePrey:
					suffix = self.controller.reprType[self.controller.repr]
					
					# check folders
					directory_base = 'metrics/results/'+self.date+'_'+suffix+'_prey_'
					directory_list = ['average', 'best', 'diversity']

					for directory in directory_list:
						if not os.path.exists(directory_base+directory):
							os.makedirs(directory_base+directory)

	    			# save data
					f =  open(directory_base+directory_list[0]+'/'+str(self.current_run)+'.txt', 'w')
					for item in self.listPrey_AverageFitness:
  						f.write("%s\n" % item)
					f.close()

					f =  open(directory_base+directory_list[1]+'/'+str(self.current_run)+'.txt', 'w')
					for item in self.listPrey_BestFitness:
  						f.write("%s\n" % item)
  					f.close()

  					f =  open(directory_base+directory_list[2]+'/'+str(self.current_run)+'.txt', 'w')
					for item in self.listPrey_Diversity:
  						f.write("%s\n" % item)
					f.close()

				if self.evaluatePredator:
					suffix = self.controller.reprType[self.controller.repr]
					
					# check folders
					directory_base = 'metrics/results/'+self.date+'_'+suffix+'_predator_'
					directory_list = ['average', 'best', 'diversity']

					for directory in directory_list:
						if not os.path.exists(directory_base+directory):
							os.makedirs(directory_base+directory)

	    			# save data
					f =  open(directory_base+directory_list[0]+'/'+str(self.current_run)+'.txt', 'w')
					for item in self.listPredator_AverageFitness:
  						f.write("%s\n" % item)
					f.close()

					f =  open(directory_base+directory_list[1]+'/'+str(self.current_run)+'.txt', 'w')
					for item in self.listPredator_BestFitness:
  						f.write("%s\n" % item)
					f.close()

					f =  open(directory_base+directory_list[2]+'/'+str(self.current_run)+'.txt', 'w')
					for item in self.listPredator_Diversity:
  						f.write("%s\n" % item)
					f.close()

				if self.phase_portrait:
					suffix = self.controller.reprType[self.controller.repr]
					directory = 'metrics/phase_portrait/results/'+self.date+'_'+suffix
					if not os.path.exists(directory):
						os.makedirs(directory)

					f =  open(diversity+'/'+str(self.current_run)+'.txt', 'w')
					for (item1, item2) in self.list_phase_portrait:
  						f.write("%s %s\n" % (item1, item2))
					f.close()

				self.save_log( '\n--- Ended run ' + str(self.current_run) + ' ---\n\n' )
				self.current_run += 1
				if (self.evaluatePrey or self.evaluatePredator) and self.current_run < self.runs:
					self.resetSimulation()
				else:
					if self.isToRecord and self.movie:
						self.movie.close()
						breve.deleteInstances( self.movie )
						self.movie = None


breve.Swarm = Swarm


class Feeder (breve.Stationary ):
	def __init__( self ):
		breve.Stationary.__init__( self )
		self.shape = None
		self.pos_x = 0
		self.pos_y = 0
		self.energy = 0
		self.lastScale = 1
		self.rapid = False
		self.VirtualEnergy = 0
		Feeder.init( self )

	def initializeRandomly( self, x, y, rapid):
		self.changePos(x,y)

		if rapid:
			self.VirtualEnergy = random.uniform(self.controller.minCreatedFoodSupply, self.controller.maxCreatedFoodSupply)
			self.rapid = True
			self.controller.addTotalFoodSupply(self.VirtualEnergy)
		else:
			self.energy = random.uniform(self.controller.minCreatedFoodSupply, self.controller.maxCreatedFoodSupply)
			self.controller.addTotalFoodSupply(self.energy)
		self.adjustSize()

	def initializeFromData( self, pos_x, pos_y, energy, lastScale, rapid, VirtualEnergy):
		self.changePos(pos_x, pos_y)
		self.energy = energy
		self.lastScale = lastScale
		self.rapid = rapid
		self.VirtualEnergy = VirtualEnergy
		self.shape.scale(breve.vector( lastScale, lastScale, lastScale) )  

	def rapidGrow(self):
		if self.rapid:
			if self.VirtualEnergy > 0.5:
				self.energy += 0.5
				self.VirtualEnergy -= 0.5
			else:
				self.energy += self.VirtualEnergy
				self.VirtualEnergy = 0
				self.rapid = False
			self.adjustSize()

	def changePos(self, x, y):
		if x < self.controller.minX-10:
			x += (self.controller.maxX+10)-(self.controller.minX-10)
		elif x > self.controller.maxX+10:
			x -= (self.controller.maxX+10)-(self.controller.minX-10)
		if y < self.controller.minY-10:
			y += (self.controller.maxY+10)-(self.controller.minY-10)
		elif y > self.controller.maxY+10:
			y -= (self.controller.maxY+10)-(self.controller.minY-10)
			
		self.pos_x = x
		self.pos_y = y
		self.move( breve.vector(x,y,0) )

	def getEnergy(self):
		return self.energy

	def addEnergy(self, num):
		self.energy += num
		if self.energy < 0:
			self.energy = 0
		self.adjustSize()

	def adjustSize( self ):
		radius = breve.breveInternalFunctionFinder.sqrt( self, self.energy )
		newScale = ( ( radius ) + 0.000010 )
		if ( newScale == self.lastScale ):
			return

		newScale = ( newScale / self.lastScale )
		self.shape.scale( breve.vector( newScale, newScale, newScale ) )
		self.lastScale = ( ( radius ) + 0.000010 )

	def init( self ):
		self.shape = breve.createInstances(breve.Sphere, 1).initWith(0.300000)

		self.setShape(self.shape)
		self.setColor( breve.vector(1, 1, 0) )


breve.Feeder = Feeder


class Corpse( breve.Mobile ):
	def __init__( self ):
		breve.Mobile.__init__( self )
		self.energy = 0
		self.lastScale = 1
		self.shape = None
		# self.shape = breve.createInstances( breve.PolygonCone, 1 ).initWith( 5, 0.200000, 0.100000 )
		# self.setShape( self.shape )
	
	def adjustSize( self ):
		newScale = ( ( self.energy * 10 ) + 0.500000 )
		self.shape.scale( breve.vector( ( newScale / self.lastScale ), 1, ( newScale / self.lastScale ) ) )
		self.lastScale = newScale

	def cross( self, v1, v2 ):
		x = ( ( v1.y * v2.z ) - ( v1.z * v2.y ) )
		y = ( ( v1.z * v2.x ) - ( v1.x * v2.z ) )
		z = ( ( v1.x * v2.y ) - ( v1.y * v2.x ) )
		return breve.vector( x, y, z )

	def myPoint( self, theVertex, theLocation ):
		v = self.cross( theVertex, theLocation )
		a = breve.breveInternalFunctionFinder.angle( self, theVertex, theLocation )
		if ( breve.length( v ) == 0.000000 ):
			self.rotate( theVertex, 0.100000 )
			return
		self.rotate( v, a )

	def changeColor( self ):
		colorVector = self.getColor()
		colorDec = 0.05
		colorVector = breve.vector(max(colorVector[0]-colorDec,0),max(colorVector[1]-colorDec,0),max(colorVector[2]-colorDec,0),)
		self.setColor(colorVector)


breve.Corpse = Corpse


class Prey( breve.Mobile ):
	def __init__( self ):
		breve.Mobile.__init__( self )
		self.shape = None
		self.ID = -1

		# can be changed
		self.pos_x = -9999
		self.pos_y = -9999
		self.vel_x = 0
		self.vel_y = 0

		# change with time
		self.energy = 1.0
		self.age = 0
		self.isAlive = True

		# static
		self.maxVel = 0.5
		self.maxAccel = 2
		self.visionAngle = 150
		self.maxSteering = 30
		self.geno = None

		# PUSH
		if self.controller.repr == 2:
			self.pushInterpreter = None
			self.pushCode = None
			self.createPush()

		self.lastScale = 1
		Prey.init( self )

	# PUSH
	def createPush(self):
		self.pushInterpreter = breve.createInstances( breve.PushInterpreter, 1 )
		self.pushInterpreter.readConfig( 'pushConfigFile.config' )
		self.pushInterpreter.addInstruction( self, 'separation' )
		self.pushInterpreter.addInstruction( self, 'alignment' )
		self.pushInterpreter.addInstruction( self, 'cohesion' )
		self.pushInterpreter.addInstruction( self, 'target' )
		self.pushInterpreter.addInstruction( self, 'currentVelocity' )
		self.pushInterpreter.addInstruction( self, 'currentEnergy' )
		self.pushInterpreter.addInstruction( self, 'randV' )
		self.pushInterpreter.addInstruction( self, 'flee' )
		self.pushInterpreter.setEvaluationLimit( 50 )
		self.pushInterpreter.setListLimit( 50 )
		self.pushCode = breve.createInstances( breve.PushProgram, 1 )
		self.pushCode.makeRandomCode( self.pushInterpreter, 80 )


	def initializeRandomly( self, x, y):
		self.changePos(x,y)

		vel_x = random.uniform(-self.maxVel, self.maxVel)
		vel_y = random.uniform(-self.maxVel, self.maxVel)
		self.changeVel(vel_x,vel_y)
		self.changeAccel(0,0)

		self.age = 0
		self.setNewColor()

		if self.controller.repr == 0:
			self.geno = [random.uniform(-5, 5) for x in range(6)]
		elif self.controller.repr == 1:
			self.geno = self.controller.create_random_tree(self.controller.initial_depth, "Prey")
		elif self.controller.repr == 2:
			self.pushCode = breve.createInstances( breve.PushProgram, 1 )
			self.pushCode.makeRandomCode( self.pushInterpreter, 80 )
			self.pushInterpreter.pushVector( breve.vector(self.vel_x,self.vel_y,0) )

	def initializeRandomly2(self):
 		x = random.uniform(self.controller.minX, self.controller.maxX)
 		y = random.uniform(self.controller.minY, self.controller.maxY)
 		self.changePos(x,y)
 
 		vel_x = random.uniform(-self.maxVel, self.maxVel)
 		vel_y = random.uniform(-self.maxVel, self.maxVel)
 		self.changeVel(vel_x,vel_y)
 
 		self.changeAccel(0,0)
 		self.age = 0
 		self.energy = 0.5

	def initializeFromData(self, pos_x, pos_y, vel_x, vel_y, accel_x, accel_y, energy, age, isAlive, maxVel, maxAccel, visionAngle, maxSteering, geno, lastScale):
		self.changePos(pos_x, pos_y)
		self.changeVel(vel_x, vel_y)
		self.changeAccel(accel_x, accel_y)

		self.energy = energy
		self.age = age
		self.isAlive = isAlive
		self.maxVel = maxVel
		self.maxAccel = maxAccel
		self.visionAngle = visionAngle
		self.maxSteering = maxSteering
		self.lastScale = lastScale

		breve.deleteInstances( self.shape )
		self.shape = breve.createInstances( breve.myCustomShape, 1 )
		self.setShape( self.shape )
		self.shape.scale( breve.vector( lastScale , 1, lastScale ) )

		self.setNewColor()
		
		if self.controller.repr == 2:
			self.pushInterpreter.clearStacks()
			self.pushCode.setFrom(geno)
		else:
			self.geno = geno

	def setNewColor( self ):
		self.setColor( breve.vector( 0, 1, 0 ) )

	def changePos(self, x, y):
		if x < self.controller.minX-10:
			x += (self.controller.maxX+10)-(self.controller.minX-10)
		elif x > self.controller.maxX+10:
			x -= (self.controller.maxX+10)-(self.controller.minX-10)
		if y < self.controller.minY-10:
			y += (self.controller.maxY+10)-(self.controller.minY-10)
		elif y > self.controller.maxY+10:
			y -= (self.controller.maxY+10)-(self.controller.minY-10)

		self.pos_x = x
		self.pos_y = y
		self.move( breve.vector(x,y,0) )

	def changeAccel(self, x, y):
		n = self.norm([x, y])
		if n > self.maxAccel:
			x = x/n * self.maxAccel
			y = y/n * self.maxAccel
		self.setAcceleration( breve.vector(x, y, 0) )
			
	def changeVel(self, x, y):
		n = self.norm([x, y])
		
		v1 = self.normalizeVector(self.vel_x, self.vel_y)
		v2 = self.normalizeVector(x, y)
		a = math.degrees(self.angle(v1, v2))
		if a > self.maxSteering:
			if self.crossproduct(v1, v2) < 0:
				an = -self.maxSteering
			else:
				an = self.maxSteering

			x, y = self.rotateVector(v1, an)
			x *= n
			y *= n
		
		if n > self.maxVel:
			x = x/n * self.maxVel
			y = y/n * self.maxVel

		self.vel_x = x
		self.vel_y = y
		self.setVelocity( breve.vector(x,y,0) )

	def normalizeVector(self, x, y):
		n = self.norm([x, y])
		if n > 0:
			x = x/n
			y = y/n
		return [x, y]

	def rotateVector(self, v, alpha):
	    alpha = -math.radians(alpha)
	    return [v[0]*math.cos(alpha)+v[1]*math.sin(alpha), -v[0]*math.sin(alpha)+v[1]*math.cos(alpha)]

	def dotproduct(self, v1, v2):
		temp = 0
		for a, b in zip(v1, v2):
			temp += (a*b)
		return temp

	def crossproduct(self, v1, v2):
		return (v1[0]*v2[1]) - (v1[1]*v2[0])

	def norm(self, v):
		try:
			return math.sqrt(self.dotproduct(v, v))
		except: 
			return 999999

	def angle(self, v1, v2):
		sub = self.norm(v1) * self.norm(v2)
		if sub == 0:
			return 0
		return math.acos(self.clean_cos(self.dotproduct(v1, v2) / sub))

	def clean_cos(self, cos_angle):
		return min(1,max(cos_angle,-1))

	def addEnergy(self, num):
		self.energy += num
		if self.energy < 0:
			self.energy = 0

	def getEnergy(self):
		return self.energy

	def eat( self, feeder ):
		if feeder.energy > 0:
			if self.energy <= 0.90:
				self.addEnergy(0.1)
				feeder.addEnergy(-0.1)
			else:
				feeder.addEnergy(self.energy-1)
				self.energy = 1.0
	
	def dropDead(self, corpse=True):
		if corpse:
			c = breve.createInstances( breve.Corpse, 1 )
			c.move( self.getLocation() )
			c.setColor (self.getColor() )
			c.energy = self.energy
			c.lastScale = self.lastScale
			c.shape = self.shape
			c.setShape( c.shape )
			c.myPoint( breve.vector( 0, 1, 0 ), self.getVelocity())
			
			self.lastScale = 1
			self.shape = breve.createInstances( breve.myCustomShape, 1 )
			self.setShape( self.shape )
			self.adjustSize()

		self.setColor(breve.vector(0,0,0))
		#just to don't overlap the animation 
		self.changePos(-9999,9999)
		self.changeVel(0,0)
		self.changeAccel(0,0)
		self.age = 0
		self.energy = 0.5
		self.isAlive = False
		self.controller.pollPreys.append(self)
		self.controller.numDeadPreys += 1


	# GP and PUSH
	def cohesion(self):
		neighbors = self.getNeighbors()
		c_x = 0
		c_y = 0
		count = 0

		v1 = self.normalizeVector(self.vel_x, self.vel_y)
		for neighbor in neighbors:

			if neighbor.isA( 'Prey' ) and neighbor.isAlive:
				v2 = self.normalizeVector(neighbor.pos_x-self.pos_x, neighbor.pos_y-self.pos_y)
				a = math.degrees(self.angle(v1, v2))

				norm = self.norm([neighbor.pos_x-self.pos_x, neighbor.pos_y-self.pos_y])
				if a <= self.visionAngle or (0 < norm < self.controller.separationZone):

					if 0 < norm < self.controller.socialZone:
						c_x += neighbor.pos_x
						c_y += neighbor.pos_y
						count += 1

		if count > 0:
			c_x /= count
			c_y /= count

		if self.controller.repr == 2:
			self.pushInterpreter.pushVector( breve.vector(c_x, c_y, 0) )
			return
		return [c_x, c_y]

	def alignment(self):
		neighbors = self.getNeighbors()
		a_x = 0
		a_y = 0
		count = 0
		
		v1 = self.normalizeVector(self.vel_x, self.vel_y)
		for neighbor in neighbors:

			if neighbor.isA( 'Prey' ) and neighbor.isAlive:
				v2 = self.normalizeVector(neighbor.pos_x-self.pos_x, neighbor.pos_y-self.pos_y)
				a = math.degrees(self.angle(v1, v2))
				
				norm = self.norm([neighbor.pos_x-self.pos_x, neighbor.pos_y-self.pos_y])
				if a <= self.visionAngle or (0 < norm < self.controller.separationZone):

					if 0 < norm < self.controller.socialZone:
						a_x += neighbor.vel_x
						a_y += neighbor.vel_y
						count += 1

		if count > 0:
			a_x /= count
			a_y /= count
			
		if self.controller.repr == 2:
			self.pushInterpreter.pushVector( breve.vector(a_x, a_y, 0) )
			return
		return [a_x, a_y]

	def separation(self):
		neighbors = self.getNeighbors()
		s_x = 0
		s_y = 0
		count = 0
		
		v1 = self.normalizeVector(self.vel_x, self.vel_y)
		for neighbor in neighbors:

			if neighbor.isA( 'Prey' ) and neighbor.isAlive:
				v2 = self.normalizeVector(neighbor.pos_x-self.pos_x, neighbor.pos_y-self.pos_y)
				a = math.degrees(self.angle(v1, v2))

				norm = self.norm([neighbor.pos_x-self.pos_x, neighbor.pos_y-self.pos_y])
				if a <= self.visionAngle or (0 < norm < self.controller.separationZone):

					if 0 < norm < self.controller.separationZone:
						# separation
						v_x = self.pos_x-neighbor.pos_x
						v_y = self.pos_y-neighbor.pos_y
						v_x, v_y = self.normalizeVector(v_x, v_y)
						s_x += v_x/norm
						s_y += v_y/norm
						count += 1

		if count > 0:
			s_x /= count
			s_y /= count

		if self.controller.repr == 2:
			self.pushInterpreter.pushVector( breve.vector(s_x, s_y, 0) )
			return
		return [s_x, s_y]

	def target(self):
		neighbors = self.getNeighbors()
		t_x = 0
		t_y = 0
		dist = 99999
		count = 0
		
		v1 = self.normalizeVector(self.vel_x, self.vel_y)
		for neighbor in neighbors:

			if neighbor.isA( 'Feeder' ):
				v2 = self.normalizeVector(neighbor.pos_x-self.pos_x, neighbor.pos_y-self.pos_y)
				a = math.degrees(self.angle(v1, v2))

				norm = self.norm([neighbor.pos_x-self.pos_x, neighbor.pos_y-self.pos_y])
				if a <= self.visionAngle or (0 < norm < self.controller.separationZone):

					#target
					if norm < dist:
						dist = norm
						t_x = neighbor.pos_x-self.pos_x
						t_y = neighbor.pos_y-self.pos_y

		if self.controller.repr == 2:
			self.pushInterpreter.pushVector( breve.vector(t_x, t_y, 0) )
			return
		return [t_x, t_y]

	def flee(self):
		neighbors = self.getNeighbors()
		f_x = 0
		f_y = 0
		count = 0

		v1 = self.normalizeVector(self.vel_x, self.vel_y)
		for neighbor in neighbors:

			if neighbor.isA( 'Predator' ) and neighbor.isAlive:
				v2 = self.normalizeVector(neighbor.pos_x-self.pos_x, neighbor.pos_y-self.pos_y)
				a = math.degrees(self.angle(v1, v2))

				norm = self.norm([neighbor.pos_x-self.pos_x, neighbor.pos_y-self.pos_y])
				if a <= self.visionAngle or (0 < norm < self.controller.separationZone):

					#flee
					if 0 < norm < self.controller.separationZone:
						v_x = self.pos_x-neighbor.pos_x
						v_y = self.pos_y-neighbor.pos_y
						v_x, v_y = self.normalizeVector(v_x, v_y)
						f_x += v_x/norm
						f_y += v_y/norm
						count += 1

		if count > 0:
			f_x /= count
			f_y /= count
		
		if self.controller.repr == 2:
			self.pushInterpreter.pushVector( breve.vector(f_x, f_y, 0) )
			return
		return [f_x, f_y]

	def currentVelocity(self):
		if self.controller.repr == 2:
			self.pushInterpreter.pushVector( breve.vector(self.vel_x, self.vel_y, 0) )
			return
		return [self.vel_x, self.vel_y]

	def currentEnergy(self):
		if self.controller.repr == 2:
			self.pushInterpreter.pushVector( breve.vector(self.energy, self.energy, 0) )
			return
		return [self.energy, self.energy]

	def randV(self):
		rand_x = random.uniform(0, 10)
		rand_y = random.uniform(0, 10)

		if self.controller.repr == 2:
			self.pushInterpreter.pushVector( breve.vector(rand_x, rand_y, 0) )
			return
		return [rand_x, rand_y]


	# GA
	def calculateAccel(self):
		neighbors = self.getNeighbors()
		t_x = 0
		t_y = 0
		f_x = 0
		f_y = 0
		s_x = 0
		s_y = 0
		a_x = 0
		a_y = 0
		c_x = 0
		c_y = 0
		dist = 99999
		count = 0
		count2 = 0
		count3 = 0

		v1 = self.normalizeVector(self.vel_x, self.vel_y)
		for neighbor in neighbors:
			if not neighbor.isA( 'Corpse' ):
				v2 = self.normalizeVector(neighbor.pos_x-self.pos_x, neighbor.pos_y-self.pos_y)
				a = math.degrees(self.angle(v1, v2))
				norm = self.norm([neighbor.pos_x-self.pos_x, neighbor.pos_y-self.pos_y])

				if a <= self.visionAngle or (0 < norm < self.controller.separationZone):

					if neighbor.isA( 'Feeder' ):
						#target
						if norm < dist:
							dist = norm
							t_x = neighbor.pos_x-self.pos_x
							t_y = neighbor.pos_y-self.pos_y

						if norm <= max(neighbor.lastScale,3):
							self.eat(neighbor) 

					elif neighbor.isA( 'Prey' ) and neighbor.isAlive:
						if 0 < norm < self.controller.separationZone:
							# separation
							v_x = self.pos_x-neighbor.pos_x
							v_y = self.pos_y-neighbor.pos_y
							v_x, v_y = self.normalizeVector(v_x, v_y)
							s_x += v_x/norm
							s_y += v_y/norm
							count2 += 1

						if 0 < norm < self.controller.socialZone:
							# alignment
							a_x += neighbor.vel_x
							a_y += neighbor.vel_y
							# cohesion
							c_x += neighbor.pos_x
							c_y += neighbor.pos_y
							count += 1

					elif neighbor.isA( 'Predator' ) and neighbor.isAlive:
						#flee
						if 0 < norm < self.controller.separationZone:
							v_x = self.pos_x-neighbor.pos_x
							v_y = self.pos_y-neighbor.pos_y
							v_x, v_y = self.normalizeVector(v_x, v_y)
							f_x += v_x/norm
							f_y += v_y/norm
							count3 += 1

		if count > 0:
			a_x /= count
			a_y /= count

			c_x /= count
			c_y /= count

		if count2 > 0:
			s_x /= count2
			s_y /= count2

		if count3 > 0:
			f_x /= count3
			f_y /= count3

		rand_x = random.uniform(0, 1)
		rand_y = random.uniform(0, 1)

		c_x, c_y = self.normalizeVector(c_x, c_y)
		a_x, a_y = self.normalizeVector(a_x, a_y)
		s_x, s_y = self.normalizeVector(s_x, s_y)
		t_x, t_y = self.normalizeVector(t_x, t_y)
		f_x, f_y = self.normalizeVector(f_x, f_y)
		rand_x, rand_y = self.normalizeVector(rand_x, rand_y)

		accel_x = self.geno[0]*c_x+self.geno[1]*a_x+self.geno[2]*s_x+self.geno[3]*t_x+self.geno[4]*f_x+self.geno[5]*rand_x
		accel_y = self.geno[0]*c_y+self.geno[1]*a_y+self.geno[2]*s_y+self.geno[3]*t_y+self.geno[4]*f_y+self.geno[5]*rand_y
		return [accel_x, accel_y]

	def fly(self):
		pos = self.getLocation()
		self.changePos(pos.x, pos.y)
		self.myPoint( breve.vector( 0, 1, 0 ), self.getVelocity())

		vel = self.getVelocity()
		vel_x = vel.x
		vel_y = vel.y
		self.changeVel(vel_x, vel_y)

		if self.controller.repr == 0:
			accel_x, accel_y = self.calculateAccel()
		else:
			if self.controller.repr == 1:
				accel_x, accel_y = self.controller.run_code(self, self.geno)
			elif self.controller.repr == 2:

				# clean the stacks
				self.pushInterpreter.clearStacks()
				self.currentVelocity()

				# run the code
				self.pushInterpreter.run( self.pushCode )
				
				# get result vector
				accel = self.pushInterpreter.getVectorStackTop()
				if ( ( ( breve.breveInternalFunctionFinder.isinf( self, accel.x ) or breve.breveInternalFunctionFinder.isnan( self, accel.x ) ) or breve.breveInternalFunctionFinder.isinf( self, accel.y ) ) or breve.breveInternalFunctionFinder.isnan( self, accel.y ) ):
					accel = breve.vector( 0.000000, 0.000000, 0.000000 )

				accel_x = accel.x
				accel_y = accel.y

			# eat
			neighbors = self.getNeighbors()

			v1 = self.normalizeVector(self.vel_x, self.vel_y)
			for neighbor in neighbors:

				if neighbor.isA( 'Feeder' ):
					v2 = self.normalizeVector(neighbor.pos_x-self.pos_x, neighbor.pos_y-self.pos_y)
					a = math.degrees(self.angle(v1, v2))

					norm = self.norm([neighbor.pos_x-self.pos_x, neighbor.pos_y-self.pos_y])
					if a <= self.visionAngle or (0 < norm < self.controller.separationZone):

						if norm <= max(neighbor.lastScale,3):
							self.eat(neighbor)

		self.changeAccel(accel_x, accel_y)
		
		self.addEnergy(-0.01 -0.01*(1/float(1+math.exp(-((self.age-100)/12.0) ) ) ) )
		self.adjustSize()
		self.age += 1

	def cross( self, v1, v2 ):
		x = ( ( v1.y * v2.z ) - ( v1.z * v2.y ) )
		y = ( ( v1.z * v2.x ) - ( v1.x * v2.z ) )
		z = ( ( v1.x * v2.y ) - ( v1.y * v2.x ) )
		return breve.vector( x, y, z )

	def myPoint( self, theVertex, theLocation ):
		v = self.cross( theVertex, theLocation )
		a = breve.breveInternalFunctionFinder.angle( self, theVertex, theLocation )
		if ( breve.length( v ) == 0.000000 ):
			self.rotate( theVertex, 0.100000 )
			return
		self.rotate( v, a )

	def adjustSize( self ):
		newScale = ( ( (self.energy+0.5) * 10 ) + 0.500000 )
		self.shape.scale( breve.vector( ( newScale / self.lastScale ), 1, ( newScale / self.lastScale ) ) )
		self.lastScale = newScale

	def init( self ):
		# self.shape = breve.createInstances( breve.PolygonCone, 1 ).initWith( 3, 0.5, 0.1 )
		self.shape = breve.createInstances( breve.myCustomShape, 1 )
		self.setShape( self.shape )
		self.adjustSize()
		self.setNeighborhoodSize( self.controller.targetZone1 )


breve.Prey = Prey


class Predator( breve.Mobile ):
	def __init__( self ):
		breve.Mobile.__init__( self )
		self.shape = None
		self.ID = -1

		# can be changed
		self.pos_x = -9999
		self.pos_y = -9999
		self.vel_x = 0
		self.vel_y = 0
		
		# change with time
		self.energy = 1.0
		self.age = 0
		self.isAlive = True

		# static
		self.maxVel = 0.73
		self.maxAccel = 2
		self.visionAngle = 130
		self.maxSteering = 20
		self.geno = None
		
		# PUSH
		if self.controller.repr == 2:
			self.pushInterpreter = None
			self.pushCode = None
			self.createPush()

		self.lastScale = 1
		Predator.init( self )

	# PUSH
	def createPush(self):
		self.pushInterpreter = breve.createInstances( breve.PushInterpreter, 1 )
		self.pushInterpreter.readConfig( 'pushConfigFile.config' )
		self.pushInterpreter.addInstruction( self, 'separation' )
		self.pushInterpreter.addInstruction( self, 'alignment' )
		self.pushInterpreter.addInstruction( self, 'cohesion' )
		self.pushInterpreter.addInstruction( self, 'target' )
		self.pushInterpreter.addInstruction( self, 'currentVelocity' )
		self.pushInterpreter.addInstruction( self, 'currentEnergy' )
		self.pushInterpreter.addInstruction( self, 'randV' )
		self.pushInterpreter.setEvaluationLimit( 50 )
		self.pushInterpreter.setListLimit( 50 )
		self.pushCode = breve.createInstances( breve.PushProgram, 1 )
		self.pushCode.makeRandomCode( self.pushInterpreter, 80 )


	def initializeRandomly( self, x, y):
		self.changePos(x,y)
		
		vel_x = random.uniform(-self.maxVel, self.maxVel)
		vel_y = random.uniform(-self.maxVel, self.maxVel)
		self.changeVel(vel_x,vel_y)
		self.changeAccel(0,0)

		self.age = 0
		self.setNewColor()

		if self.controller.repr == 0:
			self.geno = [random.uniform(-5, 5) for x in range(5)]
		elif self.controller.repr == 1:
			self.geno = self.controller.create_random_tree(self.controller.initial_depth, "Predator")
		elif self.controller.reprType == 2:
			self.pushCode = breve.createInstances( breve.PushProgram, 1 )
			self.pushCode.makeRandomCode( self.pushInterpreter, 80 )
			self.pushInterpreter.pushVector( breve.vector(self.vel_x,self.vel_y,0) )

	def initializeRandomly2(self):
 		x = random.uniform(self.controller.minX, self.controller.maxX)
 		y = random.uniform(self.controller.minY, self.controller.maxY)
 		self.changePos(x,y)
 
 		vel_x = random.uniform(-self.maxVel, self.maxVel)
 		vel_y = random.uniform(-self.maxVel, self.maxVel)
 		self.changeVel(vel_x,vel_y)
 
 		self.changeAccel(0,0)
 		self.age = 0
 		self.energy = 0.5

	def initializeFromData(self, pos_x, pos_y, vel_x, vel_y, accel_x, accel_y, energy, age, isAlive, maxVel, maxAccel, visionAngle, maxSteering, geno, lastScale):
		self.changePos(pos_x, pos_y)
		self.changeVel(vel_x, vel_y)
		self.changeAccel(accel_x, accel_y)

		self.energy = energy
		self.age = age
		self.isAlive = isAlive
		self.maxVel = maxVel
		self.maxAccel = maxAccel
		self.visionAngle = visionAngle
		self.maxSteering = maxSteering
		self.lastScale = lastScale

		breve.deleteInstances( self.shape )
		self.shape = breve.createInstances( breve.myCustomShape, 1 )
		self.setShape( self.shape )
		self.shape.scale( breve.vector( lastScale , 1, lastScale ) )

		self.setNewColor()
		
		if self.controller.repr == 2:
			self.pushInterpreter.clearStacks()
			self.pushCode.setFrom(geno)
		else:
			self.geno = geno

	def setNewColor( self ):
		self.setColor( breve.vector( 1, 0, 0 ) )

	def changePos(self, x, y):
		if x < self.controller.minX-10:
			x += (self.controller.maxX+10)-(self.controller.minX-10)
		elif x > self.controller.maxX+10:
			x -= (self.controller.maxX+10)-(self.controller.minX-10)
		if y < self.controller.minY-10:
			y += (self.controller.maxY+10)-(self.controller.minY-10)
		elif y > self.controller.maxY+10:
			y -= (self.controller.maxY+10)-(self.controller.minY-10)
		
		self.pos_x = x
		self.pos_y = y
		self.move( breve.vector(x,y,0) )

	def changeAccel(self, x, y):
		n = self.norm([x, y])
		if n > self.maxAccel:
			x = x/n * self.maxAccel
			y = y/n * self.maxAccel
		self.setAcceleration( breve.vector(x, y, 0) )
			
	def changeVel(self, x, y):
		n = self.norm([x, y])
		
		v1 = self.normalizeVector(self.vel_x, self.vel_y)
		v2 = self.normalizeVector(x, y)
		a = math.degrees(self.angle(v1, v2))
		if a > self.maxSteering:
			if self.crossproduct(v1, v2) < 0:
				an = -self.maxSteering
			else:
				an = self.maxSteering

			x, y = self.rotateVector(v1, an)
			x *= n
			y *= n
		
		if n > self.maxVel:
			x = x/n * self.maxVel
			y = y/n * self.maxVel

		self.vel_x = x
		self.vel_y = y
		self.setVelocity( breve.vector(x,y,0) )

	def normalizeVector(self, x, y):
		n = self.norm([x, y])
		if n > 0:
			x = x/n
			y = y/n
		return [x, y]

	def rotateVector(self, v, alpha):
	    alpha = -math.radians(alpha)
	    return [v[0]*math.cos(alpha)+v[1]*math.sin(alpha), -v[0]*math.sin(alpha)+v[1]*math.cos(alpha)]

	def dotproduct(self, v1, v2):
		temp = 0
		for a, b in zip(v1, v2):
			temp += (a*b)
		return temp

	def crossproduct(self, v1, v2):
		return (v1[0]*v2[1]) - (v1[1]*v2[0])

	def norm(self, v):
		try:
			return math.sqrt(self.dotproduct(v, v))
		except: 
			return 999999

	def angle(self, v1, v2):
		sub = self.norm(v1) * self.norm(v2)
		if sub == 0:
			return 0
		return math.acos(self.clean_cos(self.dotproduct(v1, v2) / sub))

	def clean_cos(self, cos_angle):
		return min(1,max(cos_angle,-1))

	def addEnergy(self, num):
		self.energy += num
		if self.energy < 0:
			self.energy = 0

	def getEnergy(self):
		return self.energy

	def eat( self, prey ):
		if prey.energy > 0:
			if self.energy <= 0.90:
				self.addEnergy(0.1)
				prey.addEnergy(-0.1)
			else:
				prey.addEnergy(self.energy-1)
				self.energy = 1.0

	def dropDead(self, corpse=True):
		if corpse:
			c = breve.createInstances( breve.Corpse, 1 )
			c.move( self.getLocation() )
			c.setColor (self.getColor() )
			c.energy = self.energy
			c.lastScale = self.lastScale
			c.shape = self.shape
			c.setShape( c.shape )
			c.myPoint( breve.vector( 0, 1, 0 ), self.getVelocity())
			
			self.lastScale = 1
			self.shape = breve.createInstances( breve.myCustomShape, 1 )
			self.setShape( self.shape )
			self.adjustSize()

		self.setColor(breve.vector(0,0,0))
		#just to don't overlap the animation 
		self.changePos(-9999,9999)
		self.changeVel(0,0)
		self.changeAccel(0,0)
		self.age = 0
		self.energy = 0.5
		self.isAlive = False
		self.controller.pollPredators.append(self)
		self.controller.numDeadPredators += 1


	# GP and PUSH
	def cohesion(self):
		neighbors = self.getNeighbors()
		c_x = 0
		c_y = 0
		count = 0
		
		v1 = self.normalizeVector(self.vel_x, self.vel_y)
		for neighbor in neighbors:

			if neighbor.isA( 'Predator' ) and neighbor.isAlive:
				v2 = self.normalizeVector(neighbor.pos_x-self.pos_x, neighbor.pos_y-self.pos_y)
				a = math.degrees(self.angle(v1, v2))
			
				norm = self.norm([neighbor.pos_x-self.pos_x, neighbor.pos_y-self.pos_y])
				if a <= self.visionAngle or (0 < norm < self.controller.separationZone):

					if 0 < norm < self.controller.socialZone:
						c_x += neighbor.pos_x
						c_y += neighbor.pos_y
						count += 1

		if count > 0:
			c_x /= count
			c_y /= count

		if self.controller.repr == 2:
			self.pushInterpreter.pushVector( breve.vector(c_x, c_y, 0) )
			return
		return [c_x, c_y]

	def alignment(self):
		neighbors = self.getNeighbors()
		a_x = 0
		a_y = 0
		count = 0
		
		v1 = self.normalizeVector(self.vel_x, self.vel_y)
		for neighbor in neighbors:

			if neighbor.isA( 'Predator' ) and neighbor.isAlive:
				v2 = self.normalizeVector(neighbor.pos_x-self.pos_x, neighbor.pos_y-self.pos_y)
				a = math.degrees(self.angle(v1, v2))

				norm = self.norm([neighbor.pos_x-self.pos_x, neighbor.pos_y-self.pos_y])
				if a <= self.visionAngle or (0 < norm < self.controller.separationZone):

					if 0 < norm < self.controller.socialZone:
						a_x += neighbor.vel_x
						a_y += neighbor.vel_y
						count += 1

		if count > 0:
			a_x /= count
			a_y /= count
			

		if self.controller.repr == 2:
			self.pushInterpreter.pushVector( breve.vector(a_x, a_y, 0) )
			return
		return [a_x, a_y]

	def separation(self):
		neighbors = self.getNeighbors()
		s_x = 0
		s_y = 0
		count = 0
		
		v1 = self.normalizeVector(self.vel_x, self.vel_y)
		for neighbor in neighbors:

			if neighbor.isA( 'Prey' ) and neighbor.isAlive:
				v2 = self.normalizeVector(neighbor.pos_x-self.pos_x, neighbor.pos_y-self.pos_y)
				a = math.degrees(self.angle(v1, v2))

				norm = self.norm([neighbor.pos_x-self.pos_x, neighbor.pos_y-self.pos_y])
				if a <= self.visionAngle or (0 < norm < self.controller.separationZone):

					if 0 < norm < self.controller.separationZone:
						# separation
						v_x = self.pos_x-neighbor.pos_x
						v_y = self.pos_y-neighbor.pos_y
						v_x, v_y = self.normalizeVector(v_x, v_y)
						s_x += v_x/norm
						s_y += v_y/norm
						count += 1

		if count > 0:
			s_x /= count
			s_y /= count

		if self.controller.repr == 2:
			self.pushInterpreter.pushVector( breve.vector(s_x, s_y, 0) )
			return
		return [s_x, s_y]

	def target(self):
		neighbors = self.getNeighbors()
		t_x = 0
		t_y = 0
		dist = 99999
		count = 0
		
		v1 = self.normalizeVector(self.vel_x, self.vel_y)
		for neighbor in neighbors:

			if neighbor.isA( 'Prey' ) and neighbor.isAlive:
				v2 = self.normalizeVector(neighbor.pos_x-self.pos_x, neighbor.pos_y-self.pos_y)
				a = math.degrees(self.angle(v1, v2))

				norm = self.norm([neighbor.pos_x-self.pos_x, neighbor.pos_y-self.pos_y])
				if a <= self.visionAngle or (0 < norm < self.controller.separationZone):

					#target
					if norm < dist:
						dist = norm
						t_x = neighbor.pos_x-self.pos_x
						t_y = neighbor.pos_y-self.pos_y
		
		if self.controller.repr == 2:
			self.pushInterpreter.pushVector( breve.vector(t_x, t_y, 0) )
			return	
		return [t_x, t_y]

	def currentVelocity(self):
		if self.controller.repr == 2:
			self.pushInterpreter.pushVector( breve.vector(self.vel_x, self.vel_y, 0) )
			return
		return [self.vel_x, self.vel_y]

	def currentEnergy(self):
		if self.controller.repr == 2:
			self.pushInterpreter.pushVector( breve.vector(self.energy, self.energy, 0) )
			return
		return [self.energy, self.energy]

	def randV(self):
		rand_x = random.uniform(0, 10)
		rand_y = random.uniform(0, 10)

		if self.controller.repr == 2:
			self.pushInterpreter.pushVector( breve.vector(rand_x, rand_y, 0) )
			return
		return [rand_x, rand_y]

	# GA
	def calculateAccel(self):
		neighbors = self.getNeighbors()
		t_x = 0
		t_y = 0
		s_x = 0
		s_y = 0
		a_x = 0
		a_y = 0
		c_x = 0
		c_y = 0
		dist = 99999
		count = 0
		count2 = 0
		
		v1 = self.normalizeVector(self.vel_x, self.vel_y)
		for neighbor in neighbors:
			if not neighbor.isA( 'Corpse' ):
				v2 = self.normalizeVector(neighbor.pos_x-self.pos_x, neighbor.pos_y-self.pos_y)
				a = math.degrees(self.angle(v1, v2))
				
				norm = self.norm([neighbor.pos_x-self.pos_x, neighbor.pos_y-self.pos_y])
				if a <= self.visionAngle or (0 < norm < self.controller.separationZone):

					if neighbor.isA( 'Prey' ) and neighbor.isAlive:
						#target
						if norm < dist:
							dist = norm
							t_x = neighbor.pos_x-self.pos_x
							t_y = neighbor.pos_y-self.pos_y

						if norm < self.controller.separationZone:
							self.eat(neighbor) 

					elif neighbor.isA( 'Predator' ) and neighbor.isAlive:
						if 0 < norm < self.controller.separationZone:
							# separation
							v_x = self.pos_x-neighbor.pos_x
							v_y = self.pos_y-neighbor.pos_y
							v_x, v_y = self.normalizeVector(v_x, v_y)
							s_x += v_x/norm
							s_y += v_y/norm
							count2 += 1

						if 0 < norm < self.controller.socialZone:
							# alignment
							a_x += neighbor.vel_x
							a_y += neighbor.vel_y
							# cohesion
							c_x += neighbor.pos_x
							c_y += neighbor.pos_y
							count += 1

		if count > 0:
			a_x /= count
			a_y /= count
			
			c_x /= count
			c_y /= count

		if count2 > 0:
			s_x /= count2
			s_y /= count2
			
		rand_x = random.uniform(0, 1)
		rand_y = random.uniform(0, 1)

		c_x, c_y = self.normalizeVector(c_x, c_y)
		a_x, a_y = self.normalizeVector(a_x, a_y)
		s_x, s_y = self.normalizeVector(s_x, s_y)
		t_x, t_y = self.normalizeVector(t_x, t_y)
		rand_x, rand_y = self.normalizeVector(rand_x, rand_y)

		accel_x = self.geno[0]*c_x+self.geno[1]*a_x+self.geno[2]*s_x+self.geno[3]*t_x+self.geno[4]*rand_x
		accel_y = self.geno[0]*c_y+self.geno[1]*a_y+self.geno[2]*s_y+self.geno[3]*t_y+self.geno[4]*rand_y
		return [accel_x, accel_y]

	def fly(self):
		pos = self.getLocation()
		self.changePos(pos.x, pos.y)
		self.myPoint( breve.vector( 0, 1, 0 ), self.getVelocity())

		vel = self.getVelocity()
		vel_x = vel.x
		vel_y = vel.y
		self.changeVel(vel_x, vel_y)

		if self.controller.repr == 0:
			accel_x, accel_y = self.calculateAccel()
		else:
			if self.controller.repr == 1:
				accel_x, accel_y = self.controller.run_code(self, self.geno)
			elif self.controller.repr == 2:

				# clean the stacks
				self.pushInterpreter.clearStacks()
				self.currentVelocity()

				# run the code
				self.pushInterpreter.run( self.pushCode )
				
				# get result vector
				accel = self.pushInterpreter.getVectorStackTop()
				if ( ( ( breve.breveInternalFunctionFinder.isinf( self, accel.x ) or breve.breveInternalFunctionFinder.isnan( self, accel.x ) ) or breve.breveInternalFunctionFinder.isinf( self, accel.y ) ) or breve.breveInternalFunctionFinder.isnan( self, accel.y ) ):
					accel = breve.vector( 0.000000, 0.000000, 0.000000 )
					
				accel_x = accel.x
				accel_y = accel.y

			# eat
			neighbors = self.getNeighbors()

			v1 = self.normalizeVector(self.vel_x, self.vel_y)
			for neighbor in neighbors:

				if neighbor.isA( 'Prey' ) and neighbor.isAlive:
					v2 = self.normalizeVector(neighbor.pos_x-self.pos_x, neighbor.pos_y-self.pos_y)
					a = math.degrees(self.angle(v1, v2))

					norm = self.norm([neighbor.pos_x-self.pos_x, neighbor.pos_y-self.pos_y])
					if a <= self.visionAngle or (0 < norm < self.controller.separationZone):

						if norm < self.controller.separationZone:
							self.eat(neighbor)

		self.changeAccel(accel_x, accel_y)

		self.addEnergy(-0.01 -0.01*(1/float(1+math.exp(-((self.age-100)/12.0) ) ) ) )
		self.adjustSize()
		self.age += 1

	def cross( self, v1, v2 ):
		x = ( ( v1.y * v2.z ) - ( v1.z * v2.y ) )
		y = ( ( v1.z * v2.x ) - ( v1.x * v2.z ) )
		z = ( ( v1.x * v2.y ) - ( v1.y * v2.x ) )
		return breve.vector( x, y, z )

	def myPoint( self, theVertex, theLocation ):
		v = self.cross( theVertex, theLocation )
		a = breve.breveInternalFunctionFinder.angle( self, theVertex, theLocation )
		if ( breve.length( v ) == 0.000000 ):
			self.rotate( theVertex, 0.100000 )
			return
		self.rotate( v, a )

	def adjustSize( self ):
		newScale = ( ( (self.energy+0.5) * 10 ) + 0.500000 )
		self.shape.scale( breve.vector( ( newScale / self.lastScale ), 1, ( newScale / self.lastScale ) ) )
		self.lastScale = newScale

	def init( self ):
		# self.shape = breve.createInstances( breve.PolygonCone, 1 ).initWith( 5, 0.200000, 0.100000 )
		self.shape = breve.createInstances( breve.myCustomShape, 1 )
		self.setShape( self.shape )
		self.adjustSize()
		self.setNeighborhoodSize( self.controller.targetZone2 )


breve.Predator = Predator


class myCustomShape( breve.CustomShape ):
	def __init__( self ):
		breve.CustomShape.__init__( self )
		self.vertices = breve.objectList()
		myCustomShape.init( self )

	def init( self ):
		self.vertices[ 0 ] = breve.vector( 0.1, 0, 0 )
		self.vertices[ 1 ] = breve.vector( -0.1, 0, 0 )
		self.vertices[ 2 ] = breve.vector( 0, 0.5, 0 )

		self.addFace( [ self.vertices[ 0 ], self.vertices[ 1 ], self.vertices[ 2 ] ] )
		self.finishShape( 1.000000 )


breve.myCustomShape = myCustomShape


# auxiliar classes
class Data_mobile:
	def __init__( self, pos_x, pos_y, vel_x, vel_y, accel_x, accel_y, energy, age, isAlive, maxVel, maxAccel, visionAngle, maxSteering, geno, lastScale):
		self.pos_x = pos_x
		self.pos_y = pos_y
		self.vel_x = vel_x
		self.vel_y = vel_y
		self.accel_x = accel_x
		self.accel_y = accel_y
		
		# change with time
		self.energy = energy
		self.age = age
		self.isAlive = isAlive

		# static
		self.maxVel = maxVel
		self.maxAccel = maxAccel
		self.visionAngle = visionAngle
		self.maxSteering = maxSteering
		self.geno = geno
		
		self.lastScale = lastScale

class Data_Stationary:
	def __init__( self, pos_x, pos_y, energy, lastScale, rapid, VirtualEnergy):
		self.pos_x = pos_x
		self.pos_y = pos_y
		self.energy = energy
		self.lastScale = lastScale
		self.rapid = rapid
		self.VirtualEnergy = VirtualEnergy

class Node:
    def __init__(self, left, right, specie):
        self.left = left
        self.right = right
        self.data = None
        self.parent = None

        if specie == 'Prey':
            self.leaf = ["indiv.alignment()", "indiv.cohesion()", "indiv.separation()", "indiv.target()", "indiv.flee()",
                         "indiv.currentVelocity()", "indiv.currentEnergy()",
                         "indiv.randV()"]
        elif specie == 'Predator':
            self.leaf = ["indiv.alignment()", "indiv.cohesion()", "indiv.separation()", "indiv.target()",
                         "indiv.currentVelocity()", "indiv.currentEnergy()",
                         "indiv.randV()"]
        self.node = ["+", "-", "*", "/"]

        self.fill_data()

    def fill_data(self):
        if self.right is None:
            # leaf
            self.data = self.leaf[random.randint(0, len(self.leaf)-1)]
        else:
            # node
            self.data = self.node[random.randint(0, len(self.node)-1)]


Swarm()
