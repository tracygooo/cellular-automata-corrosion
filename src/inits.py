"""
Implementation of board fill 
    (i) random: fill randomly with materials specified in material card
    (ii) from file: spot, batch, square grain, voronoi grain
"""

from utils import *
from voronoi import *
import random

num_of_mat = len(cf.mat_names)

# Initialize board (randomly) function
def initBoardRandom():
    for row in range(num_cells_y):
        for col in range(num_cells_x):
            random_val = random.randint(0, num_of_mat - 1)
            # Cl excluded
            # random_val = random.randint(0, num_of_mat - 2)
            for i in range (0, 2):
                cells_alloy[i][row][col] = random_val 

def randomFill(x1, x2, y1, y2, materials, probs):
    for row in range(x1, x2 + 1):
        for col in range(y1, y2 + 1):
            random_val = random.randint(1, 1000)
            for i in range(len(materials)):
                if random_val <= probs[i]:
                    cells_alloy[0][row][col] = materials[i] 
                    cells_alloy[1][row][col] = materials[i] 
                    break

def randomFillCell(row, col, materials, probs):
    random_val = random.randint(1, 1000)
    for i in range(len(materials)):
        if random_val <= probs[i]:
            cells_alloy[0][row][col] = materials[i] 
            cells_alloy[1][row][col] = materials[i] 
            break

def randomFillBound(x1, x2, y1, y2, size, width, materials, probs):
    x2 += 1
    y2 += 1
    grain_row_start = x1
    grain_row_end = x1 + size
    out_bound = False
    while not out_bound:
        for row in range(grain_row_start, grain_row_start + width):
            if row >= x2: 
                out_bound = True
                break
            for col in range(y1, y2):
                randomFillCell(row, col, materials, probs)
        for row in range(grain_row_end - width, grain_row_end):
            if row >= x2: 
                out_bound = True
                break
            for col in range(y1, y2):
                randomFillCell(row, col, materials, probs)
        grain_row_start = grain_row_end
        grain_row_end = grain_row_start + size

    grain_col_start = y1
    grain_col_end = y1 + size
    out_bound = False
    while not out_bound:
        for col in range(grain_col_start, grain_col_start + width):
            if col >= x2: 
                out_bound = True
                break
            for row in range(x1, x2):
                randomFillCell(row, col, materials, probs)
        for col in range(grain_col_end - width, grain_col_end):
            if col >= x2: 
                out_bound = True
                break
            if col == y2: break
            for row in range(x1, x2):
                randomFillCell(row, col, materials, probs)
        grain_col_start = grain_col_end
        grain_col_end = grain_col_start + size

def randomFillBoundVoro(num_grain, materials, probs):
    matrix = initVoro(min(cf.num_cells_x, num_cells_y), num_grain)
    for row in range(len(matrix)):
        for col in range(len(matrix)):
            if matrix[row][col] == 1:
                randomFillCell(row, col, materials, probs)


def initBoardFromFile(fname):
    with open(fname) as f:
        for line in f:
            if line[0] == '#':
                continue
            else:
                line = line.split() 

                if line[0] == "batch":
                    color = mat_name_idx[line[1]] 
                    for row in range(int(line[2]), int(line[3]) + 1):
                        for col in range(int(line[4]), int(line[5]) + 1):
                            for i in range (0, 2):
                                cells_alloy[i][row][col] = color 

                elif line[0] == "spot":
                    color = mat_name_idx[line[1]] 
                    row = int(line[2])
                    col = int(line[3])
                    for i in range (0, 2):
                        cells_alloy[i][row][col] = color 
                elif line[0] == "rand":
                    x1 = int(line[1])
                    x2 = int(line[2])
                    y1 = int(line[3])
                    y2 = int(line[4])
                    mats =  []
                    probs = [0]
                    i = 5
                    while i < len(line):
                        mats.append(mat_name_idx[line[i]])
                        probs.append(int(line[i+1]) + probs[-1])
                        i += 2
                    probs.pop(0)
                    randomFill(x1, x2, y1, y2, mats, probs)
                elif line[0] == "grain":
                    x1 = int(line[1])
                    x2 = int(line[2])
                    y1 = int(line[3])
                    y2 = int(line[4])
                    size = int(line[5])
                    width = int(line[6])
                    mats =  []
                    probs = [0]
                    i = 7
                    while i < len(line):
                        mats.append(mat_name_idx[line[i]])
                        probs.append(int(line[i+1]) + probs[-1])
                        i += 2
                    probs.pop(0)
                    randomFillBound(x1, x2, y1, y2, size, width, mats, probs)
                elif line[0] == "voro_grain":
                    num_grain = int(line[1])
                    mats =  []
                    probs = [0]
                    i = 2
                    while i < len(line):
                        mats.append(mat_name_idx[line[i]])
                        probs.append(int(line[i+1]) + probs[-1])
                        i += 2
                    probs.pop(0)
                    randomFillBoundVoro(num_grain, mats, probs)

