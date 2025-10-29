import csv
import pandas as pd
import unicodedata
import string
from itertools import combinations
from Levenshtein import ratio as sim
import os
from lmstudio_connector import send_devs_and_get_similarity
from pydriller import Repository


# Function for pre-processing each name,email
def process(dev):
    name: str = dev[0]

    # Remove punctuation
    trans = name.maketrans("", "", string.punctuation)
    name = name.translate(trans)
    # Remove accents, diacritics
    name = unicodedata.normalize("NFKD", name)
    name = "".join([c for c in name if not unicodedata.combining(c)])
    # Lowercase
    name = name.casefold()
    # Strip whitespace
    name = " ".join(name.split())

    # Attempt to split name into firstname, lastname by space
    parts = name.split(" ")
    # Expected case
    if len(parts) == 2:
        first, last = parts
    # If there is no space, firstname is full name, lastname empty
    elif len(parts) == 1:
        first, last = name, ""
    # If there is more than 1 space, firstname is until first space, rest is lastname
    else:
        first, last = parts[0], " ".join(parts[1:])

    # Take initials of firstname and lastname if they are long enough
    i_first = first[0] if len(first) > 1 else ""
    i_last = last[0] if len(last) > 1 else ""

    # Determine email prefix
    email: str = dev[1]
    prefix = email.split("@")[0]

    return name, first, last, i_first, i_last, email, prefix

USE_LMSTUDIO = True

# This block of code take the repository, fetches all the commits,
# retrieves name and email of both the author and commiter and saves the unique
# pairs to csv
# If you provide a URL, it clones the repo, fetches the commits and then deletes it,
# so for a big project better clone the repo locally and provide filesystem path



if __name__ == "__main__": # Added if-sentence so tests dont run all the code when importing process function
    if USE_LMSTUDIO:
        threshold = 0.7
        try:
            names = send_devs_and_get_similarity(
                os.path.join("project1devs", "devs.csv"), threshold
            )
            output_csv = os.path.join("project1devs", f"devs_similarity_t={threshold}.csv")
            # Tallenna nimet CSV:hen
            with open(output_csv, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["name"])
                for name in names:
                    writer.writerow([name])
            print(f"Similarity file saved to: {output_csv}")

        except Exception as e:
            print("LM Studio connection failed, using Bird heuristic instead.")
            print(f"Error: {e}")
            USE_LMSTUDIO = False

    if not USE_LMSTUDIO:
        DEVS = set()
        for commit in Repository("!!! Add repo directory here !!!").traverse_commits():
             DEVS.add((commit.author.name, commit.author.email))
             DEVS.add((commit.committer.name, commit.committer.email))

        DEVS = sorted(DEVS)


        # Write repository data to CSV
        with open(os.path.join("project1devs", "devs.csv"), "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["name", "email"])
            for dev in DEVS:
                writer.writerow([dev[0], dev[1]])

        # Read csv file with name,dev columns
        with open(os.path.join("project1devs", "devs.csv"), "r", newline="", encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile, delimiter=",")
            for row in reader:
                DEVS.append(row)
        # First element is header, skip
        DEVS = DEVS[1:]
        print(DEVS)

        # Compute similarity between all possible pairs
        SIMILARITY = []
        for dev_a, dev_b in combinations(DEVS, 2):
            # Pre-process both developers
            name_a, first_a, last_a, i_first_a, i_last_a, email_a, prefix_a = process(dev_a)
            name_b, first_b, last_b, i_first_b, i_last_b, email_b, prefix_b = process(dev_b)

            # Conditions of Bird heuristic
            c1 = sim(name_a, name_b)
            c2 = sim(prefix_b, prefix_a)
            c31 = sim(first_a, first_b)
            c32 = sim(last_a, last_b)
            c4 = c5 = c6 = c7 = False
            # Since lastname and initials can be empty, perform appropriate checks
            if i_first_a != "" and last_a != "":
                c4 = i_first_a in prefix_b and last_a in prefix_b
            if i_last_a != "":
                c5 = i_last_a in prefix_b and first_a in prefix_b
            if i_first_b != "" and last_b != "":
                c6 = i_first_b in prefix_a and last_b in prefix_a
            if i_last_b != "":
                c7 = i_last_b in prefix_a and first_b in prefix_a

            # Save similarity data for each conditions. Original names are saved
            SIMILARITY.append(
                [dev_a[0], email_a, dev_b[0], email_b, c1, c2, c31, c32, c4, c5, c6, c7]
            )

        # Save data on all pairs (might be too big -> comment out to avoid)
        cols = [
            "name_1",
            "email_1",
            "name_2",
            "email_2",
            "c1",
            "c2",
            "c3.1",
            "c3.2",
            "c4",
            "c5",
            "c6",
            "c7",
        ]
        df = pd.DataFrame(SIMILARITY, columns=cols)
        df.to_csv(
            os.path.join("project1devs", "devs_similarity.csv"), index=False, header=True
        )

        # Set similarity threshold, check c1-c3 against the threshold
        t = 0.7
        print("Threshold:", t)
        df["c1_check"] = df["c1"] >= t
        df["c2_check"] = df["c2"] >= t
        df["c3_check"] = (df["c3.1"] >= t) & (df["c3.2"] >= t)
        # Keep only rows where at least one condition is True
        df = df[
            df[["c1_check", "c2_check", "c3_check", "c4", "c5", "c6", "c7"]].any(axis=1)
        ]

        # Omit "check" columns, save to csv
        df = df[
            [
                "name_1",
                "email_1",
                "name_2",
                "email_2",
                "c1",
                "c2",
                "c3.1",
                "c3.2",
                "c4",
                "c5",
                "c6",
                "c7",
            ]
        ]
        df.to_csv(
            os.path.join("project1devs", f"devs_similarity_t={t}.csv"),
            index=False,
            header=True,
        )
