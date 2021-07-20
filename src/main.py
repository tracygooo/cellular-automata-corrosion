#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Entry point for CA corrosion simulation
    import intis.py for grid initializations 
    import configs.config (from intis) to configure program
    apply utils.py to conduct simulation (diffusion,reaction,thickness loss, Ra, contents)
"""

import sys
import os
import glob
import time
from inits import *

__author__ = "Jinghua Feng"
__copyright__ = "Copyright 2021, CA Corrosion Simulation"
__license__ = "GPL"
__version__ = "0.1.0"
__email__ = "tracygooo@gmail.com"
__status__ = "Dev"

if __name__ == "__main__":

    cellsNum = num_cells_x * num_cells_y
    display_mode = 0
    prev_gen = -1

    # Initilize board 
    init_file = sys.argv[1]
    initBoardFromFile(init_file)
    
    # routhness and thickness at gen = 0
    Ra, Rq, thickness  = calculateRoughnessAndThickness()
    roughness_at_gen = cf.num_of_generations

    # === Open output files to save simulation results
    prefix = init_file[:-4]
    prefix = prefix.split('/')[-1]
    opt_dir = "../output/"
    f_content = open(opt_dir + prefix + "_content.txt", "w")
    f_content.write("# gen " + " ".join(mat_names))
    f_thickness = open(opt_dir + prefix + "_thickness.txt", "w")
    f_thickness.write("# gen thickness") 
    f_thickness.write("\n" + str(roughness_at_gen) + " " + str(format(thickness, '.1f'))) 
    f_roughness = open(opt_dir + prefix + "_roughness.txt", "w")
    f_roughness.write("# gen Ra") 
    f_roughness.write("\n" + str(roughness_at_gen) + " " + str(format(Ra, '.1f'))) 
    
    # === Main loop 
    # At start point:
    # paused = True, step = False
    while not cf.done:
        # --- Keyboard event handling
        for event in pygame.event.get():
            # Check to exit
            if event.type == QUIT:
                cf.done = True
            # Check keyboard input
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    cf.done = True
                if event.key == K_SPACE:
                    cf.paused = not cf.paused
                if event.key == K_RETURN:
                    cf.paused = True
                    cf.step = True
                if event.key == K_c:
                    cf.paused = True
                    clearCells()
                if event.key == K_r:
                    initBoardRandom()
                if event.key == K_a:
                    initBoardFromFile(init_file)
                if event.key == K_j:
                    cf.separate_cells = not cf.separate_cells
                if event.key == K_d:
                    display_mode = (display_mode + 1) % (len(diffuse_agents) + 1)
        # Clear the screen
        screen.fill(background_color)

        if not cf.paused or cf.step:
            # Swap buffers
            cf.other_buffer = cf.current_buffer
            cf.current_buffer = 1 - cf.current_buffer
            updateBoard()

        # Draw the cells and count 
        counts = {i: 0 for i in range(len(mat_names))}
        displayBoard(display_mode, counts)

        if cf.num_of_generations != prev_gen: 
            prev_gen = cf.num_of_generations
            line = "\n" + str(cf.num_of_generations)
            for i in range(len(counts)):
                line += " " + str(counts[i])
            f_content.write(line)
            if cf.num_of_generations % 10 == 0 and cf.num_of_generations != 0:
                Ra, Rq, thickness  = calculateRoughnessAndThickness()
                roughness_at_gen = cf.num_of_generations
                f_roughness.write("\n" + str(roughness_at_gen) + " " + str(format(Ra, '.1f'))) 
                f_thickness.write("\n" + str(roughness_at_gen) + " " + str(format(thickness, '.1f'))) 

        # --- Run status
        offset = 10 
        mid_pos = (screen_size_x + left_bar_width) // 2
        status_text_pos = mid_pos + offset 
        if not cf.paused:
            screen.blit(running_text, (status_text_pos, text_space_y))
        elif cf.step:
            screen.blit(step_text, (status_text_pos, text_space_y))
        else:
            screen.blit(paused_text, (status_text_pos, text_space_y))

        # Display mode text
        if display_mode == 0:
            display_pos = mid_pos - corrosion_text.get_width() - offset 
            screen.blit(corrosion_text, (display_pos, text_space_y))
        else:
            mat_idx = display_mode - 1
            display_pos = mid_pos - diffusion_text.get_width() - diffuse_agents_text[mat_idx].get_width() - offset 
            screen.blit(diffusion_text, (display_pos, text_space_y))
            display_pos = mid_pos - diffuse_agents_text[mat_idx].get_width() - offset 
            screen.blit(diffuse_agents_text[mat_idx], (display_pos, text_space_y))

        # --- Left panel 
        # Draw left bar separator
        pygame.draw.line(screen, separator_color, (left_bar_width-1, 0), (left_bar_width-1, screen_size_y), 1)

        # -- Top left panel
        # Status info texts 
        # Draw status heading text, turn off to save space on UI
        # screen.blit(status_heading_text, (text_space_x, text_space_y))

        # Draw number of generations text
        generation_value_text = text_font.render(str(cf.num_of_generations), True, text_color, background_color)
        screen.blit(generation_text, (text_space_x, text_space_y))
        screen.blit(generation_value_text, (text_space_x, text_space_y + text_font_height))	


        # Roughness
        screen.blit(roughness_text, (text_space_x, text_space_y + 2 * text_font_height))	
        raValueText = text_font.render(str(format(Ra, '.1f')), True, text_color, background_color)
        screen.blit(raValueText, (text_space_x, text_space_y + 3 * text_font_height))	

        # Thickness
        screen.blit(thickness_text, (text_space_x, text_space_y + 4 * text_font_height))	
        thickness_value_text = text_font.render(str(format(thickness, '.1f')), True, text_color, background_color)
        screen.blit(thickness_value_text, (text_space_x, text_space_y + 5 * text_font_height))	

        # -- Bottom left panel
        # Materials/counts texts
        # Draw separator
        pygame.draw.line(screen, separator_color, (0, material_section_start_y), (left_bar_width - 1, material_section_start_y), 1)	

        # show text depending on display mode, headings not shown to save space on UI 
        if display_mode == 0:
            # screen.blit(materialsHeadingText, (text_space_x, material_section_start_y + text_space_y))
            percent_value_text = [text_font.render(str( format( float(counts[i]) * 100.0 / cellsNum, '.1f' ) ) + "%", True, text_color, background_color) for i in range(len(mat_names))]
            bar_width = material_legend[0].get_width() + text_space_x

            for i in range (0, len(material_text)):
                pos_y = material_section_start_y + 5 * text_space_y + i*(2*text_font_height + 4)
                screen.blit(material_legend[i], (text_space_x, pos_y))
                screen.blit(material_text[i], (bar_width + text_space_x, pos_y))
                screen.blit(percent_value_text[i], (bar_width + text_space_x, pos_y+text_font_height) )	
        else:
            # screen.blit(countsHeadingText, (text_space_x, material_section_start_y + text_space_y))
            bar_width = diffuse_legend[0].get_width() + text_space_x
            for i in range (5):
                pos_y = material_section_start_y + 5 * text_space_y + i*(text_font_height + 8)
                screen.blit(diffuse_legend[i], (text_space_x, pos_y))
                screen.blit(diffuse_count_text[i], (bar_width + text_space_x, pos_y))

        # --- Update screen 
        pygame.display.flip()

        cf.step = False # Step only once

        # screen shot for end 
        """
        if thickness > end_T or cf.num_of_generations == end_G:
            time.sleep(3)
            if display_mode == 0:
                figname = '../output/figs/' + prefix + '_corrosion_end.png'
                os.system('import -window root ' + figname)
                crop_fig_name = '../output/figs/crop/' + prefix + '_corrosion_end.png'
                os.system('convert ' +  figname + ' -crop 952x797+325+78 ' +  crop_fig_name) 
                display_mode += 1
                cf.paused = True
            elif display_mode == 1:
                figname = '../output/figs/' + prefix + '_diffusion_1_end.png'
                os.system('import -window root ' + figname)
                crop_fig_name = '../output/figs/crop/' + prefix + '_diffusion_1_end.png'
                os.system('convert ' +  figname + ' -crop 952x797+325+78 ' +  crop_fig_name) 
                display_mode += 1
            elif display_mode == 2:
                figname = '../output/figs/' + prefix + '_diffusion_2_end.png'
                os.system('import -window root ' + figname)
                crop_fig_name = '../output/figs/crop/' + prefix + '_diffusion_2_end.png'
                os.system('convert ' +  figname + ' -crop 952x797+325+78 ' +  crop_fig_name) 
                break

        # screen shot for every 50 gens
        elif cf.num_of_generations % 50 == 0:
            time.sleep(3)
            if display_mode == 0:
                figname = '../output/figs/' + prefix + '_corrosion_' + str(cf.num_of_generations) + '.png'
                os.system('import -window root ' + figname)
                crop_fig_name = '../output/figs/crop/' + prefix + '_corrosion_' + str(cf.num_of_generations) + '.png'
                os.system('convert ' +  figname + ' -crop 952x797+325+78 ' +  crop_fig_name) 
                display_mode += 1
                cf.paused = True
            elif display_mode == 1:
                figname = '../output/figs/' + prefix + '_diffusion_1_' + str(cf.num_of_generations) + '.png'
                os.system('import -window root ' + figname)
                crop_fig_name = '../output/figs/crop/' + prefix + '_diffusion_1_' + str(cf.num_of_generations) + '.png'
                os.system('convert ' +  figname + ' -crop 952x797+325+78 ' +  crop_fig_name) 
                display_mode += 1
            elif display_mode == 2:
                figname = '../output/figs/' + prefix + '_diffusion_2_' + str(cf.num_of_generations) + '.png'
                os.system('import -window root ' + figname)
                crop_fig_name = '../output/figs/crop/' + prefix + '_diffusion_2_' + str(cf.num_of_generations) + '.png'
                os.system('convert ' +  figname + ' -crop 952x797+325+78 ' +  crop_fig_name) 
                display_mode = 0
                cf.paused = False
        """
    
    f_content.close()
    f_thickness.close()
    f_roughness.close()
