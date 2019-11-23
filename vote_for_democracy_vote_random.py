""" This script should enable someone to vote randomly, without knowing the person they vote for."""

import string
from numpy.random import choice
import urllib.request
from bs4 import BeautifulSoup

import googleSheetEditor

candidate_list_url = "https://www.bbc.co.uk/news/politics/constituencies"
raw_wiki_polling_data = "1ruIC5qL6tRhG1G7Gof7QaeX2Quv9pMHbdfBYF10uZCg"

page = urllib.request.urlopen(candidate_list_url)
soup = BeautifulSoup(page.read(), 'html.parser')
cons = soup.findAll("table")
links = [c.findAll("a") for c in cons]
constituency_urls = {}
for ll in links:
    for l in ll:
        constituency_urls[l.string] = l["href"]

def get_candidates_for(constituency):
    if constituency not in constituency_urls:
        print(f"Could not find {constituency} in the list of constituencies.")
        return
    
    candidates_page = urllib.request.urlopen('https://www.bbc.co.uk' + constituency_urls[constituency])
    soup = BeautifulSoup(candidates_page.read(), 'html.parser')
    
    candidate_rows = soup.findAll("div", {"class": "ge2019-candidate-list__row"})
    
    return [(cr.findAll("div")[1].span.string, cr.findAll("div")[0].findAll("span")[1].string) for cr in candidate_rows]

def get_party_weights(average_last=5):
    rows = googleSheetEditor.get_range(
        sheet_id=raw_wiki_polling_data,
        range=f"Sheet1!E1:M{2+average_last}"
    )

    def getprob(s):
        r = "".join([n for n in s if n in '0123456789'])
        return float(r)/100 if r != "" else 0

    wiki_to_bbc = {
        'Con': 'Conservative',
        'Lab': 'Labour',
        'Lib Dem': 'Liberal Democrat',
        'SNP': 'Scottish National Party',
        'Plaid Cymru': 'Plaid Cymru',
        'UKIP': 'UKIP',
        'Green': 'Green',
        'Brexit': 'The Brexit Party',
        'Change UK': 'Change UK',
    }

    p = {}

    for party in wiki_to_bbc:
        p[wiki_to_bbc[party]] = 0

    for party_index in range(len(rows[0])):
        for i in range(2, 2 + average_last):
            p[wiki_to_bbc[rows[0][party_index]]] += getprob(rows[i][party_index])

    for party in p:
        p[party] = p[party]/average_last
        
    return [(party, p[party]) for party in p]

example_list_of_candidates_and_parties = [
	("Claire", "Conservative"),
	("Adam", "Independent"),
	("Bob", "Labour"),
	("Daniel", "Green"),
]

example_probability_weights = [
    ('Conservative', 0.43),
    ('Labour', 0.29666666666666663),
    ('Liberal Democrat', 0.14222222222222222),
    ('SNP', 0.03222222222222223),
    ('Plaid Cymru', 0.0044444444444444444),
    ('UKIP', 0.0022222222222222222),
    ('Green', 0.030000000000000002),
    ('The Brexit Party', 0.04111111111111111),
    ('Change UK', 0.0)
]

def i_should_tick_box(candidates, weights):
    #party_candidates = [c for c in candidates if c[1] in [p[0] for p in weights]]
    discounted_candidates = [c for c in candidates if c[1] not in [p[0] for p in weights]]
    
    if not set([d[1] for d in discounted_candidates]).issubset({"Independent"}):
        print("Warning: candidates with the following affiliation have been discarded,",
            "since national polling data cannot inform us on their popularity \n",
            *[d[1]+"\n" for d in discounted_candidates],
            "\n If any of these are well known parties, something has gone wrong.",
        )
        
    relevant_weights = []
    
    for c in candidates:
        weight = [w for w in weights if w[0] == c[1]]
        relevant_weights.append(weight[0][1] if weight != [] else 0)
    
    m = sum(relevant_weights)
    relevant_weights = [r/m for r in relevant_weights]
    
    my_candidate = choice(range(len(candidates)), p=relevant_weights)
    
    return my_candidate + 1


def random_vote_in(constituency):
    candidates = get_candidates_for(constituency)
    p = get_party_weights()
    
    return i_should_tick_box(candidates, p)
     
def profile(constituency, samples=10000):
    candidates = get_candidates_for(constituency)
    p = get_party_weights()
    
    c = {i:0 for i in range(1, len(candidates) + 1)}
    for i in range(samples):
       c[i_should_tick_box(candidates, p)] += 1
    
    for box in c:
        print(box, c[box])
    