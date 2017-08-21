"""
         ┌──┬──┬──┐
         │ 0│ 1│ 2│
         ├──┼──┼──┤
         │ 3│ 4│ 5│
         ├──┼──┼──┤
         │ 6│ 7│ 8│
┌──┬──┬──┼──┼──┼──┼──┬──┬──┐
│ 9│10│11│12│13│14│15│16│17│
├──┼──┼──┼──┼──┼──┼──┼──┼──┤
│18│19│20│21│22│23│24│25│26│
├──┼──┼──┼──┼──┼──┼──┼──┼──┤
│27│28│29│30│31│32│33│34│35│
└──┴──┴──┼──┼──┼──┼──┴──┴──┘
         │36│37│38│
         ├──┼──┼──┤
         │39│40│41│
         ├──┼──┼──┤
         │42│43│44│
         ├──┼──┼──┤
         │45│46│47│
         ├──┼──┼──┤
         │48│49│50│
         ├──┼──┼──┤
         │51│52│53│
         └──┴──┴──┘
"""

import re

try:
    from functools import reduce
except ImportError:
    pass

def movesInAlg(sequence):
  return re.findall("[UDRLFBudlrfbxyzMES]w?[2']?", sequence) # alg.cube.expand(sequence)

SOLVED = range(54)

moveDefs = [
  ["U", [       6,  3,  0,
                7,  4,  1,
                8,  5,  2,
   12, 13, 14, 15, 16, 17, 53, 52, 51,
   18, 19, 20, 21, 22, 23, 24, 25, 26,
   27, 28, 29, 30, 31, 32, 33, 34, 35,
               36, 37, 38,
               39, 40, 41,
               42, 43, 44,
               45, 46, 47,
               48, 49, 50,
               11, 10,  9]],
  ["x", [      12, 13, 14,
               21, 22, 23,
               30, 31, 32,
   11, 20, 29, 36, 37, 38, 33, 24, 15,
   10, 19, 28, 39, 40, 41, 34, 25, 16,
    9, 18, 27, 42, 43, 44, 35, 26, 17,
               45, 46, 47,
               48, 49, 50,
               51, 52, 53,
                0,  1,  2,
                3,  4,  5,
                6,  7,  8]],
  ["y", [       6,  3,  0,
                7,  4,  1,
                8,  5,  2,
   12, 13, 14, 15, 16, 17, 53, 52, 51,
   21, 22, 23, 24, 25, 26, 50, 49, 48,
   30, 31, 32, 33, 34, 35, 47, 46, 45,
               38, 41, 44,
               37, 40, 43,
               36, 39, 42,
               29, 28, 27,
               20, 19, 18, 
               11, 10,  9]],
  ["z" , "x y x'"],
  ["D" , "x2 U x2"],
  ["R" , "z D z'"],
  ["L" , "y2 R y2"],
  ["F" , "y' R y"],
  ["B" , "y2 F y2"],
  ["M" , "L' R x'"],
  ["E" , "z M z'"],
  ["S" , "y M y'"],
  ["Rw", "M' R"],
  ["Lw", "M L"],
  ["Uw", "D y"],
  ["Dw", "y' U"],
  ["Fw", "z B'"],
  ["Bw", "z' F"],
  ["r" , "Rw"],
  ["l" , "Lw"],
  ["u" , "Uw"],
  ["d" , "Dw"],
  ["f" , "Fw"],
  ["b" , "Bw"]
]

moveEffects = {}

def applyMove(cube, move):
  if move not in moveEffects:
    raise Exception("Unknown move '" + move + "'")
  return [cube[i] for i in moveEffects[move]]

for move, definition in moveDefs:
  # Moves are defined either as a permutation (undesirable but necessary)
  # or as another algorithm (preferred).
  if isinstance(definition, list):
      moveEffects[move] = definition
  else:
      moveEffects[move] = reduce(applyMove, movesInAlg(definition), SOLVED)
    
  cube = applyMove(SOLVED, move)
  moveEffects[move] = cube

  cube = applyMove(cube, move)
  moveEffects[move + "2"] = cube

  cube = applyMove(cube, move)
  moveEffects[move + "'"] = cube

sides = [
  [ 0,  1,  2,  3,  4,  5,  6,  7,  8],
  [ 9, 10, 11, 18, 19, 20, 27, 28, 29],
  [12, 13, 14, 21, 22, 23, 30, 31, 32],
  [15, 16, 17, 24, 25, 26, 33, 34, 35],
  [36, 37, 38, 39, 40, 41, 42, 43, 44],
  [45, 46, 47, 48, 49, 50, 51, 52, 53]
]

colours = {
    sticker:i
    for i, side in enumerate(sides)
    for sticker in side
}

ignoredStickersForStage = {
  'all': set(),
  'f2l': {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 51, 52, 53}
}

CENTER_STICKER = 4

class Cubid:
    def __init__(self, alg, init=SOLVED):
        self.contents = reduce(applyMove, movesInAlg(alg), init)

    def isSolved(self, stage='all'):
        ignoredStickers = ignoredStickersForStage[stage.lower()]
        return all(
            colours[self.contents[sticker]] == colours[self.contents[side[CENTER_STICKER]]]
            for side in sides # side = [0, 1, 2, 3, ...], [9, 10, 11, ...]
            for sticker in side # sticker = 0, 1, 2 ...
            if self.contents[sticker] not in ignoredStickers
        )

    def apply(self, alg):
        return Cubid(alg, self.contents)
