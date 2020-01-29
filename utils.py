

import re

australian_affiliations = [
    # shortname, full name, search string.
    ("UWA", "University of Western Australia", "[w|W]estern [a|A]ustralia"),
    ("Curtin", "Curtin University", "[c|C]urtin"),
    ("Adelaide", "University of Adelaide", "University of Adelaide"),
    ("Monash", "Monash University", "Monash"),
    ("Swinburne", "Swinburne University", "Swinb[o*]urne"),
    ("MEL", "University of Melbourne", "University of Melbourne"),
    ("LAT", "Latrobe University", "La(\s?)[t|T]robe"),
    ("ANU", "Australian National University", "((Australian National University)|(Stromlo)|(Siding Spring))"),
    ("UNSW", "University of New South Wales", "University of New South Wales"),
    ("WSU", "Western Sydney University", "((University of Western Sydney)|(Western Sydney University))"),
    ("USyd", "University of Sydney", "((University of Sydney)|(Sydney University))"),
    ("MCQ", "Macquarie University", "Macquarie"),
    ("TAS", "University of Tasmania", "University of Tasmania"),
    ("ATNF", "Australia Telescope National Facility", "Australia Telescope National Facility"),
    ("AAO", "Anglo-Australian Observatory", "((Anglo-Australian Observatory)|(Australian Astronomical Observatory))"),
    ("CSIRO", "Commonwealth Scientific and Industrial Research Organisation", "CSIRO"),
    ("USQ", "University of Southern Queensland", "University of Southern Queensland"),
    ("UQ", "University of Queensland", "University of Queensland"),
    ("JCU", "James Cook University", "James Cook University"),
    ("DSTO", "Defence Science Technology Group", "Defen[c|s]e Science .+ Technology Group")
]

def parse_australian_affiliation(affiliation):

    matched_affiliations = []
    for each in affiliation.split(";"):
        for short_name, full_name, regex_pattern in australian_affiliations:
            if re.search(regex_pattern, each):
                matched_affiliations.append(full_name)

                #assert "australia" not in each.lower()

    return matched_affiliations

