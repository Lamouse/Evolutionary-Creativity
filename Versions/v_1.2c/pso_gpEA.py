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
            self.leaf = ["indiv.alignment()", "indiv.cohesion()", "indiv.separation()", "indiv.target()", "indiv.flee()",
                         "indiv.currentVelocity()", "indiv.centerOfWorld()", "indiv.mostEnergizedNeighbor()",
                         "indiv.randV()"]
        elif specie == 'Predator':
            self.leaf = ["indiv.alignment()", "indiv.cohesion()", "indiv.separation()", "indiv.target()",
                         "indiv.currentVelocity()", "indiv.centerOfWorld()", "indiv.mostEnergizedNeighbor()",
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


class Swarm( breve.Control ):
	def __init__( self ):
		breve.Control.__init__( self )
		self.numBirds = 150
		self.numPred = 25
		self.num_dead_birds = 0
		self.num_dead_predators = 0

		# World
		self.minX = -50
		self.maxX = 50
		self.minY = -50
		self.maxY = 50
		self.delta = 1

		# Feeder
		self.maxFoodSupply = 600
		self.minCreatedFoodSupply = 15
		self.maxCreatedFoodSupply = 25
		self.totalFoodSupply = 0

		# List
		self.current_generation = 0
		self.breeding_season = 50
		self.breeding_inc = 0.5
		self.max_pop_predadors = 0.5
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
		while dist < 7:
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
					temp_bird.initializeRandomly(x, y, random.choice(["m", "f"]))
				else:
					temp_bird = self.pollBirds[0]
					self.pollBirds.remove(temp_bird)
					temp_bird.initializeRandomly(x, y, random.choice(["m", "f"]))

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
					temp_predator.initializeRandomly(x, y, random.choice(["m", "f"]))
				else:
					temp_predator = self.pollPredators[0]
					self.pollPredators.remove(temp_predator)
					temp_predator.initializeRandomly(x, y, random.choice(["m", "f"]))

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
	def selectBestCandidate( self, parent1, specie):
		bestCandidate = self.selectNearParent(parent1, specie)
		if bestCandidate is not None:
			for i in range(1, 4):
				candidate = self.selectNearParent(parent1, specie)
				if abs(parent1.tail-candidate.tail) < abs(parent1.tail-bestCandidate.tail):
					bestCandidate = candidate
			# print bestCandidate.tail
		return bestCandidate

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
		newBird1.geno, newBird2.geno = self.tree_crossover(parent1.geno, parent2.geno)

	def mutate(self, newBird):
		prob = random.random()
		if prob <= self.prob_mutation:
			self.tree_mutation(newBird.geno, newBird.getType())

	def createNewBird(self, newBird, parent1, parent2):
		p = random.uniform(0,1)
		v = random.uniform(0,1)
		newBird.changePos(p*parent1.pos_x+(1-p)*parent2.pos_x,p*parent1.pos_y+(1-p)*parent2.pos_y)
		newBird.changeVel(v*parent1.vel_x+(1-v)*parent2.vel_x,v*parent1.vel_y+(1-v)*parent2.vel_y)
		newBird.energy = 1.0
		newBird.isAlive = True
		newBird.gener = random.choice(["m", "f"])
		newBird.setNewColor()

		t = random.uniform(0,1)
		newBird.tail = t*parent1.tail + (1-t)*parent2.tail
		if newBird.tail < 0:
			newBird.tail = 0
		elif newBird.tail > 1:
			newBird.tail = 1
		
	def evolutionayAlgorithm(self, array):
		if breve.length(array) < 2:
			return

		newBird1 = array[0]
		newBird2 = array[1]

		# classic evolutionay algorithm
		parent1 = self.selectParent(newBird1.getType())
		if parent1 is not None:
			parent2 = self.selectBestCandidate(parent1, newBird1.getType())
			if parent2 is not None:
				self.crossover(newBird1, newBird2, parent1, parent2)
				self.mutate(newBird1)
				self.mutate(newBird2)
				self.createNewBird(newBird1, parent2, parent1)
				self.createNewBird(newBird2, parent1, parent2)
				
				array.remove(newBird1)
				array.remove(newBird2)

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
				new_birds = int(math.floor(self.breeding_inc*self.numBirds)) - breve.length(self.pollBirds)
				breve.createInstances( breve.Bird, new_birds).dropDead(False)

			if breve.length(self.pollPredators) < self.breeding_inc*self.numPred:
				new_preds = int(math.floor(self.breeding_inc*self.numPred)) - breve.length(self.pollPredators)
				breve.createInstances( breve.Predator, new_preds).dropDead(False)

			for i in range(int(math.floor(self.breeding_inc*self.numBirds))/2):
				self.evolutionayAlgorithm(self.pollBirds)
			if self.numPred < self.numBirds*self.max_pop_predadors:
				for i in range(int(min(math.floor(self.breeding_inc*self.numPred), self.numBirds*self.max_pop_predadors))/2):
					self.evolutionayAlgorithm(self.pollPredators)

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
		self.radius = 2
		self.geno = None
		self.tail = 0

		self.lastScale = 1
		Bird.init( self )


	def initializeRandomly( self, x, y, gener):
		self.changePos(x,y)
		vel_x = random.uniform(-self.maxVel, self.maxVel)
		vel_y = random.uniform(-self.maxVel, self.maxVel)
		self.changeVel(vel_x, vel_y)

		self.gener = gener
		self.setNewColor()

		self.geno = self.controller.create_random_tree(3, "Bird")
		self.tail = random.uniform(0, 1)		

	def setNewColor( self ):
		if self.gener == 'f':
			self.setColor( breve.vector( 0.5, 0.5, 1) )
		else:
			self.setColor( breve.vector( 0, 0, 1 ) )

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
		self.age = 0
		self.energy = 1
		self.isAlive = False
		self.controller.pollBirds.append(self)
		self.controller.num_dead_birds += 1

	def alignment(self):
		neighbors = self.getNeighbors()
		a_x = 0
		a_y = 0
		count = 0
		for neighbor in neighbors:
			if neighbor.isA( 'Bird' ) and neighbor.isAlive:
				# alignment
				a_x += neighbor.vel_x
				a_y += neighbor.vel_y
				count += 1

		if count > 0:
			a_x /= count
			a_y /= count
			a_x -= self.vel_x
			a_y -= self.vel_y
		return [a_x, a_y]

	def cohesion(self):
		neighbors = self.getNeighbors()
		c_x = 0
		c_y = 0
		count = 0
		for neighbor in neighbors:
			if neighbor.isA( 'Bird' ) and neighbor.isAlive:
				# cohesion
				c_x += neighbor.pos_x
				c_y += neighbor.pos_y
				count += 1

		if count > 0:
			c_x /= count
			c_y /= count
			c_x -= self.pos_x
			c_y -= self.pos_y
		return [c_x, c_y]

	def separation(self):
		neighbors = self.getNeighbors()
		s_x = 0
		s_y = 0
		count = 0
		for neighbor in neighbors:
			if neighbor.isA( 'Bird' ) and neighbor.isAlive:
				norm = ((self.pos_x-neighbor.pos_x)**2 + (self.pos_y-neighbor.pos_y)**2)**0.5
				if 0 < norm < self.radius:
					# separation
					v_x = (self.pos_x - neighbor.pos_x) / norm**2
					v_y = (self.pos_y - neighbor.pos_y) / norm**2
					s_x += v_x*self.lastScale**2
					s_y += v_y*self.lastScale**2
		return [s_x, s_y]

	def target(self):
		neighbors = self.getNeighbors()
		t_x = 0
		t_y = 0
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
		return [t_x, t_y]

	def flee(self):
		neighbors = self.getNeighbors()
		f_x = 0
		f_y = 0

		for neighbor in neighbors:
			if neighbor.isA( 'Predator' ) and neighbor.isAlive:
				norm = ((self.pos_x-neighbor.pos_x)**2 + (self.pos_y-neighbor.pos_y)**2)**0.5
				#flee
				v_x = (self.pos_x - neighbor.pos_x) / norm**2
				v_y = (self.pos_y - neighbor.pos_y) / norm**2
				f_x += v_x*self.lastScale**2
				f_y += v_y*self.lastScale**2
		return [f_x, f_y]

	def currentVelocity(self):
		return [self.vel_x,self.vel_y]

	def centerOfWorld(self):
		return [-self.pos_x,-self.pos_y]

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
		return [me_x, me_y]

	def randV(self):
		rand_x = random.uniform(0, 1)
		rand_y = random.uniform(0, 1)
		return [rand_x, rand_y]

	def fly(self):
		pos = self.getLocation()
		self.changePos(pos.x, pos.y)
		self.myPoint( breve.vector( 0, 1, 0 ), self.getVelocity())

		vel = self.getVelocity()
		vel_x = vel.x
		vel_y = vel.y
		self.changeVel(vel_x, vel_y)

		accel_x, accel_y = self.controller.run_code(self, self.geno)
		self.changeAccel(accel_x, accel_y)
		
		# eat
		neighbors = self.getNeighbors()
		for neighbor in neighbors:
			if neighbor.isA( 'Feeder' ):
				norm = ((self.pos_x-neighbor.pos_x)**2 + (self.pos_y-neighbor.pos_y)**2)**0.5
				if norm <= max(neighbor.lastScale,3):
					self.eat(neighbor) 

		if self.gener == "m":
			self.addEnergy(-0.01-0.005*self.tail)
		else:
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
		self.tail = 0
		
		self.lastScale = 1
		Predator.init( self )

	def initializeRandomly( self, x, y, gener):
		self.changePos(x,y)
		vel_x = random.uniform(-self.maxVel, self.maxVel)
		vel_y = random.uniform(-self.maxVel, self.maxVel)
		self.changeVel(vel_x, vel_y)

		self.gener = gener
		self.setNewColor()

		self.geno = self.controller.create_random_tree(3, "Predator")
		self.tail = random.uniform(0, 1)

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
		self.age = 0
		self.energy = 1
		self.isAlive = False
		self.controller.pollPredators.append(self)
		self.controller.num_dead_predators += 1

	def alignment(self):
		neighbors = self.getNeighbors()
		a_x = 0
		a_y = 0
		count = 0
		for neighbor in neighbors:
			if neighbor.isA( 'Predator' ) and neighbor.isAlive:
				# alignment
				a_x += neighbor.vel_x
				a_y += neighbor.vel_y
				count += 1

		if count > 0:
			a_x /= count
			a_y /= count
			a_x -= self.vel_x
			a_y -= self.vel_y
		return [a_x, a_y]

	def cohesion(self):
		neighbors = self.getNeighbors()
		c_x = 0
		c_y = 0
		count = 0
		for neighbor in neighbors:
			if neighbor.isA( 'Predator' ) and neighbor.isAlive:
				# cohesion
				c_x += neighbor.pos_x
				c_y += neighbor.pos_y
				count += 1

		if count > 0:
			c_x /= count
			c_y /= count
			c_x -= self.pos_x
			c_y -= self.pos_y
		return [c_x, c_y]

	def separation(self):
		neighbors = self.getNeighbors()
		s_x = 0
		s_y = 0
		count = 0
		for neighbor in neighbors:
			if neighbor.isA( 'Predator' ) and neighbor.isAlive:
				norm = ((self.pos_x-neighbor.pos_x)**2 + (self.pos_y-neighbor.pos_y)**2)**0.5
				if 0 < norm < self.radius:
					# separation
					v_x = (self.pos_x - neighbor.pos_x) / norm**2
					v_y = (self.pos_y - neighbor.pos_y) / norm**2
					s_x += v_x*self.lastScale**2
					s_y += v_y*self.lastScale**2
		return [s_x, s_y]

	def target(self):
		neighbors = self.getNeighbors()
		t_x = 0
		t_y = 0
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
		return [t_x, t_y]

	def currentVelocity(self):
		return [self.vel_x,self.vel_y]

	def centerOfWorld(self):
		return [-self.pos_x,-self.pos_y]

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
		return [me_x, me_y]

	def randV(self):
		rand_x = random.uniform(0, 1)
		rand_y = random.uniform(0, 1)
		return [rand_x, rand_y]

	def fly(self):
		accel_x, accel_y = self.controller.run_code(self, self.geno)
		self.changeAccel(accel_x, accel_y)
		vel = self.getVelocity()
		vel_x = vel.x
		vel_y = vel.y
		self.changeVel(vel_x, vel_y)

		pos = self.getLocation()
		self.changePos(pos.x, pos.y)
		self.myPoint( breve.vector( 0, 1, 0 ), self.getVelocity())

		# eat
		neighbors = self.getNeighbors()
		for neighbor in neighbors:
			if neighbor.isA( 'Bird' ) and neighbor.isAlive:
				norm = ((self.pos_x-neighbor.pos_x)**2 + (self.pos_y-neighbor.pos_y)**2)**0.5
				if norm <= max(neighbor.lastScale,3):
					self.eat(neighbor) 

		if self.gener == "m":
			self.addEnergy(-0.01-0.005*self.tail)
		else:
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
