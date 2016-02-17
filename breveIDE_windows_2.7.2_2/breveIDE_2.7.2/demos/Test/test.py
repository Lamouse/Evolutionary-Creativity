import breve

class Test( breve.Control ):
	def __init__( self ):
		breve.Control.__init__( self )

		self.object = None 
		self.increm = 0.1

		Test.init( self )

	def init( self ):
		self.setBackgroundColor( breve.vector( 0, 0, 0 ) )
		self.setDisplayTextColor( breve.vector( 1, 1, 1 ) )
		self.setIterationStep(1.0)

		self.object = breve.createInstances( breve.CustomObject, 1)

	def iterate( self ):
		self.object.energy -= self.increm
		
		self.object.adjustSize()
		if self.increm != 0:
			print self.object.temp

		if 0 >= self.object.energy or self.object.energy >= 1:
			self.increm = 0
		

breve.Test = Test


class CustomObject(breve.Stationary ):
	def __init__( self ):
		breve.Stationary.__init__( self )
		self.shape = None
		self.lastScale = 1
		self.energy = 1
		self.temp = 1

		CustomObject.init( self )

	def adjustSize( self ):
		newScale = ( ( (self.energy+0.5) * 10 ) + 0.500000 )
		self.shape.scale( breve.vector( ( newScale / self.lastScale ), 1, ( newScale / self.lastScale ) ) )

		self.temp *= (newScale / self.lastScale)

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