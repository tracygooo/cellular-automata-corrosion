"""
Config CA program
    Set grid geometries
    Read input cards (materials,diffusion,reaction rules,termination)
    Set GUI
    Initialize grid status and flow control
"""

import pygame
from pygame.locals import *
from collections import defaultdict

pygame.init()

# --- Set grid geometries
top_bar_height, left_bar_width = 45, 8*25
material_section_start_y = 250
text_space_x, text_space_y = 4, 4
num_cells_x , num_cells_y , cell_size_x , cell_size_y = 250 , 250 , 3 , 3 
screen_size_x = num_cells_x*cell_size_x + left_bar_width
screen_size_y = num_cells_y*cell_size_y + top_bar_height

# --- Read materials and colors in
mat_fname = "../input/materials.txt"
lines = list()
with open(mat_fname, 'r') as fobj:
    for line in fobj:
        if line[0] == '#': continue
        lines.append( line.split() )
mat_names = lines[0] 
mat_colors = lines[1] 
diffuse_agents = lines[2]
mat_name_idx = dict(zip(mat_names, range(len(mat_names))))

# --- Read diffusion probabilities in 
diffuse_fname = "../input/diffusion.txt"
diffuse_agent_mat_ps = dict() # {agent,{material,[p0,p2]}}
for name in diffuse_agents:
    diffuse_agent_mat_ps[name] = {}
with open(diffuse_fname, 'r') as fobj:
    for line in fobj:
        if line[0] == '#': continue
        line = line.split()
        diffuse_agent_mat_ps[ line[0] ][ line[1] ] = [ float( line[2] ) , float( line[3] ) ]

# --- Termination
end_G = 300000000 
end_T = 240
with open("../input/termination.txt") as f:
    for line in f:
        if line[0] == '#':
            continue
        else:
            line = line.split() 
            if line[0] == "end_generation":
                end_G = int(line[1])
                continue
            if line[0] == "end_thickness_loss":
                end_T = int(line[1])
                continue

# --- Reactions
# {agent,{material,[product,probability]}}
diffuse_agent_mat_product_p = dict()
for name in diffuse_agents:
    diffuse_agent_mat_product_p[name] = {}
with open("../input/rules.txt") as f:
    for line in f:
        if line[0] == '#':
            continue
        else:
            line = line.split() 
            if line[0] == "end_r":
                end_R = float(line[1])
                continue
            if line[0] == "end_g":
                end_G = int(line[1])
                continue
            if line[0] == "end_t":
                end_T = int(line[1])
                continue
            diffuse_agent = line[0]
            react = mat_name_idx[line[1]]
            prod = mat_name_idx[line[2]]
            prob = float( line[3] )
            diffuse_agent_mat_product_p[diffuse_agent][react] = [prod, prob]


# --- GUI 
pygame.event.set_allowed([QUIT, KEYDOWN])
pygame.display.set_caption('CA Corrosion Simulation')
screen = pygame.display.set_mode((screen_size_x, screen_size_y))

# fonts
heading_font = pygame.font.SysFont("consolas", 36)
text_font = pygame.font.SysFont("consolas", 34)
heading_font_height = heading_font.get_height()
text_font_height = text_font.get_height()

# colors 
text_color = pygame.Color(0, 0, 0)
separator_color = pygame.Color(0, 0, 0)
background_color = pygame.Color(255, 255, 255)
pause_color = pygame.Color(255, 32, 32)
running_color = pygame.Color(0, 255, 0)


# headings, removed for saving space 
status_heading_text = heading_font.render("Status", True, text_color, background_color)
materials_heading_text = heading_font.render("Materials", True, text_color, background_color)
counts_heading_text = heading_font.render("Counts", True, text_color, background_color)

# text and legend
running_text = text_font.render("Running", True, running_color, background_color)
step_text = text_font.render("Step", True, running_color, background_color)
paused_text = text_font.render("Paused", True, pause_color, background_color)
generation_text = text_font.render("Gen:", True, text_color, background_color)
roughness_text = text_font.render("Ra(nm):", True, text_color, background_color)
thickness_text = text_font.render("Loss(nm):", True, text_color, background_color)
diffusion_text = text_font.render("Diffusion: ", True, text_color, background_color)
corrosion_text = text_font.render("Corrosion", True, text_color, background_color)

material_text = [text_font.render(mat_names[i] + ":", True, text_color, background_color) for i in range(len(mat_names))]
material_legend = [text_font.render("  ", True, mat_colors[i] , mat_colors[i]) for i in range(len(mat_names))]
diffuse_agents_text = [text_font.render(diffuse_agents[i], True, text_color, background_color) for i in range(len(diffuse_agents))]
diffuse_colors = [ 'black' , 'blue' , 'green', 'yellow' , 'red' ]
diffuse_legend = [text_font.render("  ", True, diffuse_colors[i] ,diffuse_colors[i]) for i in range(len(diffuse_colors))]
diffuse_count_text = [text_font.render("  " + str(i), True, text_color, background_color) for i in range(len(diffuse_colors))]

# --- Initialized variables: grid status, flow control 
# cells_alloy[r][c][0]: current generation
# cells_alloy[r][c][1]: next generation
cells_alloy = [[[0 for col in range(num_cells_x)]for row in range(num_cells_y)] for generation in range(2)]
cells_diffuse = [[[[0 for diffuse_agent in range(len(diffuse_agents))] for col in range(num_cells_x)]for row in range(num_cells_y)] for generation in range(2)]

num_of_generations = 0
current_buffer = 0
other_buffer = 1 - current_buffer

separate_cells = False # without cell boundary
step = False
paused = True
done = False
