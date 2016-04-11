import breve

class Test( breve.Control ):
	def __init__( self ):
		breve.Control.__init__( self )

		self.object1 = None

		Test.init( self )

	def init( self ):
		self.setBackgroundColor( breve.vector( 0, 0, 0 ) )
		self.setDisplayTextColor( breve.vector( 1, 1, 1 ) )
		self.setIterationStep(1.0)

		self.object1 = breve.createInstances( breve.CustomObject, 1)

		print self.object1.pushInterpreter.getVectorStackTop()
		
		# initialization
		geno = ['function1', 'function2', 'POINT.+']
		self.object1.pushInterpreter.clearStacks()
		self.object1.pushCode.setFrom(geno)

		# first run
		self.object1.pushInterpreter.clearStacks()
		print self.object1.pushCode.getList()
		print self.object1.pushInterpreter.run( self.object1.pushCode )
		print self.object1.pushInterpreter.getVectorStackTop()


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
		self.pushInterpreter.addInstruction( self, 'function1' )
		self.pushInterpreter.addInstruction( self, 'function2' )
		self.pushInterpreter.setEvaluationLimit( 50 )
		self.pushInterpreter.setListLimit( 50 )
		self.pushCode = breve.createInstances( breve.PushProgram, 1 )

		self.pushCode.makeRandomCode( self.pushInterpreter, 30 )

	def function1(self):
		print 'function1'
		self.pushInterpreter.pushVector( breve.vector(1,1,1) )

	def function2(self):
		print 'function2'
		self.pushInterpreter.pushVector( breve.vector(1,2,3) )

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