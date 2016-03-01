import breve

class Test( breve.Control ):
	def __init__( self ):
		breve.Control.__init__( self )

		self.object1 = None
		self.object2 = None
		self.object3 = None

		self.begin = True

		Test.init( self )

	def init( self ):
		self.setBackgroundColor( breve.vector( 0, 0, 0 ) )
		self.setDisplayTextColor( breve.vector( 1, 1, 1 ) )
		self.setIterationStep(1.0)

		self.object1 = breve.createInstances( breve.CustomObject, 1)
		self.object2 = breve.createInstances( breve.CustomObject, 1)
		self.object3 = breve.createInstances( breve.CustomObject, 1)

		self.object1.pushInterpreter.pushVector( breve.vector(1, 2, 3) )
		self.object2.pushInterpreter.pushVector( breve.vector(100, 200, 300) )

		# first run
		self.object1.pushInterpreter.clearStacks()
		self.object1.pushInterpreter.run( self.object1.pushCode )
		print self.object1.pushInterpreter.getVectorStackTop()

		self.object2.pushInterpreter.clearStacks()
		self.object2.pushInterpreter.run( self.object1.pushCode )
		print self.object2.pushInterpreter.getVectorStackTop()

		print self.object3.pushCode.getList()
		# crossover
		self.crossover_push(self.object3, self.object1, self.object2)

		print self.object1.pushCode.getList()
		print self.object2.pushCode.getList()
		print self.object3.pushCode.getList()

		# second run
		'''self.object1.pushInterpreter.clearStacks()
		self.object1.pushInterpreter.run( self.object1.pushCode )
		print self.object1.pushInterpreter.getVectorStackTop()

		self.object2.pushInterpreter.clearStacks()
		self.object2.pushInterpreter.run( self.object1.pushCode )
		print self.object2.pushInterpreter.getVectorStackTop()'''


	def crossover_push(self, newBird, parent1, parent2):
		newBird.pushInterpreter.clearStacks()
		error = False

		c1 = breve.createInstances( breve.PushProgram, 1 )
		c2 = breve.createInstances( breve.PushProgram, 1 )
		c3 = breve.createInstances( breve.PushProgram, 1 )
		parent1.pushInterpreter.copyCodeStackTop( c1 )
		if ( c1.getSize() > 0 ):
			parent2.pushInterpreter.copyCodeStackTop( c2 )
			if ( c2.getSize() > 0 ):
				c3.crossover( c1, c2, newBird.pushInterpreter )
				newBird.pushInterpreter.pushCode( c3 )

				if len(c3.getList()) > 0:
					a = self.object3.pushCode
					self.object3.pushCode = c3
					c3 = a
				else:
					error = True
			else:
				error = True

		if error:
			newBird.pushInterpreter.pushCode( c1 )
			a = self.object3.pushCode
			self.object3.pushCode = c1
			c1 = a

		breve.deleteInstances( c1 )
		breve.deleteInstances( c2 )
		breve.deleteInstances( c3 )


breve.Test = Test


class CustomObject(breve.Stationary ):
	def __init__( self ):
		breve.Stationary.__init__( self )
		self.shape = None
		self.lastScale = 1
		self.energy = 1

		self.pushInterpreter = None
		self.pushCode = None
		self.createPush()


		CustomObject.init( self )

	def createPush(self):
		self.pushInterpreter = breve.createInstances( breve.PushInterpreter, 1 )
		self.pushInterpreter.readConfig( 'pushConfigFile.config' )
		self.pushInterpreter.addInstruction( self, 'separation' )
		self.pushInterpreter.addInstruction( self, 'alignment' )
		self.pushInterpreter.addInstruction( self, 'cohesion' )
		self.pushInterpreter.setEvaluationLimit( 50 )
		self.pushInterpreter.setListLimit( 50 )
		self.pushCode = breve.createInstances( breve.PushProgram, 1 )
		self.pushCode.makeRandomCode( self.pushInterpreter, 30 )

	def separation(self):
		self.pushInterpreter.pushVector( breve.vector(1,1,1) )

	def alignment(self):
		self.pushInterpreter.pushVector( breve.vector(2,2,2) )

	def cohesion(self):
		self.pushInterpreter.pushVector( breve.vector(3,3,3) )

	def adjustSize( self ):
		newScale = ( ( (self.energy+0.5) * 10 ) + 0.500000 )
		self.shape.scale( breve.vector( ( newScale / self.lastScale ), 1, ( newScale / self.lastScale ) ) )
		self.lastScale = newScale

	def init( self ):
		self.shape = breve.createInstances( breve.myCustomShape, 1 )
		self.setShape( self.shape )
		self.adjustSize()


breve.CustomObject = CustomObject


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


Test()