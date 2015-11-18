import breve
import random
import math

__author__ = 'Paulo Pereira'


class Swarm( breve.Control ):
	def __init__( self ):
		breve.Control.__init__( self )
		self.initialNumBirds = 150
		self.initialNumPred = 25
		self.numBirds = 150
		self.numPred = 25
		self.num_dead_birds = 0
		self.num_dead_predators = 0

		# World
		self.minX = -200
		self.maxX = 200
		self.minY = -100
		self.maxY = 100
		self.neighborRadius = 50
		self.neighborRadiusMinor = 20

		# Feeder
		self.feederMinDistance = 25
		self.maxFoodSupply = 200
		self.minCreatedFoodSupply = 7
		self.maxCreatedFoodSupply = 15
		self.totalFoodSupply = 0

		# List
		self.current_generation = 0
		self.breeding_season = 50
		self.breeding_inc = 0.4
		self.max_pop_predadors = 0.6
		self.prob_mutation = 0.05
		self.pollBirds = breve.objectList()
		self.pollPredators = breve.objectList()

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

	def createBirds(self, num):
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
				if breve.length(self.pollBirds) < 1:
					temp_bird = breve.createInstances( breve.Bird, 1)
					temp_bird.initializeRandomly(x,y,'m')
				else:
					temp_bird = self.pollBirds[0]
					self.pollBirds.remove(temp_bird)
					temp_bird.initializeRandomly(x,y,'m')

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
					self.pollPredators.remove(temp_predator)
					temp_predator.initializeRandomly(x,y,'m')

	def revive(self, array, num):
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
				newBird.energy = 1.0
				newBird.isAlive = True
				newBird.setNewColor()

	def init( self ):
		self.setBackgroundColor( breve.vector( 0, 0, 0 ) )
		self.setDisplayTextColor( breve.vector( 1, 1, 1 ) )
		self.pointCamera( breve.vector( 0, 0, 0 ), breve.vector( 0, 0, 300 ) )
		self.setIterationStep(1.0)

		self.addRandomFeederIfNecessary()
		self.createBirds(self.numBirds)
		self.createPredators(self.numPred)

	def addTotalFoodSupply(self, num):
		self.totalFoodSupply += num;

	def addRandomFeederIfNecessary( self, rapid=False):
		while (self.maxFoodSupply-self.totalFoodSupply) >= self.maxCreatedFoodSupply:
			self.createFeeder(1, rapid)

	# funcions used by breeding
	def selectNearParent( self, parent1, specie):
		#neighbour = parent1.getNeighbors()
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

	def crossover(self, newBird, parent1, parent2):
		# c1 = parent1.pushCode
		# c2 = parent2.pushCode
		# parent1.pushInterpreter.copyCodeStackTop( c1 )
		# parent2.pushInterpreter.copyCodeStackTop( c2 )
		newBird.pushInterpreter.clearStacks()
		newBird.pushCode.crossover( parent1.pushCode, parent2.pushCode, newBird.pushInterpreter )

	def mutate(self, newBird):
		prob = random.randint( 0,15 )
		newBird.pushCode.mutate( newBird.pushInterpreter, prob )

	def createNewBird(self, newBird, parent1, parent2):
		p = random.uniform(0,1)
		v = random.uniform(0,1)
		newBird.changePos(p*parent1.pos_x+(1-p)*parent2.pos_x,p*parent1.pos_y+(1-p)*parent2.pos_y)
		newBird.changeVel(v*parent1.vel_x+(1-v)*parent2.vel_x,v*parent1.vel_y+(1-v)*parent2.vel_y)
		newBird.energy = 1.0
		newBird.isAlive = True
		newBird.setNewColor()
		# newBird.pushInterpreter.pushVector( breve.vector(newBird.vel_x, newBird.vel_y, 0) )
		
	def evolutionayAlgorithm(self, array):
		newBird = array[0]
		array.remove(newBird)
		created = False
		# classic evolutionay algorithm
		parent1 = self.selectParent(newBird.getType())
		if parent1 is not None:
			parent2 = self.selectNearParent(parent1, newBird.getType())
			if parent2 is not None:
				self.crossover(newBird, parent1, parent2)
				self.mutate(newBird)
				self.createNewBird(newBird, parent1, parent2)
				created = True

		if not created:
			array.append(newBird)

	def iterate( self ):
		self.updateNeighbors()

		self.numBirds = 0
		for bird in breve.allInstances( "Bird" ):
			if bird.isAlive:
				bird.fly()
				self.numBirds += 1

		self.numPred = 0
		for predator in breve.allInstances( "Predator" ):
			if predator.isAlive:
				predator.fly()
				self.numPred += 1

		self.totalFoodSupply = 0
		for feeder in breve.allInstances( "Feeder" ):
			if feeder.rapid:
				feeder.rapidGrow()
				self.totalFoodSupply += feeder.VirtualEnergy
			self.totalFoodSupply += feeder.energy
			if feeder.energy <= 0 and not feeder.rapid:
				breve.deleteInstances( feeder )
		self.addRandomFeederIfNecessary(rapid=True)

		for corpse in breve.allInstances( "Corpse" ):
			corpse.changeColor()
			if sum(corpse.getColor()) <= 0:	
				breve.deleteInstances( corpse.shape )
				breve.deleteInstances( corpse )

		self.current_generation += 1
		if self.current_generation % self.breeding_season == 0:
			if breve.length(self.pollBirds) < self.breeding_inc*self.numBirds:
				new_birds = int(math.ceil(self.breeding_inc*self.numBirds)) - breve.length(self.pollBirds)
				breve.createInstances( breve.Bird, new_birds).dropDead(False)

			if breve.length(self.pollPredators) < self.breeding_inc*self.numPred:
				new_preds = int(math.ceil(self.breeding_inc*self.numPred)) - breve.length(self.pollPredators)
				breve.createInstances( breve.Predator, new_preds).dropDead(False)

			for i in range(int(math.ceil(self.breeding_inc*self.numBirds))/2):
				self.evolutionayAlgorithm(self.pollBirds)
			if self.numPred < self.numBirds*self.max_pop_predadors:
				for i in range(int(min(math.ceil(self.breeding_inc*self.numPred), self.numBirds*self.max_pop_predadors))/2):
					self.evolutionayAlgorithm(self.pollPredators)

		if self.numBirds < 0.2*self.initialNumBirds:
			self.revive(self.pollBirds, math.ceil(0.1*self.initialNumBirds))	
		if self.numPred < 0.2*self.initialNumPred:
			self.revive(self.pollPredators, math.ceil(0.1*self.initialNumPred))

		self.setDisplayText("Birds Alive: "+str(self.numBirds), xLoc = -0.950000, yLoc = -0.650000, messageNumber = 2, theColor = breve.vector( 1, 1, 1 ))
		self.setDisplayText("Predators Alive: "+str(self.numPred), xLoc = -0.950000, yLoc = -0.750000, messageNumber = 3, theColor = breve.vector( 1, 1, 1 ))
		self.setDisplayText("Dead Birds: "+str(self.num_dead_birds), xLoc = -0.950000, yLoc = -0.850000, messageNumber = 0, theColor = breve.vector( 1, 1, 1 ))
		self.setDisplayText("Dead Predators: "+str(self.num_dead_predators), xLoc = -0.950000, yLoc = -0.950000, messageNumber = 1, theColor = breve.vector( 1, 1, 1 ))

		# needed to move the agents with velocity and acceleration
		# also needed to detect collisions
		# print str(self.numBirdsBirth)

		breve.Control.iterate( self )


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
		self.shape = breve.createInstances( breve.PolygonCone, 1 ).initWith( 5, 0.200000, 0.100000 )
		self.setShape( self.shape )
	
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
		colorDec = 0.03
		colorVector = breve.vector(max(colorVector[0]-colorDec,0),max(colorVector[1]-colorDec,0),max(colorVector[2]-colorDec,0),)
		self.setColor(colorVector)

breve.Corpse = Corpse

class Bird( breve.Mobile ):
	def __init__( self ):
		breve.Mobile.__init__( self )
		self.shape = None
		# can be changed
		self.pos_x = 0
		self.pos_y = 0
		self.vel_x = 0
		self.vel_y = 0

		# change with time
		self.energy = 1.5
		self.age = 0
		self.isAlive = True

		# static
		self.maxVel = 0.5
		self.maxAccel = 2
		self.gener = 'm'
		self.radius = 5

		self.pushInterpreter = None
		self.pushCode = None
		self.createPush()
		
		self.lastScale = 1
		Bird.init( self )

	def createPush(self):
		self.pushInterpreter = breve.createInstances( breve.PushInterpreter, 1 )
		self.pushInterpreter.readConfig( 'pushConfigFile.config' )
		self.pushInterpreter.addInstruction( self, 'separation' )
		self.pushInterpreter.addInstruction( self, 'alignment' )
		self.pushInterpreter.addInstruction( self, 'cohension' )
		self.pushInterpreter.addInstruction( self, 'target' )
		self.pushInterpreter.addInstruction( self, 'mostEnergizedNeighbor' )
		self.pushInterpreter.addInstruction( self, 'currentVelocity' )
		self.pushInterpreter.addInstruction( self, 'centerOfWorld' )
		self.pushInterpreter.addInstruction( self, 'randV' )
		self.pushInterpreter.addInstruction( self, 'flee' )
		self.pushInterpreter.setEvaluationLimit( 75 )
		self.pushInterpreter.setListLimit( 75 )
		self.pushCode = breve.createInstances( breve.PushProgram, 1 )
		self.pushCode.makeRandomCode( self.pushInterpreter, 100 )

	def initializeRandomly( self, x, y, gener):
		self.changePos(x,y)
		vel_x = random.uniform(-self.maxVel, self.maxVel)
		vel_y = random.uniform(-self.maxVel, self.maxVel)
		self.changeVel(vel_x, vel_y)

		self.gener = gener
		self.setNewColor()

		self.pushInterpreter.pushVector( breve.vector(self.vel_x,self.vel_y,0) )

	def setNewColor( self ):
		if self.gener == 'f':
			self.setColor( breve.vector( 0.5, 0.5, 1) )
		else:
			self.setColor( breve.vector( 0, 0, 1 ) )

	# Functions used by Push
	def randV( self ):
		rand_x = random.uniform(0, 1)
		rand_y = random.uniform(0, 1)
		self.pushInterpreter.pushVector( breve.vector(rand_x, rand_y, 0) )

	def mostEnergizedNeighbor(self):
		neighbors = self.getNeighbors()
		me_x = 0
		me_y = 0
		energy = 0
		for neighbor in neighbors:
			if neighbor.isA( 'Bird' ) and neighbor.isAlive:
				if neighbor.energy > energy:
					me_x = neighbor.pos_x-self.pos_x
					me_y = neighbor.pos_y-self.pos_y
					energy = neighbor.energy
		self.pushInterpreter.pushVector( breve.vector(me_x,me_y,0) )

	def flee(self):
		neighbors = self.getNeighbors()
		s_x = 0
		s_y = 0
		for neighbor in neighbors:
			if neighbor.isA( 'Predator' ) and neighbor.isAlive:
				d = (self.pos_x-neighbor.pos_x)**2+(self.pos_y-neighbor.pos_y)**2
				if 0 <= d < 5:
					v_x = (self.pos_x - neighbor.pos_x) / d**2
					v_y = (self.pos_y - neighbor.pos_y) / d**2
					s_x += v_x*self.lastScale**2
					s_y += v_y*self.lastScale**2
		self.pushInterpreter.pushVector( breve.vector(s_x,s_y,0) )

	def separation(self):
		neighbors = self.getNeighbors()
		s_x = 0
		s_y = 0
		for neighbor in neighbors:
			if neighbor.isA( 'Bird' ) and neighbor.isAlive:
				d = (self.pos_x-neighbor.pos_x)**2+(self.pos_y-neighbor.pos_y)**2
				if 0 < d < self.radius:
					v_x = (self.pos_x - neighbor.pos_x) / d**2
					v_y = (self.pos_y - neighbor.pos_y) / d**2
					s_x += v_x*self.lastScale**2
					s_y += v_y*self.lastScale**2
		self.pushInterpreter.pushVector( breve.vector(s_x,s_y,0) )

	def alignment(self):
		neighbors = self.getNeighbors()
		a_x = 0
		a_y = 0
		count = 0

		for neighbor in neighbors:
			if neighbor.isA( 'Bird' ) and neighbor.isAlive:
				norm = (self.pos_x-neighbor.pos_x)**2+(self.pos_y-neighbor.pos_y)**2
				if norm < self.controller.neighborRadiusMinor:
					a_x += neighbor.vel_x
					a_y += neighbor.vel_y
					count += 1
		
		if count > 0:
			a_x /= count
			a_y /= count
			a_x -= self.vel_x
			a_y -= self.vel_y
		self.pushInterpreter.pushVector( breve.vector(a_x,a_y,0) )

	def cohension(self):
		neighbors = self.getNeighbors()
		c_x = 0
		c_y = 0
		count = 0

		for neighbor in neighbors:
			if neighbor.isA( 'Bird' ) and neighbor.isAlive:
				norm = (self.pos_x-neighbor.pos_x)**2+(self.pos_y-neighbor.pos_y)**2
				if norm < self.controller.neighborRadiusMinor:
					c_x += neighbor.pos_x
					c_y += neighbor.pos_y
					count += 1
			
		if count > 0:
			c_x /= count
			c_y /= count
			c_x -= self.pos_x
			c_y -= self.pos_y
		self.pushInterpreter.pushVector( breve.vector(c_x,c_y,0) )

	def target(self):
		#neighbors = breve.allInstances( "Feeder" )
		neighbors = self.getNeighbors()
		t_x = 0
		t_y = 0
		dist = 99999
		count = 0
		for neighbor in neighbors:
			if neighbor.isA( 'Feeder' ):
				norm = ((self.pos_x-neighbor.pos_x)**2 + (self.pos_y-neighbor.pos_y)**2)**0.5

				if norm < dist:
					dist = norm
					t_x = neighbor.pos_x-self.pos_x
					t_y = neighbor.pos_y-self.pos_y

		'''if dist == 99999:
			feeders = breve.allInstances( "Feeder" )
			for neighbor in feeders:
				norm = ((self.pos_x-neighbor.pos_x)**2 + (self.pos_y-neighbor.pos_y)**2)**0.5
				if norm < dist:
					dist = norm
					t_x = neighbor.pos_x-self.pos_x
					t_y = neighbor.pos_y-self.pos_y'''

		self.pushInterpreter.pushVector( breve.vector(9*t_x,9*t_y,0) )

	def currentVelocity(self):
		self.pushInterpreter.pushVector( breve.vector(self.vel_x,self.vel_y,0) )

	def centerOfWorld( self ):
		self.pushInterpreter.pushVector( breve.vector(-self.pos_x,-self.pos_y,0) )

	# end of the functions used by Push
	def changePos(self, x, y):
		self.pos_x = x
		self.pos_y = y
		self.move( breve.vector(x,y,0) )

	def changeAccel(self, x, y):
		norm = (x**2 + y**2)**0.5
		if  norm > self.maxAccel:
			x = x/norm * self.maxAccel
			y = y/norm * self.maxAccel
		self.setAcceleration( breve.vector(x,y,0) )

	def changeVel(self, x, y):
		norm = (x**2 + y**2)**0.5
		if  norm > self.maxVel:
			x = x/norm * self.maxVel
			y = y/norm * self.maxVel
		self.vel_x = x
		self.vel_y = y
		self.setVelocity( breve.vector(x,y,0) )

	def addEnergy(self, num):
		self.energy += num
		if self.energy < 0:
			self.energy = 0

	def getEnergy(self):
		return self.energy

	def eat( self, feeder ):
		if self.energy < 1.4 and feeder.energy > 0:
			self.addEnergy(0.05)
			feeder.addEnergy(-0.05)
	
	def dropDead(self, corpse=True):
		if corpse:
			c = breve.createInstances( breve.Corpse, 1 )
			c.move( self.getLocation() )
			c.setColor (self.getColor() )
			c.energy = self.energy
			#c.lastScale = self.lastScale
			c.adjustSize()
			c.myPoint( breve.vector( 0, 1, 0 ), self.getVelocity())

		self.setColor(breve.vector(0,0,0))
		#just to don't overlap the animation 
		self.changePos(-500,500)
		# self.pushInterpreter.clearStacks()
		self.age = 0
		self.energy = 1
		self.isAlive = False
		self.controller.pollBirds.append(self)
		self.controller.num_dead_birds += 1

	def fly(self):
		pos = self.getLocation()
		self.changePos(pos.x, pos.y)
		self.myPoint( breve.vector( 0, 1, 0 ), self.getVelocity())

		vel = self.getVelocity()
		vel_x = vel.x
		vel_y = vel.y
		self.changeVel(vel_x, vel_y)

		self.pushInterpreter.run( self.pushCode )
		accel = self.pushInterpreter.getVectorStackTop()
		if ( ( ( ( ( breve.breveInternalFunctionFinder.isinf( self, accel.x ) or breve.breveInternalFunctionFinder.isnan( self, accel.x ) ) or breve.breveInternalFunctionFinder.isinf( self, accel.y ) ) or breve.breveInternalFunctionFinder.isnan( self, accel.y ) ) or breve.breveInternalFunctionFinder.isinf( self, accel.z ) ) or breve.breveInternalFunctionFinder.isnan( self, accel.z ) ):
				accel = breve.vector( 0.000000, 0.000000, 0.000000 )
		self.changeAccel(accel.x, accel.y)
		
		# eat
		neighbors = self.getNeighbors()
		for neighbor in neighbors:
			if neighbor.isA( 'Feeder' ):
				norm = ((self.pos_x-neighbor.pos_x)**2 + (self.pos_y-neighbor.pos_y)**2)**0.5
				if norm <= max(neighbor.lastScale,3):
					self.eat(neighbor) 

		self.addEnergy(-0.01)
		self.adjustSize()
		self.age += 1
		#if self.energy < 0.5 or self.age > 300:
		if self.energy < 0.5:
			self.dropDead()

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
		newScale = ( ( self.energy * 10 ) + 0.500000 )
		self.shape.scale( breve.vector( ( newScale / self.lastScale ), 1, ( newScale / self.lastScale ) ) )
		self.lastScale = newScale

	def init( self ):
		# self.shape = breve.createInstances( breve.PolygonCone, 1 ).initWith( 5, 0.200000, 0.100000 )
		self.shape = breve.createInstances( breve.myCustomShape, 1 )
		self.setShape( self.shape )
		self.adjustSize()
		self.setNeighborhoodSize( self.controller.neighborRadius )

breve.Bird = Bird

class Predator( breve.Mobile ):
	def __init__( self ):
		breve.Mobile.__init__( self )
		self.shape = None
		# can be changed
		self.pos_x = 0
		self.pos_y = 0
		self.vel_x = 0
		self.vel_y = 0
		
		# change with time
		self.energy = 1.5
		self.age = 0
		self.isAlive = True

		# static
		self.maxVel = 0.7
		self.maxAccel = 2
		self.gener = 'm'
		self.radius = 2

		self.pushInterpreter = None
		self.pushCode = None
		self.createPush()
		
		self.lastScale = 1
		Predator.init( self )

	def createPush(self):
		self.pushInterpreter = breve.createInstances( breve.PushInterpreter, 1 )
		self.pushInterpreter.readConfig( 'pushConfigFile.config' )
		self.pushInterpreter.addInstruction( self, 'separation' )
		self.pushInterpreter.addInstruction( self, 'alignment' )
		self.pushInterpreter.addInstruction( self, 'cohension' )
		self.pushInterpreter.addInstruction( self, 'target' )
		self.pushInterpreter.addInstruction( self, 'mostEnergizedNeighbor' )
		self.pushInterpreter.addInstruction( self, 'currentVelocity' )
		self.pushInterpreter.addInstruction( self, 'centerOfWorld' )
		self.pushInterpreter.addInstruction( self, 'randV' )
		self.pushInterpreter.setEvaluationLimit( 75 )
		self.pushInterpreter.setListLimit( 75 )
		self.pushCode = breve.createInstances( breve.PushProgram, 1 )
		self.pushCode.makeRandomCode( self.pushInterpreter, 100 )

	def initializeRandomly( self, x, y, gener):
		self.changePos(x,y)
		vel_x = random.uniform(-self.maxVel, self.maxVel)
		vel_y = random.uniform(-self.maxVel, self.maxVel)
		self.changeVel(vel_x, vel_y)

		self.gener = gener
		self.setNewColor()

		self.pushInterpreter.pushVector( breve.vector(self.vel_x,self.vel_y,0) )

	def setNewColor( self ):
		if self.gener == 'f':
			self.setColor( breve.vector( 1, 0.5, 0.5 ) )
		else:
			self.setColor( breve.vector( 1, 0, 0 ) )

	# Functions used by Push
	def randV( self ):
		rand_x = random.uniform(0, 1)
		rand_y = random.uniform(0, 1)
		self.pushInterpreter.pushVector( breve.vector(rand_x, rand_y, 0) )

	def mostEnergizedNeighbor(self):
		neighbors = self.getNeighbors()
		me_x = 0
		me_y = 0
		energy = 0
		for neighbor in neighbors:
			if neighbor.isA( 'Predator' ) and neighbor.isAlive:
				if neighbor.energy > energy:
					me_x = neighbor.pos_x-self.pos_x
					me_y = neighbor.pos_y-self.pos_y
					energy = neighbor.energy
		self.pushInterpreter.pushVector( breve.vector(me_x,me_y,0) )

	def separation(self):
		neighbors = self.getNeighbors()
		s_x = 0
		s_y = 0
		for neighbor in neighbors:
			if neighbor.isA( 'Predator' ) and neighbor.isAlive:
				d = (self.pos_x-neighbor.pos_x)**2+(self.pos_y-neighbor.pos_y)**2
				if 0 < d < self.radius:
					v_x = (self.pos_x - neighbor.pos_x) / d**2
					v_y = (self.pos_y - neighbor.pos_y) / d**2
					s_x += v_x*self.lastScale**2
					s_y += v_y*self.lastScale**2
		self.pushInterpreter.pushVector( breve.vector(s_x,s_y,0) )

	def alignment(self):
		neighbors = self.getNeighbors()
		a_x = 0
		a_y = 0
		count = 0

		for neighbor in neighbors:
			if neighbor.isA( 'Predator' ) and neighbor.isAlive:
				norm = (self.pos_x-neighbor.pos_x)**2+(self.pos_y-neighbor.pos_y)**2
				if norm < self.controller.neighborRadiusMinor:
					a_x += neighbor.vel_x
					a_y += neighbor.vel_y
					count += 1
		
		if count > 0:
			a_x /= count
			a_y /= count
			a_x -= self.vel_x
			a_y -= self.vel_y
		self.pushInterpreter.pushVector( breve.vector(a_x,a_y,0) )

	def cohension(self):
		neighbors = self.getNeighbors()
		c_x = 0
		c_y = 0
		count = 0

		for neighbor in neighbors:
			if neighbor.isA( 'Predator' ) and neighbor.isAlive:
				norm = (self.pos_x-neighbor.pos_x)**2+(self.pos_y-neighbor.pos_y)**2
				if norm < self.controller.neighborRadiusMinor:
					c_x += neighbor.pos_x
					c_y += neighbor.pos_y
					count += 1
		
		if count > 0:
			c_x /= count
			c_y /= count
			c_x -= self.pos_x
			c_y -= self.pos_y
		self.pushInterpreter.pushVector( breve.vector(c_x,c_y,0) )

	def target(self):
		#neighbors = breve.allInstances( "Bird" )
		neighbors = self.getNeighbors()
		t_x = 0
		t_y = 0
		dist = 99999
		count = 0
		for neighbor in neighbors:
			if neighbor.isA( 'Bird' ) and neighbor.isAlive:
				norm = ((self.pos_x-neighbor.pos_x)**2 + (self.pos_y-neighbor.pos_y)**2)**0.5

				if norm < dist:
					dist = norm
					t_x = neighbor.pos_x-self.pos_x
					t_y = neighbor.pos_y-self.pos_y

		'''if dist == 99999:
			feeders = breve.allInstances( "Bird" )
			for neighbor in feeders:
				norm = ((self.pos_x-neighbor.pos_x)**2 + (self.pos_y-neighbor.pos_y)**2)**0.5
				if norm < dist:
					dist = norm
					t_x = neighbor.pos_x-self.pos_x
					t_y = neighbor.pos_y-self.pos_y'''

		self.pushInterpreter.pushVector( breve.vector(t_x,t_y,0) )

	def currentVelocity(self):
		self.pushInterpreter.pushVector( breve.vector(self.vel_x,self.vel_y,0) )

	def centerOfWorld( self ):
		self.pushInterpreter.pushVector( breve.vector(-self.pos_x,-self.pos_y,0) )

	# end of the functions used by Push
	def changePos(self, x, y):
		self.pos_x = x
		self.pos_y = y
		self.move( breve.vector(x,y,0) )

	def changeAccel(self, x, y):
		norm = (x**2 + y**2)**0.5
		if  norm > self.maxAccel:
			x = x/norm * self.maxAccel
			y = y/norm * self.maxAccel
		self.setAcceleration( breve.vector(x,y,0) )

	def changeVel(self, x, y):
		norm = (x**2 + y**2)**0.5
		if  norm > self.maxVel:
			x = x/norm * self.maxVel
			y = y/norm * self.maxVel
		self.vel_x = x
		self.vel_y = y
		self.setVelocity( breve.vector(x,y,0) )

	def addEnergy(self, num):
		self.energy += num
		if self.energy < 0:
			self.energy = 0

	def getEnergy(self):
		return self.energy

	def eat( self, bird ):
		if self.energy < 1.4 and bird.energy > 0:
			self.addEnergy(0.05)
			bird.addEnergy(-0.05)
	
	def dropDead (self, corpse=True):
		if corpse:
			c = breve.createInstances( breve.Corpse, 1 )
			c.move( self.getLocation() )
			c.setColor (self.getColor() )
			c.energy = self.energy
			#c.lastScale = self.lastScale
			c.adjustSize()
			c.myPoint( breve.vector( 0, 1, 0 ), self.getVelocity())

		self.setColor(breve.vector(0,0,0))
		#just to don't overlap the animation 
		self.changePos(-500,500)
		# self.pushInterpreter.clearStacks()
		self.age = 0
		self.energy = 1
		self.isAlive = False
		self.controller.pollPredators.append(self)
		self.controller.num_dead_predators += 1

	def fly(self):
		pos = self.getLocation()
		self.changePos(pos.x, pos.y)
		self.myPoint( breve.vector( 0, 1, 0 ), self.getVelocity())

		vel = self.getVelocity()
		vel_x = vel.x
		vel_y = vel.y
		self.changeVel(vel_x, vel_y)

		self.pushInterpreter.run( self.pushCode )
		accel = self.pushInterpreter.getVectorStackTop()
		if ( ( ( ( ( breve.breveInternalFunctionFinder.isinf( self, accel.x ) or breve.breveInternalFunctionFinder.isnan( self, accel.x ) ) or breve.breveInternalFunctionFinder.isinf( self, accel.y ) ) or breve.breveInternalFunctionFinder.isnan( self, accel.y ) ) or breve.breveInternalFunctionFinder.isinf( self, accel.z ) ) or breve.breveInternalFunctionFinder.isnan( self, accel.z ) ):
				accel = breve.vector( 0.000000, 0.000000, 0.000000 )
		self.changeAccel(accel.x, accel.y)
		
		# eat
		neighbors = self.getNeighbors()
		for neighbor in neighbors:
			if neighbor.isA( 'Bird' ) and neighbor.isAlive:
				norm = ((self.pos_x-neighbor.pos_x)**2 + (self.pos_y-neighbor.pos_y)**2)**0.5
				if norm <= max(neighbor.lastScale,3):
					self.eat(neighbor) 

		self.addEnergy(-0.01)
		self.adjustSize()
		self.age += 1
		#if self.energy < 0.5 or self.age > 300:
		if self.energy < 0.5:
			self.dropDead()

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
		newScale = ( ( self.energy * 10 ) + 0.500000 )
		self.shape.scale( breve.vector( ( newScale / self.lastScale ), 1, ( newScale / self.lastScale ) ) )
		self.lastScale = newScale

	def init( self ):
		# self.shape = breve.createInstances( breve.PolygonCone, 1 ).initWith( 5, 0.200000, 0.100000 )
		self.shape = breve.createInstances( breve.myCustomShape, 1 )
		self.setShape( self.shape )
		self.adjustSize()
		self.setNeighborhoodSize( self.controller.neighborRadius )

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


Swarm()
