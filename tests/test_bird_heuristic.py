from Levenshtein import ratio as sim
from project1developers import process
from itertools import combinations

def test_name_similarity_condition():
    name1 = "john doe"
    name2 = "jon doe"
    assert sim(name1, name2) >= 0.7

def test_email_prefix_similarity():
    prefix1 = "johndoe"
    prefix2 = "john_doe"
    assert sim(prefix1, prefix2) >= 0.7

def test_first_and_last_name_similarity():
    first1, last1 = "john", "doe"
    first2, last2 = "johnny", "doe"
    assert sim(first1, first2) >= 0.7
    assert sim(last1, last2) >= 0.7

def test_bird_heuristic_pipeline():
    devs = [
        ("John Doe", "john.doe@gmail.com"),
        ("Jon Doe", "jon.doe@gmail.com"),
        ("Alice Smith", "alice.smith@gmail.com"),
        ("Jacek Marchwicki,", "jacek.marchwicki@gmail.com"),
        ("Jackson Gardner", "jacksongardner@google.com"),
        ("James Lee,", "leebebe0612@gmail.com")
    ]

    SIMILARITY = []
    for dev_a, dev_b in combinations(devs, 2):
        name_a, first_a, last_a, i_first_a, i_last_a, email_a, prefix_a = process(dev_a)
        name_b, first_b, last_b, i_first_b, i_last_b, email_b, prefix_b = process(dev_b)
        c1 = sim(name_a, name_b)
        c2 = sim(prefix_a, prefix_b)
        c31 = sim(first_a, first_b)
        c32 = sim(last_a, last_b)
        if c1 >= 0.7 or c2 >= 0.7 or (c31 >= 0.7 and c32 >= 0.7):
            SIMILARITY.append((dev_a[0], dev_b[0]))

    names = [pair for pair in SIMILARITY if "John" in pair[0] or "Jon" in pair[1]]
    assert len(names) >= 1