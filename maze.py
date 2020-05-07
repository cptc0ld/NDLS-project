import random
import operator
import itertools
# Cretes a random maze, finds the soluton and prints it in different styles

# The print formats and the seed generation

# The maze generating algorithm creates a random spanning tree of a grid graph using Kruskal's algorithm

N = (-1, 0)
W = (0, -1)
S = (1, 0)
E = (0, 1)

DIRS = (N, E, S, W)
SIZEX = 20
SIZEY = 15
FIELDS = frozenset(itertools.product(range(SIZEX), range(SIZEY)))
parentMap = {}

characterMap = {
    #North, East,  South, West
	(True,  True,  True,  True):  chr(16),
	(True,  True,  True,  False): chr(25),
	(True,  True,  False, True):  chr(21),
	(True,  True,  False, False): chr(3),
	(True,  False, True,  True):  chr(23),
	(True,  False, True,  False): chr(5),
	(True,  False, False, True):  chr(4),
	(True,  False, False, False): chr(21),  #missing
	(False, True,  True,  True):  chr(22),
	(False, True,  True,  False): " ",      #missing
	(False, True,  False, True):  chr(6),
	(False, True,  False, False): chr(25),  #missing
    (False, False, True,  True):  chr(2),
	(False, False, True,  False): chr(22),  #missing
	(False, False, False, True):  chr(23),  #missing
	(False, False, False, False): " "
}

#--------------------------------------
# This is the part where the disjoint-set data structure is implemented:
def getParent(node):
  return parentMap.get(node, node)

def setParent(node, parent):
  parentMap[node] = parent

def find(node):
  if getParent(node) == node:
    return node
  else:
    result = find(getParent(node))
    setParent(node, result)
    return result
    
def union(nodeX, nodeY):
  roots = [find(nodeX), find(nodeY)]
  if roots[0] != roots[1]:
    random.shuffle(roots)
    setParent(roots[0], roots[1])

def isAlreadyConnected(nodeX, nodeY):
  return find(nodeX) == find(nodeY)

#---------------------------------------
# Some functions that are required to handle the graph

def addTuples(v1, v2):
  return tuple(map(operator.add, v1, v2))

def createEdge(v1, v2):
  return frozenset({v1, v2})

def getAllEdges():
  return {edge for edges in map(getIncidentalEdges, FIELDS) for edge in edges}
        
def getIncidentalEdges(field):
  neighbors = getNeighbors(field)
  return map(lambda neighbor: createEdge(neighbor, field), neighbors)

def isInside(field):
  return field in FIELDS

def getNeighbors(field):
  return filter(isInside, map(lambda direction: addTuples(field, direction), DIRS))

def isNodeConnectedTo(node, direction, edges):
  neighbor = addTuples(node, direction)
  edge = createEdge(node, neighbor)
  return edge in edges
  
#----------------------------------------
# This part generates the maze itself

def generateMazeEdges(edgeList):
  entranceEdge = ((0, -1), (0, 0))
  exitEdge = ((SIZEX - 1, SIZEY - 1), (SIZEX - 1, SIZEY))
  mazeEdges = {entranceEdge, exitEdge}
  for edge in edgeList:
    node1, node2 = edge
    if not isAlreadyConnected(node1, node2):
      union(node1, node2)
      mazeEdges |= {edge}
  return mazeEdges
  
# Methods for finding the solution
def addEdgeToDict(start, end, dictionary):
  if (start in dictionary):
    dictionary[start].append(end)
  else:
    dictionary[start] = [end]
 
def getConnectionMap(edges):
  result = {}
  for edge in edges:
    start, end = edge
    addEdgeToDict(start, end, result)
    addEdgeToDict(end, start, result)
  return result
      
def backTracePath(start, previousFieldMap):
  current = start
  result = []
  while (current != previousFieldMap[current]):
    result.append(current)
    current = previousFieldMap[current]
  result.append(current)
  return result
      
# Find a path from (0, -1) to (SIZEX - 1, SIZEY) and return the list of coordinates that 
# belong to the path
def findPath(mazeEdges):
  start = (0, -1)
  end = (SIZEX - 1, SIZEY)
  previousFieldDict = {end: end}
  connectionMap = getConnectionMap(mazeEdges)
  queue = [end]
  while len(queue) > 0:
    current = queue.pop(0)
    neighbors = connectionMap[current]
    
    # unvisitedNeighbors = list(filter(lambda neighbor: neighbor not in previousFieldDict, neighbors))
    unvisitedNeighbors = [neighbor for neighbor in neighbors if neighbor not in previousFieldDict]
    unvisitedNeighborsDict = {neighbor: current for neighbor in unvisitedNeighbors}
    
    previousFieldDict.update(unvisitedNeighborsDict)
    queue.extend(unvisitedNeighbors)
  if (start in previousFieldDict):
    return backTracePath(start, previousFieldDict)
  else:
    return None

#----------------------------------------
# stringArts are functions that when given an (x, y) tuple return a string 
# (usually a single character) that should be printed at (x, y) coordinates

# Only some of the methods defined here are actually used to print the mazes


TRANSPARENT = ""

def spaceToTransparent(char):
  return TRANSPARENT if char == " " else char

def createEmpty():
  """
    Creates an empty StringArt
  """
  return lambda coord: TRANSPARENT

def create(string):
  """
    Creates a StringArt from a string
  """
  lines = string.split("\n")
  def result(coord):
    x, y = coord
    if 0 <= x < len(lines):
      if 0 <= y < len(lines[x]):
        return spaceToTransparent(lines[x][y])
    return TRANSPARENT  
  return result
    
def translate(stringArt, vect):
  """
    Translates a StringArt to a different position
  """
  return lambda coord: stringArt((coord[0] - vect[0], coord[1] - vect[1]))

def transpose(stringArt):
  """
     Transposes a StringArt by switching x and y coordinates
  """
  return lambda coord: stringArt(coord[::-1])
  
def invertCentral(stringArt):
  """
     Inverts a stringArt centrally
  """
  return lambda coord: stringArt((-coord[0], -coord[1]))
  
def reflectHorizontally(stringArt):
  """
     Reflects a stringArt horizontally
  """
  return lambda coord: stringArt((coord[0], -coord[1]))

def reflectVertically(stringArt):
  """
     Reflects a stringArt vertically
  """
  return lambda coord: stringArt((-coord[0], coord[1]))

def stringArtUnion(stringArts):
  """
    Takes a list of StringArts and returns a stringArt that
    returns the first non-transparent value
  """
  def result(coord):
    x, y = coord
    for art in stringArts:
      if art(coord) != TRANSPARENT:
        return art(coord)
    return TRANSPARENT
  return result
  
def compose(stringArt, func):
  """
    Applies a string->string function to a stringArt.
  """
  return lambda coord: func(stringArt(coord))

def frameArt(art, dimension):
  """
    
  """
  sizeX, sizeY = dimension
  xRange = range(sizeX)
  yRange = range(sizeY)
  def result(coord):
    x, y = coord
    if (x not in xRange) or (y not in yRange):
      return TRANSPARENT
    return art(coord)
  return result
  
def window(art, dimension):
  """
    Creates a window around a StringArt of size sizeX x sizeY
    Example:
     art = abcd111
           efgh222
           ijkl333
           mnop444
     then window(art, 5, 4) =
           +--+
           |ab|
           |ef|
           |ij|
           +--+
  """
  sizeX, sizeY = dimension
  xRange = range(sizeX)
  yRange = range(sizeY)
  xInside = range(1, sizeX - 1)
  yInside = range(1, sizeY - 1)
  def result(coord):
    x, y = coord
    if (x not in xRange) or (y not in yRange):
      return TRANSPARENT
    if (x not in xInside) and (y not in yInside):
      return "+"
    if x not in xInside:
      return "-"
    if y not in yInside:
      return "|"
    return translate(art, (1, 1))(coord)
  return result

#-------------------------------------
# Methods that are responsible for displaying StringArts

def resolveChar(char):
  """
    Resolves a character from a StringArt into a printable format
  """
  return  " " if char == TRANSPARENT else char

def printArt(stringArt, dimension):
  """
    Prints a StringArt in a rectangle of sizeX x sizeY
  """
  sizeX, sizeY = dimension
  for i in range(sizeX):
    line = "".join([resolveChar(stringArt((i, j))) for j in range(sizeY)])
    print(line)


#--------------------------------------
# Methods that are responsible for creating a stringArt that represents a maze

def getWallSymbol(x, y, edges):
  leftNeighbor = (x, y)
  rightNeighbor = (x, y + 1)
  isVerticalLine = not isNodeConnectedTo(leftNeighbor, E, edges)
  isHorizontalLine = not isNodeConnectedTo(leftNeighbor, S, edges) and not isNodeConnectedTo(rightNeighbor, S, edges)
  return "|" if isVerticalLine else "_" if isHorizontalLine else " "

def getFieldSymbol(x, y, edges):
  thisField = (x, y)
  vertical = not isNodeConnectedTo(thisField, S, edges)
  return "_" if vertical else " "

def getSymbol(row, column, edges):
  x = row
  y = column // 2
  wall = column % 2 == 0
  return getWallSymbol(x, y - 1, edges) if wall else getFieldSymbol(x, y, edges)

def createMazeArt(edges):
  def result(coord):
    row, column = coord
    if row == 0:
      return "_"
    return getSymbol(row - 1, column, edges)
  return result

def getMazeSymbolStyle2(row, column, edges):
  isField = row % 2 == 1 and column % 2 == 1
  isVertWall = row % 2 == 0 and column % 2 == 1
  isHorWall = row % 2 == 1 and column % 2 == 0
  EMPTY = TRANSPARENT
  OCCUPIED = "#"
  if isField:
    return EMPTY
  if isVertWall:
    leftNeighbor = (row // 2 - 1, column // 2)
    rightNeighbor = (row // 2, column // 2)
    if createEdge(leftNeighbor, rightNeighbor) in edges:
      return EMPTY
    return OCCUPIED
  if isHorWall:
    upNeighbor = (row // 2, column // 2 - 1)
    downNeighbor = (row // 2, column // 2)
    if createEdge(upNeighbor, downNeighbor) in edges:
      return EMPTY
    return OCCUPIED
  return OCCUPIED

def createMazeArtStyle2(edges):
  def result(coord):
    row, column = coord
    return getMazeSymbolStyle2(row, column, edges)
  return result

def createPathArtStyle2(path):
  PATH = "."
  EMPTY = TRANSPARENT
  def result(coord):
    row, column = coord
    isField = row % 2 == 1 and column % 2 == 1
    isVertWall = row % 2 == 0 and column % 2 == 1
    isHorWall = row % 2 == 1 and column % 2 == 0
    if isField:
      field = (row // 2, column // 2)
      return PATH if field in path else EMPTY
    if isVertWall:
      leftNeighbor = (row // 2 - 1, column // 2)
      rightNeighbor = (row // 2, column // 2)
      return PATH if leftNeighbor in path and rightNeighbor in path else EMPTY
    if isHorWall:
      upNeighbor = (row // 2, column // 2 - 1)
      downNeighbor = (row // 2, column // 2)
      return PATH if upNeighbor in path and downNeighbor in path else EMPTY
    return EMPTY
  return result

def createMazeArtStyle3(edges):
  def result(coord):
    row, column = coord
    return getMazeSymbolStyle3(row, column, edges)
  return result

def getMazeSymbolStyle3(row, column, edges):
  northWestField = (row - 1, column - 1)
  northEastField = (row - 1, column)
  southWestField = (row,     column - 1)
  southEastField = (row,     column)
  westEdge = createEdge(northWestField, southWestField)
  eastEdge = createEdge(northEastField, southEastField)
  northEdge = createEdge(northWestField, northEastField)
  southEdge = createEdge(southWestField, southEastField)
  westWallExists = westEdge not in edges
  eastWallExists = eastEdge not in edges
  northWallExists = northEdge not in edges
  southWallExists = southEdge not in edges
  return characterMap.get((northWallExists, eastWallExists,
                           southWallExists, westWallExists), " ")

def printMaze(sizeX, sizeY, mazeEdges):
  art = createMazeArt(mazeEdges)
  printArt(art, (sizeX + 1, 2 * sizeY + 1))

def printMazeStyle2(sizeX, sizeY, mazeEdges, path):
  art = frameArt(stringArtUnion([createMazeArtStyle2(mazeEdges), createPathArtStyle2(path)]), (2 * sizeX + 1, 2 * sizeY + 1))
  printArt(art, (2 * sizeX + 1, 2 * sizeY + 1))

  # Hidden feature: Add some transformations to the maze
  # Transpose
  print("Same maze, transposed:")
  printArt(transpose(art), (2 * sizeY + 1, 2 * sizeX + 1))
  
  # Inverted
  #printArt(translate(invertCentral(art), (2 * sizeX, 2 * sizeY)), (2 * sizeX + 1, 2 * sizeY + 1))
  
  # Reflect 
  #printArt(translate(reflectVertically(art), (2 * sizeX, 0)), (2 * sizeX + 1, 2 * sizeY + 1))
  
  # Maze and reflection together
  #printArt(stringArtUnion([art,translate(reflectHorizontally(art), (0, 4 * sizeY))]), (2 * sizeX + 1, 4 * sizeY + 1))

def printMazeStyle3(sizeX, sizeY, mazeEdges):
  art = createMazeArtStyle3(mazeEdges)
  printArt(art, (sizeX + 1, sizeY + 1))
  

#------------------------------------
# The main method

def main():
  EDGESET = getAllEdges()
  edgeList = list(EDGESET)
  random.shuffle(edgeList)
  mazeEdges = generateMazeEdges(edgeList)
  path = findPath(mazeEdges)
  print("First style, without solution:")
  printMaze(SIZEX, SIZEY, mazeEdges)
  print("\nSecond style, with solution:")
  printMazeStyle2(SIZEX, SIZEY, mazeEdges, path)
  # Hidden feature: Third, experimental style - it's not 100% valid and does not look good
  # on every device :(
  #printMazeStyle3(SIZEX, SIZEY, mazeEdges)
  

seed = random.randint(0, 1000)
random.seed(seed)
print("Maze size: " + str(SIZEX) + "x" + str(SIZEY)) 
main()

