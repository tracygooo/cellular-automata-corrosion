"""
Write down the two lines below
    import set_mpl as sm
    plt = sm.plt
"""

import matplotlib as mpl
my_size = 16 
font = { 'size' : my_size }
mpl.rc( 'xtick' , labelsize = my_size )
mpl.rc( 'ytick' , labelsize = my_size )
mpl.rc( 'font' , **font )
import matplotlib.pyplot as plt
plt.rc('text' , usetex = True )
