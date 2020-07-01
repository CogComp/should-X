from google_suggest import query_patterns
import random

def main():
    # extract_clean_subset()
    print_clean_subset()

def extract_clean_subset():
    outfile = open("questions_faster3_clean_june26_2020.txt", "+w")
    total = 0
    with open("questions_faster3.txt") as f:
        all_lines = list(f.readlines())
        for line in all_lines:
            line = line.replace("\n", "")
            if is_clean(line):
                # print(f" ** {line} -> {is_clean(line)}")
                outfile.write(line)
                total += 1
    print(f" * total of clean questions: {total}")


def print_clean_subset():
    with open("questions_faster3.txt") as f:
        all_lines = list(f.readlines())

        random.shuffle(all_lines)
        print(" --------- CLEAN ------------")
        for line in all_lines[:300]:
            line = line.replace("\n", "")
            if is_clean(line):
                print(f" ** {line} -> {is_clean(line)}")

        print(" --------- UNCLEAN ------------")
        for line in all_lines[:200]:
            line = line.replace("\n", "")
            if not is_clean(line):
                print(f" ** {line} -> {is_clean(line)}")

        clean_lines = [line for line in all_lines if is_clean(line)]
        print(f" * clean queries: {len(clean_lines)}")
        print(f" * all queries: {len(all_lines)}")

import re
number_may_space = re.compile(r'\d may ')
number_may_end = re.compile(r'\d may$')
space_may_numbers = re.compile(r' may \d\d')
begin_may_numbers = re.compile(r'^may \d\d')

def is_clean(query):
    matching_patterns = [q for q in query_patterns if q in f" {query} "]
    if len(matching_patterns) > 0:

        if " may " in matching_patterns and len(matching_patterns) == 1:
            return False

        if "which of the following" in query:
            return False

        if len(query.split(" ")) < 3:
            return False

        # # skip is it is of the form `d may`, `may dd`, etc.
        # if number_may_space.search(query) is not None:
        #     # print(f" ** skipping because it matches the patten: {number_may_space}")
        #     return False
        #
        # if number_may_end.search(query) is not None:
        #     # print(f" ** skipping because it matches the patten: {number_may_end}")
        #     return False
        #
        # if begin_may_numbers.search(query) is not None:
        #     # print(f" ** skipping because it matches the patten: {begin_may_numbers}")
        #     return False
        #
        # if space_may_numbers.search(query) is not None:
        #     # print(f" ** skipping because it matches the patten: {space_may_numbers}")
        #     return False

        return True
    else:
        return False


if __name__ == '__main__':
    main()
