"""
Make a D3 choropleth map of Australian astrophysics collaborations.
"""


import pickle
import spacy
from spacy.lang.en import English
from spacy.tokens import Doc, Span, Token
from spacy.matcher import PhraseMatcher
import requests
from tqdm import tqdm

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

class RESTCountriesComponent(object):
    """spaCy v2.0 pipeline component that requests all countries via
    the REST Countries API, merges country names into one token, assigns entity
    labels and sets attributes on country tokens.
    """

    name = "rest_countries"  # component name, will show up in the pipeline

    def __init__(self, nlp, label="GPE"):
        """Initialise the pipeline component. The shared nlp instance is used
        to initialise the matcher with the shared vocab, get the label ID and
        generate Doc objects as phrase match patterns.
        """
        # Make request once on initialisation and store the data
        r = requests.get("https://restcountries.eu/rest/v2/all")
        r.raise_for_status()  # make sure requests raises an error if it fails
        countries = r.json()

        # Convert API response to dict keyed by country name for easy lookup
        # This could also be extended using the alternative and foreign language
        # names provided by the API
        self.countries = {c["name"]: c for c in countries}
        # replace one.
        self.countries["United Kingdom"] = self.countries["United Kingdom of Great Britain and Northern Ireland"]
        # TODO: Consider taking these from the altSpellings.
        self.abbreviations = [
            ("United Kingdom", "United Kingdom"),
            ("UK", "United Kingdom"),
            ("U.K.", "United Kingdom"),
            ("U. K.", "United Kingdom"),
            ("USA", "United States of America"),
            ("U.S.A.", "United States of America"),
            ("U. S. A.", "United States of America"),
            ("NZ", "New Zealand"),
            ("N.Z.", "New Zealand"),
            ("N. Z.", "New Zealand")
        ]
        for abbreviation, full_name in self.abbreviations:
            self.countries[abbreviation] = self.countries[full_name]
        self.label = nlp.vocab.strings[label]  # get entity label ID

        # Set up the PhraseMatcher with Doc patterns for each country name
        patterns = [nlp(c) for c in self.countries.keys()]
        self.matcher = PhraseMatcher(nlp.vocab)
        self.matcher.add("COUNTRIES", None, *patterns)

        # Register attribute on the Token. We'll be overwriting this based on
        # the matches, so we're only setting a default value, not a getter.
        # If no default value is set, it defaults to None.
        Token.set_extension("is_country", default=False, force=True)
        Token.set_extension("country_capital", default=False, force=True)
        Token.set_extension("country_latlng", default=False, force=True)
        Token.set_extension("country_flag", default=False, force=True)

        # Register attributes on Doc and Span via a getter that checks if one of
        # the contained tokens is set to is_country == True.
        Doc.set_extension("has_country", getter=self.has_country, force=True)
        Span.set_extension("has_country", getter=self.has_country, force=True)

    def __call__(self, doc):
        """Apply the pipeline component on a Doc object and modify it if matches
        are found. Return the Doc, so it can be processed by the next component
        in the pipeline, if available.
        """
        matches = self.matcher(doc)
        spans = []  # keep the spans for later so we can merge them afterwards
        for _, start, end in matches:
            # Generate Span representing the entity & set label
            entity = Span(doc, start, end, label=self.label)
            spans.append(entity)
            # Set custom attribute on each token of the entity
            # Can be extended with other data returned by the API, like
            # currencies, country code, flag, calling code etc.
            for token in entity:
                token._.set("is_country", True)
                token._.set("country_capital", self.countries[entity.text]["capital"])
                token._.set("country_latlng", self.countries[entity.text]["latlng"])
                token._.set("country_flag", self.countries[entity.text]["flag"])
            # Overwrite doc.ents and add entity – be careful not to replace!
            doc.ents = list(doc.ents) + [entity]
        for span in spans:
            # Iterate over all spans and merge them into one token. This is done
            # after setting the entities – otherwise, it would cause mismatched
            # indices!
            span.merge()
        return doc  # don't forget to return the Doc!

    def has_country(self, tokens):
        """Getter for Doc and Span attributes. Returns True if one of the tokens
        is a country. Since the getter is only called when we access the
        attribute, we can refer to the Token's 'is_country' attribute here,
        which is already set in the processing step."""
        return any([t._.get("is_country") for t in tokens])


LIBRARY_PATH = "1996-2018-hiif.pkl"


with open(LIBRARY_PATH, "rb") as fp:
    library = pickle.load(fp)

# Load all countries.
r = requests.get("https://restcountries.eu/rest/v2/all")
if not r.ok:
    r.raise_for_status()

countries = r.json()

# Identify countries from affiliations.
nlp = English()
rest_countries = RESTCountriesComponent(nlp)
nlp.add_pipe(rest_countries)

counts = dict()
unique_papers = dict()

n_affiliations_without_identified_countries, n_affiliations_total = (0, 0)
abbreviations = dict(rest_countries.abbreviations)

with tqdm(total=len(library)) as pbar:

    for bibcode, article in library.items():

        unique_countries = []

        for affiliations in article["aff"]:
            for doc in map(nlp, affiliations.split("; ")):
                n_affiliations_total += 1
                for token in doc:
                    if token._.is_country:
                        token_as_str = str(token)
                        token_as_str = abbreviations.get(token_as_str, token_as_str)
                        counts.setdefault(token_as_str, 0)
                        counts[token_as_str] += 1
                        unique_countries.append(token_as_str)
                        break

                else:
                    n_affiliations_without_identified_countries += 1
        
        year = int(article["year"])
        if year >= 1996 and year <= 2019:
            for unique_country in set(unique_countries):
                unique_papers.setdefault(unique_country, 0)
                unique_papers[unique_country] += 1

        f_identified = 1 - n_affiliations_without_identified_countries/n_affiliations_total
        pbar.set_description(f"Fraction of affiliations with identified countries: {f_identified:.2f}")
        pbar.update()

# Need codes too.
rows = "name,code,number\n"
for country, number in counts.items():
    code = rest_countries.countries[country]["alpha3Code"]
    rows += f"{country},{code},{number}\n"

with open("chronopleth_data.csv", "w") as fp:
    fp.write(rows)

unique_papers_per_country_rows = "name,code,number\n"
for country, number in unique_papers.items():
    code = rest_countries.countries[country]["alpha3Code"]
    unique_papers_per_country_rows += f"{country},{code},{number}\n"


with open("unique_papers_per_country_1996_2019.csv", "w") as fp:
    fp.write(unique_papers_per_country_rows)

# Now plot a bar graph.
def plot_bar_graph(country_counts, n_countries=15):

    counts_ = country_counts.copy()
    counts_.pop("Australia")
    # Rename a few.
    rename = {
        "United States of America": "USA",
        "United Kingdom": "UK"
    }
    for before, after in rename.items():
        counts_[after] = counts_.pop(before)

    x = {k: v for k, v in sorted(counts_.items(), key=lambda item: item[1], reverse=True)}

    fig, ax = plt.subplots()

    ypos = np.arange(n_countries)
    yticklabels = list(x.keys())[:n_countries]
    #yticklabels = [" ".join([r"$\textrm{{{0}}}$".format(foo) for foo in ea.split()]) for ea in yticklabels]
    yticklabels = [r"$\textrm{{{0}}}$".format(ea) for ea in yticklabels]

    ax.barh(ypos, list(x.values())[:n_countries], align="center", facecolor="tab:blue")

    ax.set_yticks(ypos)
    ax.set_yticklabels(yticklabels)
    ax.yaxis.set_tick_params(width=0)

    w = 0.75
    ax.set_ylim(ypos[-1] + w, -w)

    ax.set_xlabel(r"$\textrm{Number of collaborations}$")
    fig.tight_layout()

    return fig


fig = plot_bar_graph(counts, n_countries=15)
fig.savefig("collaboration_frequency.pdf", dpi=600)

