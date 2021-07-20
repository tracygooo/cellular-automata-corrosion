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
#    plt.yscale( 'log' )
    plt.legend()


if __name__ == "__main__" : 

    x_lbl , y_lbl = r'Generation' , r'Contents'

    # my_marker = [ 'o' ,'^' , 's' , '<' , 'x' ]
    my_marker = [ 'o' , 'o' ,'o' , 'o' , 'o' , 'o' ]
    grain_size = [ '17' , '37' , '44', '77', '136']
    content_names = ['Cr', 'Ni', 'Carbides' , 'Void', 'Mo', 'Products']


    # ---------------------------------------------------
    # Compare reflectivity for different thicknesses
    # ---------------------------------------------------
    for grain_idx in range( len(grain_size) ) :
        plt.figure()
        data_fname = '../' + grain_size[ grain_idx ] + '_content.txt'
        data = np.loadtxt( data_fname )
        n = len(content_names) 
        x = data[0: , 0 ]
        y = data[0: , 1: ]
        for content_idx in range( n ): 
            if content_idx == 3 or content_idx == 5 :
                continue
            y = data[ 0: , content_idx + 1 ]
            PlotFunt( x , y , x_lbl , y_lbl , content_names[content_idx] , my_marker[ grain_idx ] , '' )
        
        opt_fname = 'figs/contents_' + grain_size[grain_idx] + 'nm.png'
        plt.tight_layout()
        plt.savefig( opt_fname , format = 'png' )
