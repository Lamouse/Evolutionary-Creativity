import breve
import random
import math
import cPickle

__author__ = 'Paulo Pereira'


class Swarm( breve.Control ):
	def __init__( self ):
		breve.Control.__init__( self )

		self.showCorpse = True
		self.isToLoad = False
		self.isToSave = False
		self.isToRecord = True
		self.movie = None

		# Simulation
		self.initialNumPreys = 150
		self.initialNumPredators = 25
		self.numPreys = 150
		self.numPredators = 25
		self.numDeadPreys = 0
		self.numDeadPredators = 0

		# World
		self.minX = -200
		self.maxX = 200
		self.minY = -100
		self.maxY = 100
		self.targetZone = 50
		self.socialZone = 20

		# Feeder
		self.feederMinDistance = 25
		self.maxFoodSupply = 200
		self.minCreatedFoodSupply = 7
		self.maxCreatedFoodSupply = 15
		self.totalFoodSupply = 0

		# List
		self.pollPreys = breve.objectList()
		self.pollPredators = breve.objectList()

		# Generation
		self.maxGeneration = 5000
		self.current_generation = 0
		self.breeding_season = 50
		self.breeding_inc = 0.5
		self.max_pop_predators = 0.6
		self.prob_mutation = 0.05

		# Other thing
		Swarm.init( self )

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
				norm = ((x-feeder.pos_x)**2 + (y-feeder.pos_y)**2)**0.5
				if norm < dist:
					dist = norm
		temp_feed = breve.createInstances( breve.Feeder, 1)
		temp_feed.initializeRandomly(x,y,rapid)

	def createPreys(self, num):
		# latin hypercubes
		if num < 1:
			return

		size = (int) (math.floor(num**0.5))
		num_segments_x = (self.maxX-self.minX)/size
		num_segments_y = (self.maxY-self.minY)/size

		for i in range(size):
			for j in range(size):
				x = random.uniform((float) (i*num_segments_x+self.minX), (float) ((i+1)*num_segments_x+self.minX))
				y = random.uniform((float)(j*num_segments_y+self.minY), (float)((j+1)*num_segments_y+self.minY))
				if breve.length(self.pollPreys) < 1:
					temp_prey = breve.createInstances( breve.Prey, 1)
					temp_prey.initializeRandomly(x,y,'m')
				else:
					temp_prey = self.pollPreys[0]
					temp_prey.isAlive = True
					self.pollPreys.remove(temp_prey)
					temp_prey.initializeRandomly(x,y,'m')
				temp_prey.energy = 0.5

	def createPredators(self, num):
		# latin hypercubes
		if num < 1:
			return

		size = (int) (math.floor(num**0.5))
		num_segments_x = (self.maxX-self.minX)/size
		num_segments_y = (self.maxY-self.minY)/size

		for i in range(size):
			for j in range(size):
				x = random.uniform((float) (i*num_segments_x+self.minX), (float) ((i+1)*num_segments_x+self.minX))
				y = random.uniform((float)(j*num_segments_y+self.minY), (float)((j+1)*num_segments_y+self.minY))
				if breve.length(self.pollPredators) < 1:
					temp_predator = breve.createInstances( breve.Predator, 1)
					temp_predator.initializeRandomly(x,y,'m')
				else:
					temp_predator = self.pollPredators[0]
					temp_predator.isAlive = True
					self.pollPredators.remove(temp_predator)
					temp_predator.initializeRandomly(x,y,'m')
				temp_predator.energy = 0.5

	def revive(self, array, num):
		# immigrants
		if num < 1:
			return

		size = (int) (math.floor(num**0.5))
		num_segments_x = (self.maxX-self.minX)/size
		num_segments_y = (self.maxY-self.minY)/size

		for i in range(size):
			for j in range(size):
				x = random.uniform((float) (i*num_segments_x+self.minX), (float) ((i+1)*num_segments_x+self.minX))
				y = random.uniform((float)(j*num_segments_y+self.minY), (float)((j+1)*num_segments_y+self.minY))

				newBird = array[-1]
				array.remove(newBird)
				
				newBird.changePos(x, y)
				newBird.changeVel(0,0)
				newBird.changeAccel(0,0)

				newBird.energy = 0.5
				newBird.isAlive = True
				newBird.setNewColor()
				
	def init( self ):
		self.setBackgroundColor( breve.vector( 0, 0, 0 ) )
		self.setDisplayTextColor( breve.vector( 1, 1, 1 ) )
		self.pointCamera( breve.vector( 0, 0, 0 ), breve.vector( 0, 0, 300 ) )
		self.setIterationStep(1.0)

		if not self.isToLoad:
			self.addRandomFeederIfNecessary()
			self.createPreys(self.initialNumPreys)
			self.createPredators(self.initialNumPredators)
		else:
			self.load_data()

	def save_data(self):
		# feeders
		f =  open('data/feeder_ga.pkl', 'wb')
		for feeder in breve.allInstances( "Feeder" ):
			temp_feeder = Data_Stationary(feeder.pos_x, feeder.pos_y, feeder.energy, feeder.lastScale, feeder.rapid, feeder.VirtualEnergy)
			cPickle.dump(temp_feeder, f)
		f.close()

		# preys
		f =  open('data/prey_ga.pkl', 'wb')
		for prey in breve.allInstances( "Prey" ):
			if prey.isAlive:
				temp_accel = prey.getAcceleration()
				temp_prey = Data_mobile(prey.pos_x, prey.pos_y, prey.vel_x, prey.vel_y, temp_accel.x, temp_accel.y, prey.energy, prey.age, prey.isAlive, prey.maxVel, prey.maxAccel, prey.gener, prey.radius, prey.geno, prey.lastScale)
				cPickle.dump(temp_prey, f)
		for prey in self.pollPreys:
			temp_accel = prey.getAcceleration()
			temp_prey = Data_mobile(prey.pos_x, prey.pos_y, prey.vel_x, prey.vel_y, temp_accel.x, temp_accel.y, prey.energy, prey.age, prey.isAlive, prey.maxVel, prey.maxAccel, prey.gener, prey.radius, prey.geno, prey.lastScale)
			cPickle.dump(temp_prey, f)
		f.close()

		# prepadors
		f =  open('data/predator_ga.pkl', 'wb')
		for predator in breve.allInstances( "Predator" ):
			if predator.isAlive:
				temp_accel = predator.getAcceleration()
				temp_predator = Data_mobile(predator.pos_x, predator.pos_y, predator.vel_x, predator.vel_y, temp_accel.x, temp_accel.y, predator.energy, predator.age, predator.isAlive, predator.maxVel, predator.maxAccel, predator.gener, predator.radius, predator.geno, predator.lastScale)
				cPickle.dump(temp_predator, f)
		for predator in self.pollPredators:
			temp_accel = predator.getAcceleration()
			temp_predator = Data_mobile(predator.pos_x, predator.pos_y, predator.vel_x, predator.vel_y, temp_accel.x, temp_accel.y, predator.energy, predator.age, predator.isAlive, predator.maxVel, predator.maxAccel, predator.gener, predator.radius, predator.geno, predator.lastScale)
			cPickle.dump(temp_predator, f)
		f.close()

	def load_data(self):
		# feeders
		f =  open('data/feeder_ga.pkl', 'rb')
		while True:
			try:
				data_feeder = cPickle.load(f)
				temp_feed = breve.createInstances( breve.Feeder, 1)
				temp_feed.initializeFromData(data_feeder.pos_x, data_feeder.pos_y, data_feeder.energy, data_feeder.lastScale, data_feeder.rapid, data_feeder.VirtualEnergy)
			except EOFError:
				break
		f.close()

		# preys
		f =  open('data/prey_ga.pkl', 'rb')
		while True:
			try:
				data_prey = cPickle.load(f)
				temp_prey = breve.createInstances( breve.Prey, 1)
				temp_prey.initializeFromData(data_prey.pos_x, data_prey.pos_y, data_prey.vel_x, data_prey.vel_y, data_prey.accel_x, data_prey.accel_y, data_prey.energy, data_prey.age, data_prey.isAlive, data_prey.maxVel, data_prey.maxAccel, data_prey.gener, data_prey.radius, data_prey.geno, data_prey.lastScale)
				if not temp_prey.isAlive:
					temp_prey.dropDead(False)
			except EOFError:
				break
		f.close()

		# prepadors
		f =  open('data/predator_ga.pkl', 'rb')
		while True:
			try:
				data_predator = cPickle.load(f)
				temp_predator = breve.createInstances( breve.Predator, 1)
				temp_predator.initializeFromData(data_predator.pos_x, data_predator.pos_y, data_predator.vel_x, data_predator.vel_y, data_predator.accel_x, data_predator.accel_y, data_predator.energy, data_predator.age, data_predator.isAlive, data_predator.maxVel, data_predator.maxAccel, data_predator.gener, data_predator.radius, data_predator.geno, data_predator.lastScale)
				if not temp_predator.isAlive:
					temp_predator.dropDead(False)
			except EOFError:
				break
		f.close()

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
		for i in range(dim-1):
			candidate2 = birds[random.randint(0,leng-1)]
			if candidate2.energy > candidate.energy:
				candidate = candidate2
		return candidate

	def crossover(self, newBird1, newBird2, parent1, parent2):
		# one point crossover
		pos = random.randint(0, len(parent1.geno))
		newBird1.geno = parent1.geno[0:pos] + parent2.geno[pos:]
		newBird2.geno = parent2.geno[0:pos] + parent1.geno[pos:]

	def mutate(self, newBird):
		# uniform mutation
		for i in range(len(newBird.geno)):
			prob = random.random()
			if prob <= self.prob_mutation:
				newBird.geno[i] += random.uniform(-0.5,0.5)

	def createNewBird(self, newBird, parent1, parent2):
		p = random.uniform(0,1)
		v = random.uniform(0,1)
		newBird.changePos(p*parent1.pos_x+(1-p)*parent2.pos_x,p*parent1.pos_y+(1-p)*parent2.pos_y)
		newBird.changeVel(v*parent1.vel_x+(1-v)*parent2.vel_x,v*parent1.vel_y+(1-v)*parent2.vel_y)
		newBird.changeAccel(0,0)
		newBird.energy = 0.5
		newBird.isAlive = True
		newBird.setNewColor()
		
	def evolutionayAlgorithm(self, array):
		if breve.length(array) < 2:
			return

		newBird1 = array[0]
		newBird2 = array[1]

		# classic evolutionay algorithm
		parent1 = self.selectParent(newBird1.getType())
		if parent1 is not None:
			parent2 = self.selectNearParent(parent1, newBird1.getType())
			if parent2 is not None:
				self.crossover(newBird1, newBird2, parent1, parent2)
				self.mutate(newBird1)
				self.mutate(newBird2)
				self.createNewBird(newBird1, parent2, parent1)
				self.createNewBird(newBird2, parent1, parent2)
				
				array.remove(newBird1)
				array.remove(newBird2)

	def iterate( self ):
		if self.current_generation < self.maxGeneration:
			if self.isToRecord and not self.movie:
				self.movie = breve.createInstances( breve.Movie, 1 )
				self.movie.record( 'BOID_GA.mpeg' )

			self.updateNeighbors()

			# moviment of Prey
			self.numPreys = 0
			for prey in breve.allInstances( "Prey" ):
				if prey.isAlive:
					prey.fly()
					self.numPreys += 1

			# moviment of Predator
			self.numPredators = 0
			for predator in breve.allInstances( "Predator" ):
				if predator.isAlive:
					predator.fly()
					self.numPredators += 1

			# management of the energy from feeders
			self.totalFoodSupply = 0
			for feeder in breve.allInstances( "Feeder" ):
				if feeder.rapid:
					feeder.rapidGrow()
					self.totalFoodSupply += feeder.VirtualEnergy
				self.totalFoodSupply += feeder.energy
				if feeder.energy <= 0 and not feeder.rapid:
					breve.deleteInstances( feeder )
			self.addRandomFeederIfNecessary(rapid=True)

			# vanish corpse
			for corpse in breve.allInstances( "Corpse" ):
				corpse.changeColor()
				if sum(corpse.getColor()) <= 0:	
					breve.deleteInstances( corpse.shape )
					breve.deleteInstances( corpse )


			self.current_generation += 1
			# breeding
			if self.current_generation % self.breeding_season == 0:
				# preys
				tam_prey = int(math.ceil((self.breeding_inc*self.numPreys)/2))
				if breve.length(self.pollPreys) < tam_prey*2:
					new_prey = tam_prey - breve.length(self.pollPreys)
					breve.createInstances( breve.Prey, new_prey).dropDead(False)
				for i in range(tam_prey):
					self.evolutionayAlgorithm(self.pollPreys)

				# predators
				predator_max = self.numPreys*self.max_pop_predators
				predator_breed = self.breeding_inc*self.numPredators
				tam_predator = int(math.ceil(min(predator_max, predator_breed)/2))
				if breve.length(self.pollPredators) < tam_predator*2:
					new_preds = tam_predator - breve.length(self.pollPredators)
					breve.createInstances( breve.Predator, new_preds).dropDead(False)
				for i in range(tam_predator):
					self.evolutionayAlgorithm(self.pollPredators)
			# immigrants
			else:
				if self.numPreys < 0.2*self.initialNumPreys:
					self.revive(self.pollPreys, math.floor(0.15*self.initialNumPreys))
					self.createPreys(math.floor(0.05*self.initialNumPreys))
				if self.numPredators < 0.2*self.initialNumPredators:
					self.revive(self.pollPredators, math.floor(0.15*self.initialNumPredators))
					self.createPredators(math.floor(0.05*self.initialNumPredators))
			
			# checkpoint
			if self.isToSave and self.current_generation % (self.breeding_season*25) == 0:
				self.save_data()


			# to display on screen
			self.setDisplayText("Generation: "+str((int) (math.ceil(self.current_generation/self.breeding_season))), xLoc = -0.950000, yLoc = -0.550000, messageNumber = 5, theColor = breve.vector( 1, 1, 1 ))
			self.setDisplayText("Preys Alive: "+str(self.numPreys), xLoc = -0.950000, yLoc = -0.650000, messageNumber = 4, theColor = breve.vector( 1, 1, 1 ))
			self.setDisplayText("Predators Alive: "+str(self.numPredators), xLoc = -0.950000, yLoc = -0.750000, messageNumber = 3, theColor = breve.vector( 1, 1, 1 ))
			self.setDisplayText("Dead Preys: "+str(self.numDeadPreys), xLoc = -0.950000, yLoc = -0.850000, messageNumber = 2, theColor = breve.vector( 1, 1, 1 ))
			self.setDisplayText("Dead Predators: "+str(self.numDeadPredators), xLoc = -0.950000, yLoc = -0.950000, messageNumber = 1, theColor = breve.vector( 1, 1, 1 ))

			# needed to move the agents with velocity and acceleration
			# also needed to detect collisions
			# print str(self.numBirdsBirth)
			breve.Control.iterate( self )

		elif self.isToRecord and self.movie:
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
		self.gener = 'm'
		self.radius = 2
		self.geno = None
		#self.geno = [0.005, 0.01, 1, 0.005, 1]

		self.lastScale = 1
		Prey.init( self )


	def initializeRandomly( self, x, y, gener):
		self.changePos(x,y)
		# vel_x = random.uniform(-self.maxVel, self.maxVel)
		# vel_y = random.uniform(-self.maxVel, self.maxVel)
		self.changeVel(0,0)
		self.changeAccel(0,0)

		self.gener = gener
		self.setNewColor()

		self.geno = [random.uniform(-5, 5) for x in range(6)]

	def initializeFromData(self, pos_x, pos_y, vel_x, vel_y, accel_x, accel_y, energy, age, isAlive, maxVel, maxAccel, gener, radius, geno, lastScale):
		self.maxVel = maxVel
		self.maxAccel = maxAccel

		self.changePos(pos_x, pos_y)
		self.changeVel(vel_x, vel_y)
		self.changeAccel(accel_x, accel_y)

		# self.energy = 1.5
		# self.lastScale = lastScale
		self.age = 0
		self.isAlive = isAlive
		self.gener = gener
		self.radius = radius
		
		# self.energy = energy
		# self.adjustSize()
		self.setNewColor()
		
		self.geno = geno

	def setNewColor( self ):
		if self.gener == 'f':
			self.setColor( breve.vector( 0.5, 1, 0.5) )
		else:
			self.setColor( breve.vector( 0, 1, 0 ) )

	def changePos(self, x, y):
		self.pos_x = x
		self.pos_y = y
		self.move( breve.vector(x,y,0) )

	def changeAccel(self, x, y):
		norm = (x**2 + y**2)**0.5
		if  norm > self.maxAccel:
			x = x/norm * self.maxAccel
			y = y/norm * self.maxAccel
		self.setAcceleration( breve.vector(x, y, 0) )
			
	def changeVel(self, x, y):
		norm = (x**2 + y**2)**0.5
		if  norm > self.maxVel:
			x = x/norm * self.maxVel
			y = y/norm * self.maxVel
		self.vel_x = x
		self.vel_y = y
		self.setVelocity( breve.vector(x,y,0) )

	def normalizeVector(self, x, y):
		norm = (x**2 + y**2)**0.5
		if norm > 0:
			x = x/norm * self.maxAccel
			y = y/norm * self.maxAccel
		return [x, y]

	def addEnergy(self, num):
		self.energy += num
		if self.energy < 0:
			self.energy = 0

	def getEnergy(self):
		return self.energy

	def eat( self, feeder ):
		if self.energy <= 0.90 and feeder.energy > 0:
			self.addEnergy(0.1)
			feeder.addEnergy(-0.1)
	
	def dropDead(self, corpse=True):
		if corpse:
			c = breve.createInstances( breve.Corpse, 1 )
			c.move( self.getLocation() )
			c.setColor (self.getColor() )
			c.energy = self.energy
			#c.lastScale = self.lastScale
			# c.adjustSize()
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
		self.energy = 1
		self.isAlive = False
		self.controller.pollPreys.append(self)
		self.controller.numDeadPreys += 1

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
		dist2 = 99999
		count = 0
		for neighbor in neighbors:
			if neighbor.isA( 'Feeder' ):
				norm = ((self.pos_x-neighbor.pos_x)**2 + (self.pos_y-neighbor.pos_y)**2)**0.5
				#target
				if norm < dist:
					#dist = norm*(1-neighbor.energy)
					dist = norm
					t_x = neighbor.pos_x-self.pos_x
					t_y = neighbor.pos_y-self.pos_y

				if norm <= max(neighbor.lastScale,3):
					self.eat(neighbor) 

			elif neighbor.isA( 'Prey' ) and neighbor.isAlive:
				norm = ((self.pos_x-neighbor.pos_x)**2 + (self.pos_y-neighbor.pos_y)**2)**0.5
				if 0 < norm < self.radius:
					# separation
					v_x = (self.pos_x - neighbor.pos_x) / norm**2
					v_y = (self.pos_y - neighbor.pos_y) / norm**2
					s_x += v_x*self.lastScale**2
					s_y += v_y*self.lastScale**2

				if norm < self.controller.socialZone:
					# alignment
					a_x += neighbor.vel_x
					a_y += neighbor.vel_y
					# cohesion
					c_x += neighbor.pos_x
					c_y += neighbor.pos_y
					count += 1

			elif neighbor.isA( 'Predator' ) and neighbor.isAlive:
				norm = ((self.pos_x-neighbor.pos_x)**2 + (self.pos_y-neighbor.pos_y)**2)**0.5
				#flee
				if norm < dist2:
					dist2 = norm
					f_x = (self.pos_x - neighbor.pos_x)
					f_y = (self.pos_y - neighbor.pos_y)

		if count > 0:
			a_x /= count
			a_y /= count
			a_x -= self.vel_x
			a_y -= self.vel_y

			c_x /= count
			c_y /= count
			c_x -= self.pos_x
			c_y -= self.pos_y

		rand_x = random.uniform(0, 1)
		rand_y = random.uniform(0, 1)

		'''if dist == 99999:
			feeders = breve.allInstances( "Feeder" )
			for neighbor in feeders:
				norm = ((self.pos_x-neighbor.pos_x)**2 + (self.pos_y-neighbor.pos_y)**2)**0.5
				if norm < dist:
					dist = norm
					t_x = neighbor.pos_x-self.pos_x
					t_y = neighbor.pos_y-self.pos_y'''

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

		accel_x, accel_y = self.calculateAccel()
		self.changeAccel(accel_x, accel_y)

		# self.addEnergy(-0.01 - (1/(1+math.exp(self.age/150)))*0.005 )
		self.addEnergy(-0.01)
		self.adjustSize()
		self.age += 1

		#if self.energy < 0 or self.age > 300:
		if self.energy <= 0:
			self.dropDead(self.controller.showCorpse)

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
		self.setNeighborhoodSize( self.controller.targetZone )


breve.Prey = Prey


class Predator( breve.Mobile ):
	def __init__( self ):
		breve.Mobile.__init__( self )
		self.shape = None
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
		self.maxVel = 0.7
		self.maxAccel = 2
		self.gener = 'm'
		self.radius = 2
		self.geno = None
		
		self.lastScale = 1
		Predator.init( self )

	def initializeRandomly( self, x, y, gener):
		self.changePos(x,y)
		# vel_x = random.uniform(-self.maxVel, self.maxVel)
		# vel_y = random.uniform(-self.maxVel, self.maxVel)
		self.changeVel(0,0)
		self.changeAccel(0,0)
		
		self.gener = gener
		self.setNewColor()

		self.geno = [random.uniform(-5, 5) for x in range(5)]

	def initializeFromData(self, pos_x, pos_y, vel_x, vel_y, accel_x, accel_y, energy, age, isAlive, maxVel, maxAccel, gener, radius, geno, lastScale):
		self.maxVel = maxVel
		self.maxAccel = maxAccel

		self.changePos(pos_x, pos_y)
		self.changeVel(vel_x, vel_y)
		self.changeAccel(accel_x, accel_y)

		# self.energy = 1.5
		# self.lastScale = lastScale
		self.age = 0
		self.isAlive = isAlive
		self.gener = gener
		self.radius = radius
		
		# self.energy = energy
		# self.adjustSize()
		self.setNewColor()
		
		self.geno = geno

	def setNewColor( self ):
		if self.gener == 'f':
			self.setColor( breve.vector( 1, 0.5, 0.5 ) )
		else:
			self.setColor( breve.vector( 1, 0, 0 ) )

	def changePos(self, x, y):
		self.pos_x = x
		self.pos_y = y
		self.move( breve.vector(x,y,0) )

	def changeAccel(self, x, y):
		norm = (x**2 + y**2)**0.5
		if  norm > self.maxAccel:
			x = x/norm * self.maxAccel
			y = y/norm * self.maxAccel
		self.setAcceleration( breve.vector(x, y, 0) )

	def changeVel(self, x, y):
		norm = (x**2 + y**2)**0.5
		if  norm > self.maxVel:
			x = x/norm * self.maxVel
			y = y/norm * self.maxVel
		self.vel_x = x
		self.vel_y = y
		self.setVelocity( breve.vector(x,y,0) )

	def normalizeVector(self, x, y):
		norm = (x**2 + y**2)**0.5
		if norm > 0:
			x = x/norm * self.maxAccel
			y = y/norm * self.maxAccel
		return [x, y]

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
			#c.lastScale = self.lastScale
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
		self.energy = 1
		self.isAlive = False
		self.controller.pollPredators.append(self)
		self.controller.numDeadPredators += 1

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
		for neighbor in neighbors:
			if neighbor.isA( 'Prey' ) and neighbor.isAlive:
				norm = ((self.pos_x-neighbor.pos_x)**2 + (self.pos_y-neighbor.pos_y)**2)**0.5
				#target
				if norm < dist:
					dist = norm
					t_x = neighbor.pos_x-self.pos_x
					t_y = neighbor.pos_y-self.pos_y

				if norm < self.radius:
					self.eat(neighbor) 

			elif neighbor.isA( 'Predator' ) and neighbor.isAlive:
				norm = ((self.pos_x-neighbor.pos_x)**2 + (self.pos_y-neighbor.pos_y)**2)**0.5
				if 0 < norm < self.radius:
					# separation
					v_x = (self.pos_x - neighbor.pos_x) / norm**2
					v_y = (self.pos_y - neighbor.pos_y) / norm**2
					s_x += v_x*self.lastScale**2
					s_y += v_y*self.lastScale**2

				if norm < self.controller.socialZone:
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
			a_x -= self.vel_x
			a_y -= self.vel_y

			c_x /= count
			c_y /= count
			c_x -= self.pos_x
			c_y -= self.pos_y

		rand_x = random.uniform(0, 1)
		rand_y = random.uniform(0, 1)

		'''if dist == 99999:
			feeders = breve.allInstances( "Prey" )
			for neighbor in feeders:
				norm = ((self.pos_x-neighbor.pos_x)**2 + (self.pos_y-neighbor.pos_y)**2)**0.5
				if norm < dist:
					dist = norm
					t_x = neighbor.pos_x-self.pos_x
					t_y = neighbor.pos_y-self.pos_y'''

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

		accel_x, accel_y = self.calculateAccel()
		self.changeAccel(accel_x, accel_y)

		#self.addEnergy(-0.01 - (1/(1+math.exp(self.age/150)))*0.005 )
		self.addEnergy(-0.01)
		self.adjustSize()
		self.age += 1

		#if self.energy < 0.5 or self.age > 300:
		if self.energy <= 0:
			self.dropDead(self.controller.showCorpse)

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
		self.setNeighborhoodSize( self.controller.targetZone*1.5 )


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
	def __init__( self, pos_x, pos_y, vel_x, vel_y, accel_x, accel_y, energy, age, isAlive, maxVel, maxAccel, gener, radius, geno, lastScale):
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
		self.gener = gener
		self.radius = radius
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


Swarm()
