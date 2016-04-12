import breve
import random
import math
import copy
import cPickle
import time

__author__ = 'Paulo Pereira'


class Swarm( breve.Control ):
	def __init__( self ):
		breve.Control.__init__( self )

		# Random Number Generator
		random.seed( 5 )
		self.setRandomSeed( 5 )
		# self.setRandomSeedFromDevRandom()

		# World
		self.minX = -200
		self.maxX = 200
		self.minY = -100
		self.maxY = 100

		self.targetZone = 40
		self.socialZone = 15
		self.separationZone = 3

		# Feeder
		self.feederMinDistance = 25
		self.maxFoodSupply = 300
		self.minCreatedFoodSupply = 7
		self.maxCreatedFoodSupply = 15
		self.totalFoodSupply = 0

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
				
	def init( self ):
		self.setBackgroundColor( breve.vector( 0, 0, 0 ) )
		self.setDisplayTextColor( breve.vector( 1, 1, 1 ) )
		self.pointCamera( breve.vector( 0, 0, 0 ), breve.vector( 0, 0, 300 ) )
		self.setIterationStep(1.0)
		self.enableDrawEveryFrame()
		self.enableSmoothDrawing()

		self.addRandomFeederIfNecessary()
		breve.createInstances( breve.Prey, 1).initializeRandomly(0,0,'m')

		breve.createInstances( breve.Neighborhood1, 1)
		breve.createInstances( breve.Neighborhood2, 1)
		breve.createInstances( breve.Neighborhood3, 1)

	def addTotalFoodSupply(self, num):
		self.totalFoodSupply += num;

	def addRandomFeederIfNecessary( self, rapid=False):
		while (self.maxFoodSupply-self.totalFoodSupply) >= self.maxCreatedFoodSupply:
			self.createFeeder(1, rapid)

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


class Prey( breve.Stationary ):
	def __init__( self ):
		breve.Stationary.__init__( self )
		self.shape = None
		# can be changed
		self.pos_x = -9999
		self.pos_y = -9999

		# change with time
		self.energy = 1.0
		self.age = 0
		self.isAlive = True

		# static
		self.gener = 'm'
		self.geno = None

		self.lastScale = 1
		Prey.init( self )

	def initializeRandomly( self, x, y, gener):
		self.changePos(x,y)

		self.age = 0
		self.gener = gener
		self.setNewColor()

	def setNewColor( self ):
		self.setColor( breve.vector( 0, 0, 0) )

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
		self.move( breve.vector(x,y,10) )

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


class Neighborhood1 (breve.Stationary ):
	def __init__( self ):
		breve.Stationary.__init__( self )
		self.shape = None
		self.pos_x = 0
		self.pos_y = 0
		Neighborhood1.init( self )

	def init( self ):
		self.shape = breve.createInstances(breve.Sphere, 1).initWith(self.controller.targetZone)
		self.move( breve.vector(0,0, -70) )
		self.setShape(self.shape)
		self.setColor( breve.vector(0, 1, 0) )


breve.Neighborhood1 = Neighborhood1


class Neighborhood2 (breve.Stationary ):
	def __init__( self ):
		breve.Stationary.__init__( self )
		self.shape = None
		self.pos_x = 0
		self.pos_y = 0
		Neighborhood2.init( self )

	def init( self ):
		self.shape = breve.createInstances(breve.Sphere, 1).initWith(self.controller.socialZone)
		self.move( breve.vector(0,0, -30) )
		self.setShape(self.shape)
		self.setColor( breve.vector(1, 1, 0) )


breve.Neighborhood2 = Neighborhood2


class Neighborhood3 (breve.Stationary ):
	def __init__( self ):
		breve.Stationary.__init__( self )
		self.shape = None
		self.pos_x = 0
		self.pos_y = 0
		Neighborhood3.init( self )

	def init( self ):
		self.shape = breve.createInstances(breve.Sphere, 1).initWith(self.controller.separationZone)
		self.move( breve.vector(0,0,0) )
		self.setShape(self.shape)
		self.setColor( breve.vector(1, 0, 0) )


breve.Neighborhood3 = Neighborhood3

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
