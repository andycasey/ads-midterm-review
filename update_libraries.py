
"""
Update (local) libraries that we will use for the National Committee of Astronomy's Mid-term Review.
"""

import ads
import os
import pickle
import warnings
from tqdm import tqdm

# TODO: In the future we should periodically update a remote library and not use this (expensive) query to update a local one.
library_path = "1996-2019-hiif.pkl"
query_string = "aff:(\"Australia\") year:1996-2019 property:refereed bibstem:(MNRAS OR ApJ OR ApJS OR AJ OR AJS OR A&A OR ARA&A OR PASA)"


if not os.path.exists(library_path):
    library = {}
    warnings.warn(f"No path '{library_path}' found. Creating new library..")

else:
    with open(library_path, "rb") as fp:
        library = pickle.load(fp)

articles = ads.SearchQuery(q=query_string,
                            fl=["bibcode", "year", "aff", "author", "citation", "reference"],
                            rows=200, max_pages=100)
                            
# Execute now so we can get the total number of pages.
articles.execute()
_, total = map(int, articles.progress.split("/"))

def parse_article_data(article):
    data = article.__dict__["_raw"].copy()
    for k in ("reference", "citation"):
        bibcodes = data.pop(k, []) or []
        data[k] = dict()
        for bibcode in bibcodes:
            data[k][bibcode] = dict()
    
    return data



for article in tqdm(articles, total=total):
    # Is this in the library?
    if article.bibcode in library:
        # Check for new citations.
        for bibcode in article.citation:
            library[article.bibcode]["citation"].setdefault(bibcode, dict())
    
    else:
        library[article.bibcode] = parse_article_data(article)

# Save before continuing.
with open(library_path, "wb") as fp:
    pickle.dump(library, fp)



