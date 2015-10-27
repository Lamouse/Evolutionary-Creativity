import breve
import random
import math
import copy

__author__ = 'Paulo Pereira'


class Node:
    def __init__(self, left, right, specie):
        self.left = left
        self.right = right
        self.data = None
        self.parent = None

        if specie == 'Bird':
            self.leaf = ["self.alignment()", "self.cohesion()", "self.separation()", "self.target()", "self.flee()",
                         "self.currentVelocity()", "self.centerOfWorld()", "self.mostEnergizedNeighbor()",
                         "self.randV()"]
        elif specie == 'Predator':
            self.leaf = ["self.alignment()", "self.cohesion()", "self.separation()", "self.target()",
                         "self.currentVelocity()", "self.centerOfWorld()", "self.mostEnergizedNeighbor()",
                         "self.randV()"]
        self.node = ["+", "-", "*", "/"]

        self.fill_data()

    def fill_data(self):
        if self.right is None:
            # leaf
            self.data = self.leaf[random.randint(0, len(self.leaf)-1)]
        else:
            # node
            self.data = self.node[random.randint(0, len(self.node)-1)]


class Swarm( breve.Control ):
	def __init__( self ):
		breve.Control.__init__( self )
		self.numBirds = 150
		self.numPred = 25
		self.numBirdsBirth = 0

		# World
		self.minX = -50
		self.maxX = 50
		self.minY = -50
		self.maxY = 50
		self.delta = 1

		# Feeder
		self.maxFoodSupply = 400
		self.minCreatedFoodSupply = 15
		self.maxCreatedFoodSupply = 25
		self.totalFoodSupply = 0

		# List
		self.deadBirds = breve.objectList()

		# Other thing
		Swarm.init( self )

	def createFeeder(self, num, rapid ):
		# Simple Sequential Inhibition
		dist = 0
		x = 0
		y = 0
		while dist < 10:
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
				temp_bird = breve.createInstances( breve.Bird, 1)
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
				temp_bird = breve.createInstances( breve.Predator, 1)
				temp_bird.initializeRandomly(x,y,'m')

	def init( self ):
		self.setBackgroundColor( breve.vector( 0, 0, 0 ) )
		self.setDisplayTextColor( breve.vector( 1, 1, 1 ) )
		self.pointCamera( breve.vector( 0, 0, 0 ), breve.vector( 0, 0, 150 ) )
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
		pos = random.randint(0, len(newBird1.geno))
		newBird1.geno = parent1.geno[0:pos] + parent2.geno[pos:]
		newBird2.geno = parent2.geno[0:pos] + parent1.geno[pos:]

	def mutate(self, newBird):
		# uniform mutation
		for i in range(len(newBird.geno)):
			prob = random.random()
			if prob <= 0.05:
				newBird.geno[i] += random.uniform(-0.5,0.5)

	def createNewBird(self, newBird, parent1, parent2):
		p = random.uniform(0,1)
		v = random.uniform(0,1)
		newBird.changePos(p*parent1.pos_x+(1-p)*parent2.pos_x,p*parent1.pos_y+(1-p)*parent2.pos_y)
		newBird.changeVel(v*parent1.vel_x+(1-v)*parent2.vel_x,v*parent1.vel_y+(1-v)*parent2.vel_y)
		newBird.energy = 1.0
		newBird.isAlive = True
		if newBird.isA( 'Bird' ):
			if newBird.gener == 'f':
				newBird.setColor( breve.vector( 1, 0.08, 0.58 ) )
			else:
				newBird.setColor( breve.vector( 0, 0, 1 ) )
		else:
			if newBird.gener == 'f':
				newBird.setColor( breve.vector( 0.58, 0.08, 1 ) )
			else:
				newBird.setColor( breve.vector( 1, 0, 0 ) )
		
	def evolutionayAlgorithm(self):
		if len(self.deadBirds) < 2:
			return

		newBird1 = self.deadBirds[0]
		self.deadBirds.remove(newBird1)

		newBird2 = None
		for dead in self.deadBirds:
			if dead.getType() == newBird1.getType():
				newBird2 = dead
				self.deadBirds.remove(newBird2)
				break

		if newBird2 is None:
			self.deadBirds.append(newBird1)
			return

		created = False
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

				self.numBirdsBirth += 2
				created = True

		if not created:
			self.deadBirds.append(newBird1)
			self.deadBirds.append(newBird2)

	def fill_parents(self, tree):
	    if tree.right is not None:
	        # node
	        tree.left.parent = tree
	        tree.right.parent = tree

	        fill_parents(tree.left)
	        fill_parents(tree.right)


	def print_tree(self, tree):
	    if tree.right is None:
	        # leaf
	        print tree.data, 
	    else:
	        # node
	        print "(",
	        print_tree(tree.left)
	        print tree.data,
	        print_tree(tree.right)
	        print ")",


	def run_code(self, tree):
	    if tree.right is None:
	        # leaf
	        # it should execute the code
	        # return exec(tree.data)
	        return [random.uniform(-5, 5), random.uniform(-5, 5)]
	    else:
	        # node
	        return [eval('x'+tree.data+'y') for x, y in zip(run_code(tree.left), run_code(tree.right))]


	def select_random_node(self, tree, list_nodes):
	    if tree.right is not None:
	        list_nodes.append(tree)
	        select_random_node(tree.left, list_nodes)
	        select_random_node(tree.right, list_nodes)


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
	    current_node.left = tree_copy(parent1.left)
	    current_node.right = tree_copy(parent1.right)
	    return current_node


	def tree_mutation(self, tree):
	    prob = random.random()
	    if prob <= 0.05:
	        node_list = []
	        select_random_node(tree, node_list)
	        index = random.randint(1, len(node_list)-1)
	        depth = random.randint(1, 5)
	        new_sub_tree = create_random_tree(depth, "Bird")
	        replace_tree(node_list[index], new_sub_tree)
	        fill_parents(tree)


	def tree_crossover(self, parent1, parent2):
	    tree_child1 = tree_copy(parent1)
	    tree_child2 = tree_copy(parent2)
	    fill_parents(tree_child1)
	    fill_parents(tree_child2)

	    node_list1 = []
	    select_random_node(tree_child1, node_list1)
	    index1 = random.randint(1, len(node_list1)-1)

	    node_list2 = []
	    select_random_node(tree_child2, node_list2)
	    index2 = random.randint(1, len(node_list2)-1)

	    subtree_parent1 = node_list1[index1]
	    subtree_parent2 = node_list2[index2]

	    replace_tree(subtree_parent1, subtree_parent2)
	    replace_tree(subtree_parent2, subtree_parent1)
	    fill_parents(tree_child1)
	    fill_parents(tree_child2)

	    return tree_child1, tree_child2

	def iterate( self ):
		self.updateNeighbors()

		for bird in breve.allInstances( "Bird" ):
			if bird.isAlive:
				bird.fly()

		for predator in breve.allInstances( "Predator" ):
			if predator.isAlive:
				predator.fly()

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

		for i in range(breve.length(self.deadBirds)):
			self.evolutionayAlgorithm()

		self.setDisplayText("Births: "+str(self.numBirdsBirth), xLoc = -0.950000, yLoc = -0.950000, theColor = breve.vector( 1, 1, 1 ))

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
		self.radius = 2
		self.geno = None
		#self.geno = [0.005, 0.01, 1, 0.005, 1]

		self.lastScale = 1
		Bird.init( self )


	def initializeRandomly( self, x, y, gener):
		if gener == 'f':
			self.setColor( breve.vector( 1, 0.08, 0.58) )
		else:
			self.setColor( breve.vector( 0, 0, 1 ) )
		self.gener = gener

		self.changePos(x,y)
		self.geno = [random.uniform(-5, 5) for x in range(6)]
		vel_x = random.uniform(-self.maxVel, self.maxVel)
		vel_y = random.uniform(-self.maxVel, self.maxVel)
		self.changeVel(vel_x, vel_y)

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
		if self.energy < 1.4:
			self.addEnergy(0.05)
			feeder.addEnergy(-0.05)
	
	def dropDead (self):
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
		self.age = 0
		self.energy = 1
		self.isAlive = False
		self.controller.deadBirds.append(self)

	def fly(self):
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
		for neighbor in neighbors:
			if neighbor.isA( 'Feeder' ):
				norm = ((self.pos_x-neighbor.pos_x)**2 + (self.pos_y-neighbor.pos_y)**2)**0.5
				#target
				if norm*(1-neighbor.energy) < dist:
					dist = norm*(1-neighbor.energy)
					t_x = neighbor.pos_x-self.pos_x
					t_y = neighbor.pos_y-self.pos_y

				if norm <= max(neighbor.lastScale,3):
					self.eat(neighbor) 

			elif neighbor.isA( 'Bird' ) and neighbor.isAlive:
				norm = ((self.pos_x-neighbor.pos_x)**2 + (self.pos_y-neighbor.pos_y)**2)**0.5
				if 0 < norm < self.radius:
					# separation
					v_x = (self.pos_x - neighbor.pos_x) / norm**2
					v_y = (self.pos_y - neighbor.pos_y) / norm**2
					s_x += v_x*self.lastScale**2
					s_y += v_y*self.lastScale**2
				# alignment
				a_x += neighbor.vel_x
				a_y += neighbor.vel_y
				c_x += neighbor.pos_x
				# cohesion
				c_y += neighbor.pos_y
				count += 1

			elif neighbor.isA( 'Predator' ) and neighbor.isAlive:
				norm = ((self.pos_x-neighbor.pos_x)**2 + (self.pos_y-neighbor.pos_y)**2)**0.5
				#flee
				v_x = (self.pos_x - neighbor.pos_x) / norm**2
				v_y = (self.pos_y - neighbor.pos_y) / norm**2
				f_x += v_x*self.lastScale**2
				f_y += v_y*self.lastScale**2

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

		accel_x = self.geno[0]*c_x+self.geno[1]*a_x+self.geno[2]*s_x+self.geno[3]*t_x+self.geno[4]*f_x+self.geno[5]*rand_x
		accel_y = self.geno[0]*c_y+self.geno[1]*a_y+self.geno[2]*s_y+self.geno[3]*t_y+self.geno[4]*f_y+self.geno[5]*rand_y
		self.changeAccel(accel_x, accel_y)
		vel = self.getVelocity()
		vel_x = vel.x
		vel_y = vel.y
		self.changeVel(vel_x, vel_y)

		pos = self.getLocation()
		self.changePos(pos.x, pos.y)
		self.myPoint( breve.vector( 0, 1, 0 ), self.getVelocity())
		

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
		self.shape = breve.createInstances( breve.PolygonCone, 1 ).initWith( 5, 0.200000, 0.100000 )
		self.setShape( self.shape )
		self.adjustSize()
		self.setNeighborhoodSize( 10.0 )

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
		self.maxVel = 0.5
		self.maxAccel = 2
		self.gener = 'm'
		self.radius = 2
		self.geno = None
		
		self.lastScale = 1
		Predator.init( self )

	def initializeRandomly( self, x, y, gener):
		if gener == 'f':
			self.setColor( breve.vector( 0.58, 0.08, 1 ) )
		else:
			self.setColor( breve.vector( 1, 0, 0 ) )
		self.gener = gener

		self.changePos(x,y)
		self.geno = [random.uniform(-5, 5) for x in range(5)]
		vel_x = random.uniform(-self.maxVel, self.maxVel)
		vel_y = random.uniform(-self.maxVel, self.maxVel)
		self.changeVel(vel_x, vel_y)

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
		if self.energy < 1.4:
			self.addEnergy(0.05)
			bird.addEnergy(-0.05)
	
	def dropDead (self):
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
		self.age = 0
		self.energy = 1
		self.isAlive = False
		self.controller.deadBirds.append(self)

	def fly(self):
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
			if neighbor.isA( 'Bird' ) and neighbor.isAlive:
				norm = ((self.pos_x-neighbor.pos_x)**2 + (self.pos_y-neighbor.pos_y)**2)**0.5
				#target
				if norm*(1-neighbor.energy) < dist:
					dist = norm*(1-neighbor.energy)
					t_x = neighbor.pos_x-self.pos_x
					t_y = neighbor.pos_y-self.pos_y

				if norm <= max(neighbor.lastScale,3):
					self.eat(neighbor) 

			elif neighbor.isA( 'Predator' ) and neighbor.isAlive:
				norm = ((self.pos_x-neighbor.pos_x)**2 + (self.pos_y-neighbor.pos_y)**2)**0.5
				if 0 < norm < self.radius:
					# separation
					v_x = (self.pos_x - neighbor.pos_x) / norm**2
					v_y = (self.pos_y - neighbor.pos_y) / norm**2
					s_x += v_x*self.lastScale**2
					s_y += v_y*self.lastScale**2
				# alignment
				a_x += neighbor.vel_x
				a_y += neighbor.vel_y
				c_x += neighbor.pos_x
				# cohesion
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

		accel_x = self.geno[0]*c_x+self.geno[1]*a_x+self.geno[2]*s_x+self.geno[3]*t_x+self.geno[4]*rand_x
		accel_y = self.geno[0]*c_y+self.geno[1]*a_y+self.geno[2]*s_y+self.geno[3]*t_y+self.geno[4]*rand_y
		self.changeAccel(accel_x, accel_y)
		vel = self.getVelocity()
		vel_x = vel.x
		vel_y = vel.y
		self.changeVel(vel_x, vel_y)

		pos = self.getLocation()
		self.changePos(pos.x, pos.y)
		self.myPoint( breve.vector( 0, 1, 0 ), self.getVelocity())

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
		self.shape = breve.createInstances( breve.PolygonCone, 1 ).initWith( 5, 0.200000, 0.100000 )
		self.setShape( self.shape )
		self.adjustSize()
		self.setNeighborhoodSize( 10.0 )

breve.Predator = Predator

Swarm()
