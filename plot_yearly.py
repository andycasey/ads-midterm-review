
"""
Make bibiliometric plots for the National Committee for Astronomy Mid-term Review.
"""

import os
import pickle
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

matplotlib.style.use({

    # Lines
    'lines.linewidth': 1.7,
    'lines.antialiased': True,
    'lines.marker': '.',
    'lines.markersize': 5.,

    # Patches
    'patch.linewidth': 1.0,
    'patch.facecolor': '#348ABD',
    'patch.edgecolor': '#CCCCCC',
    'patch.antialiased': True,

    # images
    'image.origin': 'upper',

    # Font
    'font.size': 12.0,
    'text.usetex': True,
    'text.latex.preamble': r'\usepackage{amsmath}',
    'text.latex.preview': True,
    'axes.unicode_minus': False,
})


def plot_papers_by_year(years, rotation=60, **kwargs):
    r"""
    Produce a histogram plot of the number of unique years by year.

    :param years:
        A list of year of each article publication.
    
    :param rotation: [optional]
        The angle of rotation for the x-axis tick labels.
    """

    #years = [int(article.year) for article in articles]
    unique_years = np.arange(min(years), 2 + max(years))

    hist_kwds = dict(rwidth=0.95, facecolor="#CCCCCC", bins=unique_years)
    hist_kwds.update(kwargs)

    fig, ax = plt.subplots()
    ax.hist(years, **hist_kwds)

    ticks = unique_years[:-1]

    ax.set_xticks(ticks + 0.5)
    ax.set_xticklabels([r"${0}$".format(year) for year in ticks],
                       rotation=rotation)
    ax.set_xlabel(r"$\textrm{Year}$")
    ax.set_ylabel(r"$\textrm{Unique article count}$")
    
    fig.tight_layout()

    return fig


if __name__ == "__main__":

    with open("1996-2018-hiif.pkl", "rb") as fp:
        library = pickle.load(fp)


    years = np.array([article["year"] for article in library.values()]).astype(int)
    fig = plot_papers_by_year(years, facecolor="tab:blue")
    fig.savefig("papers_by_year.pdf", dpi=600)
