__author__ = 'Paulo Pereira'

import breve
import random

class Swarm( breve.Control ):
	def __init__( self ):
		breve.Control.__init__( self )
		# World
		self.minX = -25
		self.maxX = 25
		self.minY = -25
		self.maxY = 25
		self.delta = 0.1

		# Feeders
		self.maxFoodSupply = 15
		self.minCreatedFoodSupply = 3
		self.maxCreatedFoodSupply = 5
		self.totalFoodSupply = 0

		# Other thing
		Swarm.init( self )

	def addTotalFoodSupply(self, num):
		self.totalFoodSupply += num;

	def addRandomFeedersIfNecessary( self, last=False ):
		while (self.maxFoodSupply-self.totalFoodSupply) >= self.maxCreatedFoodSupply:
			breve.createInstances( breve.Feeders, 1 ).initializeRandomly()
		#if last and (self.maxFoodSupply-self.totalFoodSupply) >= self.minCreatedFoodSupply:
		#	breve.createInstances( breve.Feeders, 1 ).initializeRandomly(True, self.maxFoodSupply-self.totalFoodSupply)

	def init( self ):
		# self.cloudTexture = breve.createInstances( breve.Image, 1 ).load( 'images/clouds.png' )
		# self.setBackgroundTextureImage( self.cloudTexture )
		# self.setBackgroundTextureImage( self.cloudTexture )
		# floor = breve.createInstances( breve.Stationary, 1 )
		# floor.register( breve.createInstances( breve.Cube, 1 ).initWith( breve.vector( 100, 100, 2 ) ), breve.vector( 0, 0, -5 ) )
		# floor.setColor( breve.vector(1, 1, 1) )
		self.setBackgroundColor( breve.vector( 0, 0, 0 ) )

		self.pointCamera( breve.vector( 0, 0, 0 ), breve.vector( 0, 0, 80 ) )

		self.addRandomFeedersIfNecessary(last=True)
		breve.createInstances( breve.Bird, 100 ).initializeRandomly()

	def iterate( self ):
		self.updateNeighbors()

		birds = breve.allInstances( "Bird" )

		for bird in birds:
			bird.fly()

		# needed to move the agents with velocity and acceleration
		# also needed to detect collisions
		# breve.Control.iterate( self )


breve.Swarm = Swarm

class Feeders (breve.Stationary ):
	def __init__( self ):
		breve.Stationary.__init__( self )
		self.shape = None
		self.pos_x = 0
		self.pos_y = 0
		self.energy = 0
		self.lastScale = 1
		Feeders.init( self )

	def initializeRandomly( self, last=False, energy=0 ):
		x = random.uniform(self.controller.minX, self.controller.maxX)
		y = random.uniform(self.controller.minY, self.controller.maxY)
		self.changePos(x,y)

		if last:
			self.energy = energy
		else:
			self.energy = random.uniform(self.controller.minCreatedFoodSupply, self.controller.maxCreatedFoodSupply)
		self.controller.addTotalFoodSupply(self.energy)
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
		newScale = 0
		radius = 0

		radius = breve.breveInternalFunctionFinder.sqrt( self, self.energy )
		newScale = ( ( radius * 2 ) + 0.000010 )
		if ( newScale == self.lastScale ):
			return

		newScale = ( newScale / self.lastScale )
		self.shape.scale( breve.vector( newScale, newScale, newScale ) )
		self.lastScale = ( ( radius * 2 ) + 0.000010 )

	def init( self ):
		self.shape = breve.createInstances(breve.Sphere, 1).initWith(0.300000)
		self.setShape(self.shape)
		self.setColor( breve.vector(1, 1, 0) )


breve.Feeders = Feeders

class Bird( breve.Mobile ):
	def __init__( self ):
		breve.Mobile.__init__( self )
		self.shape = None
		self.pos_x = 0
		self.pos_y = 0
		self.vel_x = 0
		self.vel_y = 0
		self.maxVel = 2
		self.energy = 1
		self.age = 0
		self.lastScale = 1
		Bird.init( self )

	def initializeRandomly( self, last=False, energy=0 ):
		x = random.uniform(self.controller.minX, self.controller.maxX)
		y = random.uniform(self.controller.minY, self.controller.maxY)
		self.changePos(x,y)

		vel_x = random.uniform(-self.maxVel, self.maxVel)
		vel_y = random.uniform(-self.maxVel, self.maxVel)
		self.changeVel(vel_x, vel_y)

	def changePos(self, x, y):
		self.pos_x = x
		self.pos_y = y
		self.move( breve.vector(x,y,0) )

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
		# do something
		pass

	def fly(self):
		# self.addEnergy(-0.01)
		# self.adjustSize()
		
		neighbors = self.getNeighbors()

		s_x = 0
		s_y = 0
		a_x = 0
		a_y = 0
		c_x = 0
		c_y = 0
		t_x = 0
		t_y = 0
		dist = 99999
		vel_x = self.vel_x
		vel_y = self.vel_y
		count = 0

		for neighbor in neighbors:
			if neighbor.isA( 'Bird' ):
				# Separation
				v_x = self.pos_x - neighbor.pos_x
				v_y = self.pos_y - neighbor.pos_y
				d = (self.pos_x-neighbor.pos_x)**2+(self.pos_y-neighbor.pos_y)**2
				if 0 < d < 1:
					v_x /= d**2
					v_y /= d**2
					s_x += v_x*self.lastScale**2
					s_y += v_y*self.lastScale**2
				# Alignment
				a_x += neighbor.vel_x
				a_y += neighbor.vel_y

				# Cohension
				c_x += neighbor.pos_x
				c_y += neighbor.pos_y

				count += 1
			elif neighbor.isA( 'Feeders' ):
				# Target
				norm = (self.pos_x-neighbor.pos_x)**2 + (self.pos_y-neighbor.pos_y)**2 
				if norm < dist:
					t_x = neighbor.pos_x-self.pos_x
					t_y = neighbor.pos_y-self.pos_y

		if count > 0:
			# Alignment
			a_x /= count
			a_y /= count
			a_x -= self.vel_x
			a_y -= self.vel_y
			# Cohension
			c_x /= count
			c_y /= count
			c_x -= self.pos_x
			c_y -= self.pos_y

		vel_x += c_x * 0.005 + a_x * 0.01 + s_x * 1 + t_x * 0.005
		vel_y += c_y * 0.005 + a_y * 0.01 + s_y * 1 + t_y * 0.005

		self.changeVel(vel_x, vel_y)
		self.changePos(self.pos_x+self.vel_x*self.controller.delta, self.pos_y+self.vel_y*self.controller.delta)
		self.myPoint( breve.vector( 0, 1, 0 ), self.getVelocity())
		
	def cross( self, v1, v2 ):
		z = 0
		y = 0
		x = 0

		x = ( ( v1.y * v2.z ) - ( v1.z * v2.y ) )
		y = ( ( v1.z * v2.x ) - ( v1.x * v2.z ) )
		z = ( ( v1.x * v2.y ) - ( v1.y * v2.x ) )
		return breve.vector( x, y, z )

	def myPoint( self, theVertex, theLocation ):
		v = breve.vector()
		a = 0

		v = self.cross( theVertex, theLocation )
		a = breve.breveInternalFunctionFinder.angle( self, theVertex, theLocation )
		if ( breve.length( v ) == 0.000000 ):
			self.rotate( theVertex, 0.100000 )
			return

		self.rotate( v, a )

	def adjustSize( self ):
		newScale = 0
		newScale = ( ( self.energy * 10 ) + 0.500000 )
		self.shape.scale( breve.vector( ( newScale / self.lastScale ), 1, ( newScale / self.lastScale ) ) )
		self.lastScale = newScale

	def init( self ):
		self.shape = breve.createInstances( breve.PolygonCone, 1 ).initWith( 5, 0.200000, 0.100000 )
		self.setShape( self.shape )
		self.setColor( breve.vector( 0, 0, 1 ) )
		self.adjustSize()
		self.setNeighborhoodSize( 10.0 )
		self.handleCollisions( 'Feeders', 'eat' )

breve.Bird = Bird


Swarm()


