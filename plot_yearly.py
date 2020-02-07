
"""
Make bibiliometric plots for the National Committee for Astronomy Mid-term Review.
"""

import os
import pickle
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from astropy.table import Table

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
    unique_years = np.arange(min(years), 2 + max(years)) - 0.5

    hist_kwds = dict(rwidth=0.95, facecolor="#CCCCCC", bins=unique_years)
    hist_kwds.update(kwargs)

    fig, ax = plt.subplots()
    counts, years, *_ = ax.hist(years, **hist_kwds)

    years = unique_years[1:].astype(int)
    data = Table(data=dict(years=years, unique_article_count=counts))

    ticks = unique_years[:-1]

    ax.set_xticks(ticks + 0.5)
    ax.set_xticklabels([r"${0}$".format(year) for year in years],
                       rotation=rotation)
    #ax.set_xlabel(r"$\textrm{Year}$")
    ax.set_ylabel(r"$\textrm{Unique article count}$")
    ax.set_xlim(ticks[0] - 0.25, ticks[-1] + 1.25)
    fig.tight_layout()

    return (fig, data)



def _parse_author(name):
    skip_keywords = ("collaboration", "team", "noao data lab", "consortium")
    for kw in skip_keywords:
        if kw in name.lower():
            return None

    last_name, *_ = name.split(",")
    if len(_) == 0:
        _.append("")
    return f"{last_name.strip()}, {_[0].strip()[:1].upper()}"

def _is_australian_affiliation(affiliation):
    return "australia" in affiliation.lower()


def plot_unique_authors_by_year(library, rotation=60, **kwargs):
    r"""
    Produce a histogram plot of the number of unique authors by year.

    :param library:
        A library of data. 
        # TODO explain format.

    """

    # Get unique names (last names + first initial only).
    # TODO this is wrong but no time.
    authors_per_year = dict()
    for bibcode, article_data in library.items():

        year = int(article_data["year"])
        authors_per_year.setdefault(year, list())

        for author, aff in zip(article_data["author"], article_data["aff"]):
            if not _is_australian_affiliation(aff):
                continue

            parsed_author_name = _parse_author(author)
            if parsed_author_name is None:
                continue

            authors_per_year[year].append(parsed_author_name)

    unique_authors_per_year = []
    for year in sorted(authors_per_year.keys()):
        unique_authors_per_year.append([year, len(set(authors_per_year[year]))])

    unique_authors_per_year = np.array(unique_authors_per_year)

    unique_years = unique_authors_per_year.T[0]

    hist_kwds = dict(rwidth=0.95, facecolor="#CCCCCC", bins=unique_years)
    hist_kwds.update(kwargs)

    fig, ax = plt.subplots()
    ax.bar(unique_years, unique_authors_per_year.T[1])
    
    ticks = unique_years

    ax.set_xticks(ticks)
    ax.set_xticklabels([r"${0}$".format(year) for year in ticks],
                       rotation=rotation)
    #ax.xaxis.set_tick_params(width=0)
    ax.set_ylabel(r"$\textrm{Unique Australian author count}$")
    
    ax.set_xlim(unique_years[0] - 0.75, unique_years[-1] + 0.75)
    fig.tight_layout()

    t = Table(rows=unique_authors_per_year, names=("year", "unique_author_count"))
    return (fig, t)




if __name__ == "__main__":

    with open("1996-2019-hiif.pkl", "rb") as fp:
        library = pickle.load(fp)

    fig, data = plot_unique_authors_by_year(library)
    data.write("unique_australian_authors_by_year.csv")
    fig.savefig("unique_australian_authors_by_year.pdf", dpi=600)

    years = np.array([article["year"] for article in library.values()]).astype(int)
    fig, data = plot_papers_by_year(years, facecolor="tab:blue")
    data.write("papers_by_year.csv")
    fig.savefig("papers_by_year.pdf", dpi=600)
