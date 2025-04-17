import seaborn as sns
from math import sqrt
import matplotlib

# sns.set_style("white")

# The following is the latexify function. It allows you to create 2 column or 1
# column figures. You may also wish to alter the height or width of the figure.
# The default settings are good for most cases. You may also change the
# parameters such as labelsize and fontsize based on your classfile.
def latexify(fig_width=None, fig_height=None, columns=1):
    """Set up matplotlib's RC params for LaTeX plotting.
    Call this before plotting a figure.

    Parameters
    ----------
    fig_width : float, optional, inches
    fig_height : float,  optional, inches
    columns : {1, 2}
    """

    # code adapted from http://www.scipy.org/Cookbook/Matplotlib/LaTeX_Examples
    # Width and max height in inches for IEEE journals taken from
    # computer.org/cms/Computer.org/Journal%20templates/transactions_art_guide.pdf

    assert(columns in [1, 2])

    if fig_width is None:
        fig_width = 6.9 if columns == 1 else 13.8  # width in inches #3.39

    if fig_height is None:
        golden_mean = (sqrt(5) - 1.0) / 2.0    # Aesthetic ratio
        fig_height = fig_width * golden_mean  # height in inches

    MAX_HEIGHT_INCHES = 16.0
    if fig_height > MAX_HEIGHT_INCHES:
        print(("WARNING: fig_height too large:" + fig_height +
              "so will reduce to" + MAX_HEIGHT_INCHES + "inches."))
        fig_height = MAX_HEIGHT_INCHES

    params = {
            # 'backend': 'ps',
              'pgf.rcfonts': False,
              'pgf.preamble': ['\\usepackage{gensymb}', '\\usepackage[dvipsnames]{xcolor}'],
              "pgf.texsystem": "pdflatex",
              'text.latex.preamble': ['\\usepackage{gensymb}', '\\usepackage[dvipsnames]{xcolor}'],

              #values below are useful defaults. individual plot fontsizes are
              #modified as necessary.
              'axes.labelsize': 15,  # fontsize for x and y labels
              'axes.titlesize': 15,
              'font.size': 15,
              'legend.fontsize': 10,
              'xtick.labelsize': 10,
              'ytick.labelsize': 10,
              'text.usetex': False,
              'figure.figsize': [fig_width, fig_height],
              'font.family': 'sans-serif',
               'lines.linewidth': 1,
               'lines.markersize':1,
               'xtick.major.pad' : 2,
               'ytick.major.pad' : 2
              }

    matplotlib.rcParams.update(params)

def saveimage(name, fig = matplotlib.pyplot, extension = 'pdf', folder = '', minorticks_off=False, x_grid = False, y_grid=False):
    sns.despine()

    if minorticks_off:
        matplotlib.pyplot.minorticks_off()

    if x_grid:
        matplotlib.pyplot.grid(True, axis = "x", linestyle="--", zorder=-100)
    if y_grid:
        matplotlib.pyplot.grid(True, axis = "y", linestyle="--", zorder=-100)
    
    fig.savefig('{}{}.{}'.format(folder,name, extension), bbox_inches = 'tight')

