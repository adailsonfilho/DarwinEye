#Text parameters
XSMALL = 7
SMALL = 9
NORMAL = 11
BIG = 13

#PADDING (%)
PAD = .05
MPL_COLORMAP= 'brg'

#LAYOUT CONFIGURATION
LEFT = 0.04
BOTTOM = 0.07
RIGHT = 0.98
TOP = 0.94
WSPACE = 0.17
HSPACE = 1.

#Line Width
LW_THIN = 0.3
LW_MEDIUM = 0.5
LW_NORMAL = 1
LW_TICK = 2

MAXIMIZE = 'maximize'
MINIMIZE = 'minimize'

#COLORS
RED = 'red'
BLACK = 'black'
RED_DARK = '#AA2222'
GREEN = 'green'
ORANGE = 'orange'
BLUE = 'blue'
GRAY8 = '#888888'

#size of scatter point
SMAX = 50
SMIN = 10

ALPHA50 = 0.5
ALPHA70 = 0.7
ALPHA80 = 0.8
ALPHA100 = 1.

SCATTER_DEFAULT = dict(edgecolor=GRAY8,lw=1)
SCATTER_HIGH = dict(edgecolor=BLACK, lw=2)

LINE_DEFAULT = dict(alpha=ALPHA70, lw=LW_MEDIUM)
LINE_HIGH = dict(alpha=ALPHA100, lw=LW_TICK, zorder=101)