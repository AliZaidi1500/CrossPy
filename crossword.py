from sys import argv, exit
from getopt import getopt, GetoptError

# Constant variables
GRID_SIZE = 20 # Grid size for rows and columns
GRID_CHAR = ' ' # Character to fill blanks in the grid
ERRORS = [
	'No intersections',
	'Illegal adjacencies',
	'Out of bounds'
] # List containing error strings

def main():
	debug = False
	usage = f'{argv[0]} <words>'
	try:
		opts, args = getopt(argv[1:],'hd',['debug'])
	except GetoptError:
		print(usage)
		exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print(usage)
			exit()
		elif opt in ('-d', '--debug'):
			debug = True
	if (not debug and len(argv) > 1) or (debug and len(argv) > 2):
		crossword(argv[(2 if debug else 1):], debug)
	else:
		print(usage)

def crossword(L: list, debug: bool) -> None:
	"""
	Function to generate a crossword puzzle

	Generates a crossword puzzle with the given words

	Parameters:
		L (list): List of strings representing words
	"""
	
	# Keep executing code until changeOccured is False
	# When changeOccured is False then words can't be added anymore
	grid = [[GRID_CHAR] * GRID_SIZE for row in range(GRID_SIZE)]
	changeOccured = True # Variable to keep of grid changes
	while changeOccured:

		wordERRORS = [] # List to hold word ERRORS as tuples: (word, error)
		wordInserted = False # Helper variable for changeOccured
		C = L.copy() # Copy list so iteration is not affected once a word is removed from the original list
		for index, word in enumerate(C):
			wordError = None # Variable to keep track of word error
			rowStartIndex = None # Start index for horizontal placement
			columnStartIndex = None # Start index for vertical placement
			placementFound = False # Variable to track if a valid placement has been found

			# First word placement
			# If the grid is empty then the current word is the first word
			if isGridEmpty(grid):
				rowIndex = (len(grid) // 2) - 1 # Middle row index of the grid
				columnStartIndex = ((len(grid[rowIndex]) - len(word)) // 2) # Column index for word placement in the middle
				columnEndIndex = columnStartIndex + len(word) - 1
				if not boundCheck(columnStartIndex, columnEndIndex):
					wordError = ERRORS[2]
				else:
					placementFound = True
			else:
				# Determine intersections
				intersections = [] # List to keep track of possible intersections
				for row, cells in enumerate(grid):
					for column, cell in enumerate(cells):
						if cell in word:
							intersections.append((row, column))
				horizontalIntersections = groupIntersections(intersections, 0) # Group horizontal intersections
				verticalIntersections = groupIntersections(intersections, 1) # Group vertical intersections

				if not intersections:
					wordError = ERRORS[0]

				# Find valid placement
				for row, column in intersections:
					cell = grid[row][column]
					occurences = [index for index, alpha in enumerate(word) if alpha == cell] # Get all possible variations of word placement

					for occurence in occurences:
						# Horizontal check
						rowIndex = row
						columnStartIndex = column - occurence
						columnEndIndex = column + len(word) - occurence - 1
						check, wordError = horizontalCheck(grid, word, columnStartIndex, columnEndIndex, rowIndex, [column for row, column in horizontalIntersections[rowIndex]])
						if check:
							placementFound = True
							break
						columnStartIndex = None

						# Vertical check
						columnIndex = column
						rowStartIndex = row - occurence
						rowEndIndex = row + len(word) - occurence - 1
						check, wordError = verticalCheck(grid, word, rowStartIndex, rowEndIndex, columnIndex, [row for row, column in verticalIntersections[columnIndex]])
						if check:
							placementFound = True
							break
						rowStartIndex = None

					if placementFound: break # Break placement loop once a valid placement has been found

			# Word insertion
			if placementFound:
				for index, alpha in enumerate(word):
					# Horizontal insertion
					if columnStartIndex is not None:
						grid[rowIndex][columnStartIndex + index] = alpha
					# Vertical insertion
					else:
						grid[rowStartIndex + index][columnIndex] = alpha
				L.remove(word) # Remove word from list once its added
				wordInserted = True
			# Add word error to word ERRORS list
			else:
				wordERRORS.append((word, wordError))

		# If a word is inserted then a change has occured therefore the code needs to execute again with the new set of possibilites for the remaining words
		# Otherwise a change has not occured if a word hasn't been inserted and the code doesn't need to execute again
		changeOccured = wordInserted
	
	if debug and wordERRORS:
		print('WORD ERRORS')
		wordSpacing = len(max((word for word, error in wordERRORS), key=len))
		print('\n'.join(('{:>{}}: {}'.format(word, wordSpacing, error) for word, error in wordERRORS)))
	printGrid(grid)

def printGrid(grid: list) -> None:
	"""
	Function to print grid

	Prints the given grid with evenly spaced
	characters and a border around the grid

	Parameters:
		grid (list): 2D list representing a grid
	"""
	print('-' * ((GRID_SIZE * 2) + 1))
	print('\n'.join((f'|{" ".join(row)}|' for row in grid)))
	print('-' * ((GRID_SIZE * 2) + 1))

def lineCheck(line: list) -> bool:
	"""
	Function to check if line is empty

	Checks if a given line on grid is empty

	Parameters:
		line (list): List representing a vertical
					 or horizontal line on grid

	Returns:
		boolean: True if line is empty otherwise False
	"""
	return all(char == GRID_CHAR for char in line)

def isGridEmpty(grid: list) -> bool:
	"""
	Function to check if grid is empty

	Checks if the given grid is empty

	Parameters:
		grid (list): 2D list representing a grid

	Returns:
		boolean: True if grid is empty otherwise False
	"""
	return all([lineCheck(row) for row in grid])

def boundCheck(startIndex: int, endIndex: int) -> bool:
	"""
	Function to check if indexes are out of bounds

	Checks if the given start and end index are out of bounds

	Parameters:
		startIndex (int): Index on grid for the first
						  character of the word
		endIndex (int): Index on grid for the last
						character of the word

	Returns:
		boolean: True if indexes are within bounds otherwise False
	"""
	return startIndex >= 0 and endIndex < GRID_SIZE

def groupIntersections(intersections: list, key: int) -> dict:
	"""
	Function to group horizontal or vertical intersections

	Groups horizontal or vertical intersections
	as a list into a dict by the given key

	Parameters:
		intersections (list): List of tuples representing
							  intersection points
		key (int): Tuple index to group by
				   (0 for rows and 1 for columns)

	Returns:
		dict: Lists of intersections as values grouped by key
	"""
	groupedIntersections = {}

	for intersection in intersections:
		keyValue = intersection[key]
		if keyValue not in groupedIntersections.keys():
			groupedIntersections[keyValue] = []
		group = groupedIntersections[keyValue]
		group.append(intersection)
	
	return groupedIntersections

def verticalCheck(grid: list, word: str, rowStartIndex: int, rowEndIndex: int, column: int, intersectionRows: list) -> bool: 
	"""
	Function to check if word can be placed vertically

	Checks if the given word can legally be
	placed vertically at the given start index

	Parameters:
		grid (list): 2D list representing a grid
		word (string): String representing the word
		rowStartIndex (int): Row index for the first
							 character of the word
		rowEndIndex (int): Row index for the last
						   character of the word
		column (int): Column index for vertical placement
		intersectionRows (list): List of integers representing
								 valid rows of intersection

	Returns:
		boolean: True if placement is legal otherwise False
		string: Error string if illegal placement otherwise None
	"""
	if not boundCheck(rowStartIndex, rowEndIndex):
		return False, ERRORS[2] # Return False if word is out of grid bounds
	
	leftColumn = [] # List to keep track of grid characters on the left side of the word
	rightColumn = [] # List to keep track of grid characters on the right side of the word
	middleColumn = [] # List to keep track of grid characters on the column of the word
	startIndex = rowStartIndex-1 if rowStartIndex != 0 else rowStartIndex
	endIndex = rowEndIndex+1 if rowEndIndex != len(grid)-1 else rowEndIndex
	for row, cells in enumerate(grid[startIndex:endIndex+1]):
		gridRow = startIndex + row
		if gridRow != rowStartIndex-1 and gridRow != rowEndIndex+1:
			if gridRow not in intersectionRows:
				middleColumn.append(cells[column])
				if column != 0:
					leftColumn.append(cells[column-1])
				if column != GRID_SIZE-1:
					rightColumn.append(cells[column+1])
			else:
				if cells[column] != word[row - (1 if startIndex != rowStartIndex else 0)]:
					middleColumn.append(cells[column])
		else:
			middleColumn.append(cells[column])

	# Check if at least one cell is a blank to avoid overlapping with duplicates
	GRID_CHARCheck = any([cell == GRID_CHAR for cell in middleColumn[1 if startIndex != rowStartIndex else None:-1 if endIndex != rowEndIndex else None]])
	linesCheck = lineCheck(leftColumn) and lineCheck(rightColumn) and lineCheck(middleColumn) and GRID_CHARCheck
	return linesCheck, None if linesCheck else ERRORS[1]

def horizontalCheck(grid: list, word: str, columnStartIndex: int, columnEndIndex: int, row: int, intersectionColumns: list) -> bool:
	"""
	Function to check if word can be placed horizontaly

	Checks if the given word can validly be placed
	horizontally at the given start index

	Parameters:
		grid (list): 2D list representing a grid
		word (string): String representing the word
		columnStartIndex (int): column index for the first
								character of the word
		columnEndIndex (int): column index for the last
							  character of the word
		row (int): row index for horizontal placement
		intersectionColumns (list): list of integers representing
									valid columns of intersection

	Returns:
		boolean: True if placement is legal otherwise False
		string: Error string if illegal placement otherwise None
	"""
	if not boundCheck(columnStartIndex, columnEndIndex):
		return False, ERRORS[2] # Return False if word is out of grid bounds
	
	topRow = [] # List to keep track of grid characters above the word
	middleRow = [] # List to keep track of grid characters on the row of the word
	bottomRow = [] # List to keep trach of grid characters below the word
	startIndex = columnStartIndex-1 if columnStartIndex else 0
	endIndex = columnEndIndex+1 if columnEndIndex != len(grid[0])-1 else columnEndIndex
	for column in range(startIndex, endIndex+1):
		if column != columnStartIndex-1 and column != columnEndIndex+1:
			if column not in intersectionColumns:
				middleRow.append(grid[row][column])
				if row != 0:
					topRow.append(grid[row-1][column])
				if row != GRID_SIZE-1:
					bottomRow.append(grid[row+1][column])
			else:
				if grid[row][column] != word[column - columnStartIndex]:
					middleRow.append(grid[row][column])
		else:
			middleRow.append(grid[row][column])
	
	# Check if at least one cell is a blank to avoid overlapping with duplicates
	GRID_CHARCheck = any([cell == GRID_CHAR for cell in middleRow[1 if startIndex != columnStartIndex else None:-1 if endIndex != columnEndIndex else None]])
	linesCheck =  lineCheck(topRow) and lineCheck(middleRow) and lineCheck(bottomRow) and GRID_CHARCheck
	return linesCheck, None if linesCheck else ERRORS[1]

if __name__ == '__main__':
	main()
