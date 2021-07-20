"""
Implement diffusion and corrosion process
Update and draw grid
Count materials
Compute roughness and thickness loss
"""

from configs.configs import *
import configs.configs as cf 
import random
import queue
import math


# Clear both buffers
def clearCells():
    cf.num_of_generations = 0
    for row in range(num_cells_y-1, -1, -1):
        for col in range(num_cells_x-1, -1, -1):
            for i in range (0, 2):
                cells_alloy[i][row][col] = 0
                for mat in range(len(diffuse_agents)):
                    cells_diffuse[i][row][col][mat] = 0

def countBitOne(num):
    return bin(num).count("1")

def computeProbability(single_prob, cnt):
    # return 1.0 - pow( 1.0 - single_prob , cnt_cl )
    return single_prob * cnt

# Update diffusion agent after reaction
def updateAgent(agent, sd = 0):
    bits_one = list()
    i = 0
    agent_tmp = agent
    while agent_tmp:
        if agent_tmp & 1 :
            bits_one.append( i )
        agent_tmp = agent_tmp >> 1
        i += 1
    if len( bits_one ) == 0: 
        print( "WARNING: Agent is empty!")
        return
    rd = random.randrange( 0 , len( bits_one ) )
    agent = agent ^ ( 1 << bits_one[rd] )
    return agent

# Diffuse: mu0, mu1, mu2, and mu3 
# rd = rand(0,1), rd <= p0, mu0 = 1 
    # rd > p0 , rd<=p0+p, mu1 = 1
    # rd > p0+p , rd<=p0+p+p2, mu2 = 1
    # else mu3 = 1
# Update the four neighbours based on eq.
def getNonZeroMuIdx( p0 , p2 ) :
    p = ( 1 - p0 - p2 ) / 2.0
    rd = random.uniform( 0 , 1 )
    if rd < p0 : return 0
    elif rd < p0 + p: return 1
    elif rd < p0 + p + p2: return 2
    return 3

# Process drawing function
def processCell(col, row):
    cur_cell_alloy = cells_alloy[cf.other_buffer][row][col]
    probs_sum = []
    prods = []
    mats = []

    # === Diffuse from four neighborhoods to current processing cell
    # --- Check four neighbors
    dr = [ 0 , -1 , 0 , 1 ]
    dc = [ 1 , 0 , -1 , 0 ]
    # i = {0,1,2,3} ==> {right,up,left,down} ==> Ci in textbook
    for mat in range(len(diffuse_agents)):
        if row == 0:
            cells_diffuse[cf.current_buffer][row][col][mat] = 15
        elif row == num_cells_y - 1:
            cells_diffuse[cf.current_buffer][row][col][mat] = 0
        else:
            # -- intialized to be empty 
            cells_diffuse[cf.current_buffer][row][col][mat] = 0
            for i in range( 4 ):
                # e.g., i = 0, , i + 2 = 2 represents left direction of right neighbor 
                j = ( i + 2 ) % 4
                new_row = (row + dr[i]) % num_cells_y
                new_col = (col + dc[i]) % num_cells_x
                bit_j = cells_diffuse[cf.other_buffer][new_row][new_col][mat] & ( 1 << j )
                if bit_j: cells_diffuse[cf.current_buffer][row][col][mat] ^= ( 1 << j ) 

            cur_cell_mat = cells_diffuse[cf.current_buffer][row][col][mat]

            # -- Rotation 
            # define p0,p2,p in rules
            mat_name = mat_names[cur_cell_alloy] 
            if mat_name in diffuse_agent_mat_ps[diffuse_agents[mat]]:
                p0 = diffuse_agent_mat_ps[diffuse_agents[mat]][mat_name][0]
                p2 = diffuse_agent_mat_ps[diffuse_agents[mat]][mat_name][1]
            else:
                print( "Warning: {} is not in diffusion file!".format( mat_name ) )
                p0 , p2 = 0.3 , 0.3 # Default probabilities
            l_one = getNonZeroMuIdx( p0 , p2 )
            if l_one != 0 :
                rotated = 0
                for k in range( 4 ):
                    if cur_cell_mat & ( 1 << k ) :
                        rotated ^= 1 << ( ( k + l_one ) % 4 )
                cells_diffuse[cf.current_buffer][row][col][mat] = rotated

        # -- Chemical reaction between alloy and diffuse agent
        cur_cell_mat = cells_diffuse[cf.current_buffer][row][col][mat]
        if cur_cell_alloy in diffuse_agent_mat_product_p[diffuse_agents[mat]]: 
            cnt = countBitOne( cur_cell_mat ) ;
            product, prob = diffuse_agent_mat_product_p[diffuse_agents[mat]][cur_cell_alloy]
            p = computeProbability( prob , cnt )
            rd = random.uniform( 0 , 1 )
            if rd < p :
                if len(probs_sum) == 0: 
                    probs_sum.append(prob)
                else:
                    probs_sum.append(probs_sum[-1] + prob)
                prods.append(product)
                mats.append(mat)

    # reaction pool is empty
    if len(probs_sum) == 0:
        cells_alloy[cf.current_buffer][row][col] = cells_alloy[cf.other_buffer][row][col]
    # Pick an reaction from reaction pool
    else:
        rd = random.uniform( 0 , probs_sum[-1] )
        for i in range(len(prods)):
            if rd <= probs_sum[i]:
                cells_alloy[cf.current_buffer][row][col] = prods[i]
                # cur_cell_mat = cells_diffuse[cf.current_buffer][row][col][mats[i]]
                # cells_diffuse[cf.current_buffer][row][col][mats[i]] = updateAgent( cur_cell_mat )


def updateBoard():
    cf.num_of_generations += 1
    for row in range(num_cells_y):
        for col in range(num_cells_x):
            processCell(col, row)

def displayBoard(display_mode, counts):
    # Draw each cell, count each material
    for row in range(num_cells_y): 
        for col in range(num_cells_x):
            drawCell(col, row, display_mode)
            thisCell = cells_alloy[cf.current_buffer][row][col]
            counts[thisCell] += 1

def drawCell(col, row, display_mode):
    if display_mode == 0:
        color = cf.mat_colors[cells_alloy[cf.current_buffer][row][col]]
    else:
        mat_idx = display_mode - 1
        cnt = countBitOne(cells_diffuse[cf.current_buffer][row][col][mat_idx])
        color = pygame.Color( cf.diffuse_colors[cnt] )
    if cf.separate_cells:
        pygame.draw.rect(screen, color, pygame.Rect(left_bar_width + col*cell_size_x + 1, top_bar_height + row*cell_size_y + 1, cell_size_x-2, cell_size_y-2))
    else:
        pygame.draw.rect(screen, color, pygame.Rect(left_bar_width + col*cell_size_x, top_bar_height + row*cell_size_y, cell_size_x, cell_size_y))

def calculateRoughnessAndThickness():
    prod_id = cf.mat_name_idx["Prod"]
    boundary = []
    visited = [[False for col in range(num_cells_x)]for row in range(num_cells_y)]
    q = queue.Queue()
    q.put([num_cells_y - 1, 0])
    q.put([num_cells_y - 1, num_cells_x - 1])
    visited[num_cells_y - 1][0] = True
    visited[num_cells_y - 1][num_cells_x - 1] = True
    count = 0
    while not q.empty():
        # --- Check four neighbors
        row, col = q.get()
        is_boundary = False
        dr = [ 0 , -1 , 0 , 1 ]
        dc = [ 1 , 0 , -1 , 0 ]
        for i in range( 4 ):
            new_row = (row + dr[i])
            new_col = (col + dc[i])
            if new_row >= 0 and new_row < num_cells_y and new_col >= 0 and new_col < num_cells_x:
                if cells_alloy[cf.current_buffer][new_row][new_col] == prod_id:
                    is_boundary = True
                else:
                    if not visited[new_row][new_col]:
                        q.put([new_row, new_col])
                        visited[new_row][new_col] = True
            if is_boundary:
                boundary.append([row, col])
    sum_y = 0
    count_y = 0
    sum_variance = 0
    sum_abs = 0
    for row, _ in boundary:
        count_y += 1
        sum_y += row
    if count_y == 0:
        average_y = 0
    else:
        average_y = float(sum_y) / count_y
    for row, _ in boundary:
        sum_variance += (row - average_y) ** 2
        sum_abs += abs(row - average_y)
    if count_y == 0:
        Ra  = 0
        Rq = 0
    else:
        Ra = float(sum_abs) / count_y
        Rq = math.sqrt(float(sum_variance) / count_y)
    return Ra, Rq, average_y
