#!/usr/bin/env python3

"""
Plot multiple lines in one graph
"""

import numpy as np
import set_mpl as sm 
plt = sm.plt

# ---------------------------------------------------
# When one doesn't specify line style and color,
# plt.plot will change them automatically
# ---------------------------------------------------
def PlotFunt( x , y , x_lbl , y_lbl , ln_lbl , my_mk ,  fname ) :
    #plt.plot( x , y ,  '--b' , label = lbl , marker = 'o', ms = 8 , mfc = 'none' , mec = 'r' , mew = 2 )
    plt.plot( x , y ,  label = ln_lbl , marker = my_mk ,  ms = 1 , mfc = 'none' , mew = 1 )
    plt.xlabel( x_lbl )
    plt.ylabel( y_lbl )
    plt.xlim(-100, 5500)
    plt.ylim(-1, 40)
    plt.legend()


if __name__ == "__main__" : 

    res = 600
    x_lbl , y_lbl = r'Generation' , r'Ra (nm)'

    #my_marker = [ 'o' ,'^' , 's' , '<' , 'x' ]
    my_marker = [ 'o' , 'o' ,'o' , 'o' , 'o' , 'o' ]
    grain_size = [ '17' , '37' , '44', '77', '136']
    legend_name = [ '16.7 nm' , '37.5 nm' , '44.1 nm', '76.9 nm', '136.4 nm']


    # ---------------------------------------------------
    # Compare reflectivity for different thicknesses
    # ---------------------------------------------------
    plt.figure()
    for i in range( len(grain_size) ) :
        data_fname = '../' + grain_size[ i ] + '_roughness.txt'
        data = np.loadtxt( data_fname )
        x , y = data[0: , 0 ] , data[0: , 1 ]
        ln_lbl = legend_name[ i ]
        PlotFunt( x , y , x_lbl , y_lbl , ln_lbl, my_marker[ i ] , '' )

    opt_fname = './figs/roughness.png'
    plt.tight_layout()
    plt.savefig( opt_fname , dpi = res, format = 'png' )
