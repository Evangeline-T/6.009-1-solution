#!/usr/bin/env python3
"""6.009 Lab -- Six Double-Oh Mines"""

# NO IMPORTS ALLOWED!

def dump(game):
    """
    Prints a human-readable version of a game (provided as a dictionary)
    """
    for key, val in sorted(game.items()):
        if isinstance(val, list) and val and isinstance(val[0], list):
            print(f'{key}:')
            for inner in val:
                print(f'    {inner}')
        else:
            print(f'{key}:', val)


# 2-D IMPLEMENTATION

def new_game_2d(num_rows, num_cols, bombs):
    """
    Start a new game.

    Return a game state dictionary, with the 'dimensions', 'state', 'board' and
    'mask' fields adequately initialized.

    Parameters:
       num_rows (int): Number of rows
       num_cols (int): Number of columns
       bombs (list): List of bombs, given in (row, column) pairs, which are
                     tuples

    Returns:
       A game state dictionary

    >>> dump(new_game_2d(2, 4, [(0, 0), (1, 0), (1, 1)]))
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: (2, 4)
    mask:
        [False, False, False, False]
        [False, False, False, False]
    state: ongoing
    """
    return new_game_nd((num_rows, num_cols), bombs)

def dig_2d(game, row, column):
    """
    Reveal the cell at (row, col), and, in some cases, recursively reveal its
    neighboring squares.

    Update game['mask'] to reveal (row, col).  Then, if (row, col) has no
    adjacent bombs (including diagonally), then recursively reveal (dig up) its
    eight neighbors.  Return an integer indicating how many new squares were
    revealed in total, including neighbors, and neighbors of neighbors, and so
    on.

    The state of the game should be changed to 'defeat' when at least one bomb
    is visible on the board after digging (i.e. game['mask'][bomb_location] ==
    True), 'victory' when all safe squares (squares that do not contain a bomb)
    and no bombs are visible, and 'ongoing' otherwise.

    Parameters:
       game (dict): Game state
       row (int): Where to start digging (row)
       col (int): Where to start digging (col)

    Returns:
       int: the number of new squares revealed

    >>> game = {'dimensions': (2, 4),
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'mask': [[False, True, False, False],
    ...                  [False, False, False, False]],
    ...         'state': 'ongoing'}
    >>> dig_2d(game, 0, 3)
    4
    >>> dump(game)
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: (2, 4)
    mask:
        [False, True, True, True]
        [False, False, True, True]
    state: victory

    >>> game = {'dimensions': [2, 4],
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'mask': [[False, True, False, False],
    ...                  [False, False, False, False]],
    ...         'state': 'ongoing'}
    >>> dig_2d(game, 0, 0)
    1
    >>> dump(game)
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: [2, 4]
    mask:
        [True, True, False, False]
        [False, False, False, False]
    state: defeat
    """

    return dig_nd(game, (row, column))


def render_2d(game, xray=False):
    """
    Prepare a game for display.

    Returns a two-dimensional array (list of lists) of '_' (hidden squares), '.'
    (bombs), ' ' (empty squares), or '1', '2', etc. (squares neighboring bombs).
    game['mask'] indicates which squares should be visible.  If xray is True (the
    default is False), game['mask'] is ignored and all cells are shown.

    Parameters:
       game (dict): Game state
       xray (bool): Whether to reveal all tiles or just the ones allowed by
                    game['mask']

    Returns:
       A 2D array (list of lists)

    >>> render_2d({'dimensions': (2, 4),
    ...         'state': 'ongoing',
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'mask':  [[False, True, True, False],
    ...                   [False, False, True, False]]}, False)
    [['_', '3', '1', '_'], ['_', '_', '1', '_']]

    >>> render_2d({'dimensions': (2, 4),
    ...         'state': 'ongoing',
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'mask':  [[False, True, False, True],
    ...                   [False, False, False, True]]}, True)
    [['.', '3', '1', ' '], ['.', '.', '1', ' ']]
    """
    
    return render_nd(game, xray)

def render_ascii(game, xray=False):
    """
    Render a game as ASCII art.

    Returns a string-based representation of argument 'game'.  Each tile of the
    game board should be rendered as in the function 'render_2d(game)'.

    Parameters:
       game (dict): Game state
       xray (bool): Whether to reveal all tiles or just the ones allowed by
                    game['mask']

    Returns:
       A string-based representation of game

    >>> print(render_ascii({'dimensions': (2, 4),
    ...                     'state': 'ongoing',
    ...                     'board': [['.', 3, 1, 0],
    ...                               ['.', '.', 1, 0]],
    ...                     'mask':  [[True, True, True, False],
    ...                               [False, False, True, False]]}))
    .31_
    __1_
    """
    # This is extremely simnilar to render 2d, except we just return a string with the elements revealed
    # as they were in render 2d.
    num_of_rows = game["dimensions"][0]
    num_of_columns = game["dimensions"][1]
    
    new_board = ""
    
    if xray:
        for r in range(num_of_rows):
            for c in range(num_of_columns):
                if game["board"][r][c] == 0:
                    new_board += " "
                else:
                    new_board += str(game["board"][r][c])
            if r!= num_of_rows - 1:
                new_board += "\n"  # Start a new line to go to the next row.
                    
    else:
        for r in range(num_of_rows):
            for c in range(num_of_columns):
                if game["mask"][r][c]:
                    if game["board"][r][c] == 0:
                        new_board += ' '
                    else:
                        new_board += str(game["board"][r][c])
                else:
                    new_board += '_'
            if r!= num_of_rows - 1:
                new_board += "\n"
            
    return new_board



# N-D IMPLEMENTATION


def empty_board(dimensions, depth, mask = False):
    """
    Parameters
    ----------
    dimensions : tuple 
        The dimension of this board and how many values in each dimension.
    depth : int
        The current diemsion we are on.
    mask : booean, optional
        If set to True, will build mask dictionary instead, all elements set to False.
        The default is False.

    Returns
    -------
    The board we are looking for.
    """
    dim_size = dimensions[depth]
    coordinate = []
    if mask:  # If mask is True, we build the mask information of the new game.
        if depth == len(dimensions) - 1:  # When we are at the last dimension, we can start filling it up with False.
            for i in range(dim_size):
                coordinate.append(False)
            return coordinate
        else:
            for i in range(dim_size):
                coordinate.append(empty_board(dimensions, depth + 1, mask = True))  # We recurse into the last dimension and fill the coordinate.
            return coordinate

    else:
        if depth == len(dimensions) - 1:
            for i in range(dim_size):
                coordinate.append(0)  # To build an empty board, this time we fill with 0s.
            return coordinate
        else:
            for i in range(dim_size):
                coordinate.append(empty_board(dimensions, depth + 1, mask = False))
            return coordinate
        
          
def find_neighbouring_coordinates(dimensions, coordinate, current_neighbouring_coordinate, list_of_coordinates, depth):  # We define another function for the recursion so the list of neighbouring coordinates does not get reset.
    """
    Parameters
    ----------
    dimensions : tuple 
        The dimension of this board and how many values in each dimension.
    coordinate : list
        The coordinate we are trying to find the neighbours of.
    curent_neighbouring_coordinate : tuple
        The current potential neighbouring coordinate.
    list_of_coordinates : set
        A list of the current neighbours of the given coordinate.
    depth : int
        How far into the coordinate's dimensions we are when trying to find it's neighbours.

    Returns
    -------
    None. This function is called by neighbouring_coordinates, and it mutates a set
    which is returned by neighbouring_coordinates.
    """
    if depth == len(dimensions):  # If we are at the last dimension and the current neighbour fits all the conditions, we know it is a neighbour.
        list_of_coordinates.add(tuple(current_neighbouring_coordinate))  # We use a tuple just to get rid of hashing errors.
        
    else:
        for x in range(-1, 2):
            new_coordinate = current_neighbouring_coordinate[:]
            if coordinate[depth] + x < 0 or coordinate[depth] + x > dimensions[depth] - 1:  # We check the coordinates that are 1 unit away in that dimension.
                continue
            new_coordinate.append(coordinate[depth] + x)  # We create the new coordinate that potentially neighbours the target one.
            find_neighbouring_coordinates(dimensions, coordinate, new_coordinate, list_of_coordinates, depth + 1)
        
        
def neighbouring_coordinates(dimensions, coordinate, depth, current_neighbouring_coordinate = []):
    """
    Parameters
    ----------
    dimensions : tuple
        The dimension of this board and how many values in each dimension..
    coordinate : list
        The coordinate we are trying to find the neighbours of..
    depth : int
        How far into the coordinate's dimensions we are when trying to find it's neighbours..
    current_neighbouring_coordinate : list, optional
        The current potential neighbouring coordinate. Initially is empty
        because we haven't started analysing yet. The default is [].

    Returns
    -------
    list_of_coordinates : set
        A set of all the neighbouring coordinates for the given one..
    """
    list_of_coordinates = set()
    find_neighbouring_coordinates(dimensions, coordinate, current_neighbouring_coordinate, list_of_coordinates, depth)
    return list_of_coordinates

def set_coordinate(board, coordinate, depth, bomb = False, mask = False, value = False, info = None):
    """
    Parameters
    ----------
    board : array
        The board of the game we are looking at.
    coordinate : list
        The coordinate we are changing.
    depth : How far into the dimensions of the coordinate we currently are.
        DESCRIPTION.
    bomb : bool, optional
        If set to true, we set the coordinate to a bomb. The default is False.
    mask : bool, optional
        If set to True, we set the coordinates mask value to True. The default is False.
    value : bool, optional
        If set to True, we set the coordinate equal to info.
    info : string
        The information that is associated with the coordinate if value is True.

    Returns
    -------
    TYPE
        DESCRIPTION.
    """
    if mask:
        if depth == len(coordinate) - 1:
            if board[coordinate[depth]]:
                return board[coordinate[depth]]
            else:
                board[coordinate[depth]] = True
                return board[coordinate[depth]]
        else:
            current_mask = board[coordinate[depth]]
            return set_coordinate(current_mask, coordinate, depth + 1, bomb, mask)
    else:
        if depth == len(coordinate) - 1:  # If we are at the right dimension and we are trying to add a bomb, then add a bomb to that coordinate.
            if bomb:
                board[coordinate[depth]] = '.'
            else:
                if type(board[coordinate[depth]]) != str and not value:  # Add 1 if are not trying to initialize bombs, we add 1 because this function is used to work out what number coordinates neighbouring bombs need.
                    board[coordinate[depth]] += 1
                elif value:  # If we are trying to augment the value of a coordinate, we do it here and set it to info.
                    board[coordinate[depth]] = info
        else:
            current_board = board[coordinate[depth]]  # We go to the next dimension in the bomb, and the corresponding dimension in the board.
            return set_coordinate(current_board, coordinate, depth + 1, bomb, mask, value, info)
        
def set_all_coordinates(dimensions, board, bombs):
    """
    Parameters
    ----------
    board : array
        The nd board we are working with.
    bombs : array
        Locations of the bombs in the board

    Returns
    -------
    Fills the game board with bombs, and fills the bombs' neighbours with the 
    appropriate number for how many bombs neighbour a valid coordinate.

    """
    for bomb in bombs:
        for coordinate in neighbouring_coordinates(dimensions, bomb, 0):  # Look at possible neighbouring coordinates of the bomb.
            if tuple(coordinate) in bombs:  # We don't need to change the value of any neighbouring bombs.
                continue
            set_coordinate(board, coordinate, 0)  # Add 1 to the valid neighbouring coordinates.
        set_coordinate(board, bomb, 0, bomb = True)  # Set the bomb itself to '.' by adding True.

def new_game_nd(dimensions, bombs):
    """
    Start a new game.

    Return a game state dictionary, with the 'dimensions', 'state', 'board' and
    'mask' fields adequately initialized.


    Args:
       dimensions (tuple): Dimensions of the board
       bombs (list): Bomb locations as a list of lists, each an
                     N-dimensional coordinate

    Returns:
       A game state dictionary

    >>> g = new_game_nd((2, 4, 2), [(0, 0, 1), (1, 0, 0), (1, 1, 1)])
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    mask:
        [[False, False], [False, False], [False, False], [False, False]]
        [[False, False], [False, False], [False, False], [False, False]]
    state: ongoing
    """
    empty_game_board = empty_board(dimensions, 0)
    mask = empty_board(dimensions, 0, mask = True)
    set_all_coordinates(dimensions, empty_game_board, bombs)
    game = {"board" : empty_game_board, "dimensions" : dimensions, "mask" : mask, "state" : 'ongoing'}
    return game

def check_coordinate(board, coordinate, depth):
    """
    Parameters
    ----------
    board : array
        The board of the game we are playing.
    coordinate : list
        The coordinate we are trying to get the number of.
    depth : TYPE
        DESCRIPTION.

    Returns
    -------
    The number of neighbouring bombs, or if the coordinate being checked is a bomb.
    """
    if depth == len(coordinate) - 1:
        return board[coordinate[depth]]  # We are just checking and returning what the coordinate information is.
    else:
        current_board = board[coordinate[depth]]  # We index into the next dimension to continue checking.
        return check_coordinate(current_board, coordinate, depth + 1)
    
def check_if_true(mask, coordinate, depth):
    """
    Parameters
    ----------
    mask : array
        A list of whether each coordinate in the board has been revealed or not.
    coordinate : list
        The coordinate we are looking at.
    depth : int
        How far we have gone into the dimension of the coordinate to find the correct
        piece of information.

    Returns
    -------
    True if that coordinate has been revealed, else returns False.
    """
    if depth == len(coordinate) - 1:
        if mask[coordinate[depth]]:  # Here we are checking if a coordinate has been seen before.
            return True
        else:
            return False
    else:
        current_mask = mask[coordinate[depth]]
        return check_if_true(current_mask, coordinate, depth + 1)
    
def reveal_number_of_nd_neighbours(game, coordinate):
    """
    Parameters
    ----------
    game : dictionary
        The current game being played.
    coordinate : list
        The coordinate we are digging up

    Returns
    -------
    The number of neighbours that are revealed when digging up this coordinate.
    """
    
    if check_coordinate(game["board"], coordinate, 0) != 0:  # If we select a coordinate that has neighbouring bombs, then we can only return 1 or 0.
        if check_if_true(game["mask"], coordinate, 0):  # If the coordinate has been seen before, return 0.
            return 0
        else:
            set_coordinate(game["mask"], coordinate, 0, bomb = False, mask = True)  # If the coordinate hasn't been seen, make it seen and add 1.  
            return 1
    else:
        revealed = set()
        for neighbouring_coordinate in neighbouring_coordinates(game["dimensions"], coordinate, 0):  # Chech the neighbours of the coordinate with no neighbouring bombs.
            if not check_if_true(game["mask"], neighbouring_coordinate, 0):  # Only check the neighbours if they haven't yet been seen.
                set_coordinate(game["mask"], neighbouring_coordinate, 0, bomb = False, mask = True)
                revealed.add(tuple(neighbouring_coordinate))
                
    current_number_of_revealed_coordinates = len(revealed)
    for coordinate in revealed:
        current_number_of_revealed_coordinates += reveal_number_of_nd_neighbours(game, coordinate)  # Recurse on the neighbours in case they are also not neighbouring any bombs.
    return current_number_of_revealed_coordinates

          
def find_all_coordinates(dimensions, depth, current_coordinate = [], list_of_coordinates = set()):  
    """
    Parameters
    ----------
    dimensions : tuple
        The dimensions of the all the coordinates we are creating.
    depth : int
        How far into the dimensions we currently are.
    current_coordinate : list, optional
        The current coordinates found in a dimension. The default is [].
    list_of_coordinates : set, optional
        The coordinates in the given dimensions. The default is set().

    Returns
    -------
    Nothing, just creates the list that is returned by the all_coordinates function.
    """
    if depth == len(dimensions):
        list_of_coordinates.add(tuple(current_coordinate))  
        
    else:
        for x in range(dimensions[depth]):
            new_coordinate = current_coordinate[:]
            new_coordinate.append(x)  # Get part of the coordinate for that dimension, then move to the next one to get the value from the next dimension.
            find_all_coordinates(dimensions, depth + 1, new_coordinate, list_of_coordinates)   # We recurse on the newly added piece from one dimension to get it's full coordinate, before going back to the beginning and getting the next piece from the first dimenson.
    
        
def all_coordinates(dimensions, depth, current_coordinate = []):
    """
    Parameters
    ----------
    dimensions : tuple
        The dimensions we are finding the coordinates of.
    depth : int
        How far into the dimensions we have currently gone.
    current_coordinate : list, optional
        The current coordinates in the current dimension we
        are in. The default is [].

    Returns
    -------
    list_of_coordinates : set
        A list of the coordinates in these dimensions..
    """
    list_of_coordinates = set()  
    find_all_coordinates(dimensions, depth, current_coordinate, list_of_coordinates)  # We define a function for the recursion so that the list doesn't get reset.
    return list_of_coordinates

def dig_nd(game, coordinates):
    """
    Recursively dig up square at coords and neighboring squares.

    Update the mask to reveal square at coords; then recursively reveal its
    neighbors, as long as coords does not contain and is not adjacent to a
    bomb.  Return a number indicating how many squares were revealed.  No
    action should be taken and 0 returned if the incoming state of the game
    is not 'ongoing'.

    The updated state is 'defeat' when at least one bomb is visible on the
    board after digging, 'victory' when all safe squares (squares that do
    not contain a bomb) and no bombs are visible, and 'ongoing' otherwise.

    Args:
       coordinates (tuple): Where to start digging

    Returns:
       int: number of squares revealed

    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'mask': [[[False, False], [False, True], [False, False], [False, False]],
    ...               [[False, False], [False, False], [False, False], [False, False]]],
    ...      'state': 'ongoing'}
    >>> dig_nd(g, (0, 3, 0))
    8
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    mask:
        [[False, False], [False, True], [True, True], [True, True]]
        [[False, False], [False, False], [True, True], [True, True]]
    state: ongoing
    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'mask': [[[False, False], [False, True], [False, False], [False, False]],
    ...               [[False, False], [False, False], [False, False], [False, False]]],
    ...      'state': 'ongoing'}
    >>> dig_nd(g, (0, 0, 1))
    1
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    mask:
        [[False, True], [False, True], [False, False], [False, False]]
        [[False, False], [False, False], [False, False], [False, False]]
    state: defeat
    """
    
    if game["state"] == "defeat" or game["state"] == "victory":  # The game is already over.
        return 0
    
    if check_coordinate(game["board"], coordinates, 0) == '.':
        set_coordinate(game["mask"], coordinates, 0, False, True)
        game["state"] = "defeat"  # If we land on a bomb, the game is over.
        return 1
    
    total_number_of_revealed_coordinates = reveal_number_of_nd_neighbours(game, coordinates)
    bombs = 0
    covered_squares = 0
    
    for coordinate in all_coordinates(game["dimensions"], 0):
        if check_coordinate(game["board"], coordinate, 0) == '.':
            bombs += 1
        if not check_if_true(game["mask"], coordinate, 0):
            covered_squares += 1
            
    the_truth = bombs == covered_squares  # If the number of covered squares is equal to the number of bombs, then we have revealed all the valid coordinates, and we are done.
    
    if the_truth:
        game['state'] = 'victory'
        return total_number_of_revealed_coordinates
    else:
        game['state'] = 'ongoing'
        return total_number_of_revealed_coordinates

def render_nd(game, xray=False):
    """
    Prepare the game for display.

    Returns an N-dimensional array (nested lists) of '_' (hidden squares),
    '.' (bombs), ' ' (empty squares), or '1', '2', etc. (squares
    neighboring bombs).  The mask indicates which squares should be
    visible.  If xray is True (the default is False), the mask is ignored
    and all cells are shown.

    Args:
       xray (bool): Whether to reveal all tiles or just the ones allowed by
                    the mask

    Returns:
       An n-dimensional array of strings (nested lists)

    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'mask': [[[False, False], [False, True], [True, True], [True, True]],
    ...               [[False, False], [False, False], [True, True], [True, True]]],
    ...      'state': 'ongoing'}
    >>> render_nd(g, False)
    [[['_', '_'], ['_', '3'], ['1', '1'], [' ', ' ']],
     [['_', '_'], ['_', '_'], ['1', '1'], [' ', ' ']]]

    >>> render_nd(g, True)
    [[['3', '.'], ['3', '3'], ['1', '1'], [' ', ' ']],
     [['.', '3'], ['3', '.'], ['1', '1'], [' ', ' ']]]
    """
    coordinates = all_coordinates(game['dimensions'], 0)
    new_board = empty_board(game['dimensions'], 0)
    
    for coordinate in coordinates:
        coordinate_info = check_coordinate(game['board'], coordinate, 0)  # We pull the info from the coordinate.
        if xray:
            if coordinate_info == 0:
                set_coordinate(new_board, coordinate, 0, value = True, info = " ")  # If the coordinate is 0, we add an empty string, as instructed.
            else:
                set_coordinate(new_board, coordinate, 0, value = True, info = str(coordinate_info))  # Else, we add the string of the coordinate.
        else:
            if check_if_true(game['mask'], coordinate, 0):  # We can only reveal information if it has been revealed prior.
                if coordinate_info == 0:
                    set_coordinate(new_board, coordinate, 0, value = True, info = " ")
                else:
                    set_coordinate(new_board, coordinate, 0, value = True, info = str(coordinate_info))
            else:
                set_coordinate(new_board, coordinate, 0, value = True, info = '_')  # We hide unrevealed information with this symbol.
    return new_board
                    

if __name__ == "__main__":
    # Test with doctests. Helpful to debug individual lab.py functions.
    import doctest
    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    doctest.testmod(optionflags=_doctest_flags) #runs ALL doctests

    # Alternatively, can run the doctests JUST for specified function/methods,
    # e.g., for render_2d or any other function you might want.  To do so, comment
    # out the above line, and uncomment the below line of code. This may be
    # useful as you write/debug individual doctests or functions.  Also, the
    # verbose flag can be set to True to see all test results, including those
    # that pass.
    #
    #doctest.run_docstring_examples(render_2d, globals(), optionflags=_doctest_flags, verbose=False)
