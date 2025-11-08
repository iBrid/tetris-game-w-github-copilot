import copy

# Tetromino definitions as 4x4 grids (lists of lists). 1 indicates a block cell.
SHAPES = {
    'I': [[0,0,0,0],
          [1,1,1,1],
          [0,0,0,0],
          [0,0,0,0]],
    'O': [[0,1,1,0],
          [0,1,1,0],
          [0,0,0,0],
          [0,0,0,0]],
    'T': [[0,1,0,0],
          [1,1,1,0],
          [0,0,0,0],
          [0,0,0,0]],
    'S': [[0,1,1,0],
          [1,1,0,0],
          [0,0,0,0],
          [0,0,0,0]],
    'Z': [[1,1,0,0],
          [0,1,1,0],
          [0,0,0,0],
          [0,0,0,0]],
    'J': [[1,0,0,0],
          [1,1,1,0],
          [0,0,0,0],
          [0,0,0,0]],
    'L': [[0,0,1,0],
          [1,1,1,0],
          [0,0,0,0],
          [0,0,0,0]],
}

# Simple colors for shapes (RGB tuples)
COLORS = {
    'I': (0, 240, 240),
    'O': (240, 240, 0),
    'T': (160, 0, 240),
    'S': (0, 240, 0),
    'Z': (240, 0, 0),
    'J': (0, 0, 240),
    'L': (240, 160, 0),
}

def rotate_shape(shape):
    """Rotate a 2D square matrix (list of lists) 90 degrees clockwise.

    Input is a 4x4 (or NxN) nested list; this returns a new rotated matrix.
    """
    # transpose then reverse rows
    n = len(shape)
    new = [[0]*n for _ in range(n)]
    for r in range(n):
        for c in range(n):
            new[c][n-1-r] = shape[r][c]
    return new

def shape_cells(shape_matrix, offset_x=0, offset_y=0):
    """Yield (x,y) positions of occupied cells from a shape matrix with offsets."""
    positions = []
    for r, row in enumerate(shape_matrix):
        for c, val in enumerate(row):
            if val:
                positions.append((c + offset_x, r + offset_y))
    return positions

def clone_shape(name):
    return copy.deepcopy(SHAPES[name])
