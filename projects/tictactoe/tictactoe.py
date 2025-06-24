"""
Tic Tac Toe Player
"""

import math
import copy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    #Since X goes first, as long as EMPTY boxes are odd, its Xs turn
    count_empty = sum(cell is EMPTY for row in board for cell in row)
    return X if count_empty % 2 == 1 else O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    possible_moves = set()
    for row in range(len(board)):
        for cell in range(len(board[row])):
            if board[row][cell] == EMPTY:
                possible_moves.add((row,cell))
    return possible_moves


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    if (action[0] < 0) or ( action[0] > 2) or (action[1] < 0) or ( action[1] > 2):
        raise Exception("Out of Bounds")
    
    new_board = copy.deepcopy(board)
    if new_board[action[0]][action[1]] == EMPTY:
        new_board[action[0]][action[1]] = player(board)
    else:
        raise Exception("Invalid Input")
    
    return new_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    #Messy method, found better one during diagonal development
    #Left in for personal documentational purposes
    
    # #Horizontal Victory
    # for row in range(len(board)):
    #     x_count, o_count = 0, 0
    #     for cell in range(len(board[row])):
    #         if board[row][cell] == X:
    #             x_count +=1
    #         if board[row][cell] == O:
    #             o_count+=1
    #         if o_count == 3:
    #             return O
    #         if x_count == 3:
    #             return X
    #     x_count, o_count = 0, 0
    
    # #Vertical Victory
    # for col in range(len(board[0])):
    #     x_count, o_count = 0, 0
    #     for row in range(len(board)):
    #         if board[row][col] == X:
    #             x_count +=1
    #         if board[row][col] == O:
    #             o_count+=1
    #         if o_count == 3:
    #             return O
    #         if x_count == 3:
    #             return X
    #     x_count, o_count = 0, 0
    
    #Horizontal Vicotires
    for row in range(len(board)):
        if board[row][0] is not EMPTY:
            if board[row][0] == board[row][1] == board[row][2]:
                return board[row][0]
    
    #Vertical Vicotries
    for col in range(len(board[0])):
        if board[0][col] is not EMPTY:
            if board[0][col] == board[1][col] == board[2][col]:
                return board[0][col]

    #Diagonal Victories
    if (board[0][0] is not EMPTY):
        if (board[0][0] == board[1][1] == board[2][2]):
            return board[0][0]
    if (board[0][2] is not EMPTY):
        if (board[0][2] == board[1][1] == board[2][0]): 
            return board[0][2]
    
    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if (winner(board) is not None) or (all(cell is not EMPTY for row in board for cell in row)):
        return True
    else:
        return False


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if winner(board) == X:
        return 1
    if winner(board) == O:
        return -1
    return 0


def max_value(board, alpha, beta):
    """
    Recursively computes best achievable utility for X
    """
    if terminal(board):
        return utility(board)
    
    v = -math.inf

    for action in actions(board):
        v = max(v, min_value(result(board, action), alpha, beta))
        alpha = max(alpha, v)
        if alpha >=beta:
            break

    return v


def min_value(board, alpha, beta):
    """
    Recursively computes best achievable utility for O
    """
    if terminal(board):
        return utility(board)
    
    v = math.inf

    for i in actions(board):
        v = min(v, max_value(result(board, i), alpha, beta))
        beta = min(beta, v)
        if alpha >=beta:
            break

    return v


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        return None
    
    alpha = -math.inf
    beta = math.inf

    if player(board) == X:
        best_score = -math.inf
        best_action = None
        for action in actions(board):
            score = min_value(result(board, action), alpha, beta)
            if score > best_score:
                best_score = score
                best_action = action
        return best_action
    else:
        best_score = math.inf
        best_action = None
        for action in actions(board):
            score = max_value(result(board,action), alpha, beta)
            if score < best_score:
                best_score = score
                best_action = action
        return best_action