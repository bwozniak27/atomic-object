#!/usr/bin/python

import sys
import json
import socket

# line = direction of line - 8 directions
def count_line(board, player, square, line):
  direction = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
  count = 0
  end = False
  row = square[0]
  col = square[1]
  target = 2 if player == 1 else 1
  # loop through direction until player's piece is found to count num of pieces in line
  # if empty square or end of board is found then line is invalid
  while not end:
    row += direction[line][0]
    col += direction[line][1]
    # edge
    if row < 0 or row > 7 or col < 0 or col > 7:
      count = 0
      end = True
    # opponent piece
    elif board[row][col] == target:
      count += 1
    else:
      # is not sandwhich so line is invalid
      if board[row][col] == 0:
        count = 0
      end = True
  return count

# returns the total number of pieces that the player can flip by counting each direction
def count_total(board, player, square):
  total = 0
  for i in range(8):
    total += count_line(board, player, square, i) 
  return total

# returns if square is a corner square
def is_corner(square):
  if square[0] in [0,7] and square[1] in [0,7]:
    return True
  return False

def is_danger_zone(square):
  if square[0] in [0, 7] and square[1] in [1, 6]:
    return True
  if square[0] in [1, 6] and square[1] in [0, 1, 6, 7]:
    return True
  return False


def get_move(player, board):
  best_move = None
  best_score = 0
  danger_move = None
  for row in range(len(board)):
    for col in range(len(board[row])):
      # playable square
      if board[row][col] == 0:
        square = [row, col]
        # available pieces to capture with move
        score = count_total(board, player, square)
        # valid move
        if score > 0:
          # corners win championships
          if is_corner(square):
            return square
          # dont let opponent get corner
          elif is_danger_zone(square):
            danger_move = square
            continue # skip move if another move exists
        if score > best_score:
          best_score = score
          best_move = square
  # only used danger move if no other move exists
  return best_move if best_move else danger_move

def prepare_response(move):
  response = '{}\n'.format(move).encode()
  print('sending {!r}'.format(response))
  return response

if __name__ == "__main__":
  port = int(sys.argv[1]) if (len(sys.argv) > 1 and sys.argv[1]) else 1337
  host = sys.argv[2] if (len(sys.argv) > 2 and sys.argv[2]) else socket.gethostname()

  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  try:
    sock.connect((host, port))
    while True:
      data = sock.recv(1024)
      if not data:
        print('connection to server closed')
        break
      json_data = json.loads(str(data.decode('UTF-8')))
      board = json_data['board']
      maxTurnTime = json_data['maxTurnTime']
      player = json_data['player']
      print(player, maxTurnTime, board)

      move = get_move(player, board)
      response = prepare_response(move)
      sock.sendall(response)
  finally:
    sock.close()
