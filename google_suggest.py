import json
import random

import requests
import numpy as np
import time
import spacy
from tqdm import tqdm


def example1():
    r = requests.get("http://suggestqueries.google.com/complete/search?output=toolbar&hl=en&q=should%20a")
    print(r.status_code)
    print(r.headers)
    print(r.content)

def example2():
    r = requests.get("http://google.com/complete/search?client=chrome&q=should%20t")
    print(r.status_code)
    print(r.headers)
    print(r.content)


file = "queries.txt"
def query_and_save(prefix):
    queries = get_queries_issued_to_google()
    # skip the query is it's already been queried once
    if prefix in queries:
        print(f" ==> skipping {prefix}")
        return
    r = requests.get(f"http://google.com/complete/search?client=chrome&q={prefix}")
    print(r.status_code)
    print(r.headers)
    print(r.content)
    if r.status_code == 200:
        # save it
        f = open(file, "a")
        content = r.content.decode("utf-8", errors='replace')
        f.write(content + "\n")
        f.close()
    time.sleep(5)

def query_and_return(prefix):
    time.sleep(0.3)
    r = requests.get(f"http://google.com/complete/search?client=chrome&q={prefix}")
    if r.status_code == 200:
        # save it
        content = r.content.decode("utf-8", errors='replace')
        content = json.loads(content)
        return content[1]
    else:
        return []

patterns = []
def query_looper():
    for i in np.arange(ord('a'), 1 + ord('z')):
        # print(chr(i))
        # query_and_save(f"should {chr(i)}")
        # query_and_save(f"why should {chr(i)}")
        # query_and_save(f"reasons why {chr(i)}")
        # query_and_save(f"good reasons why {chr(i)}")
        # query_and_save(f"pros and cons of {chr(i)}")
        query_and_save(f"reasons on why {chr(i)}")
        query_and_save(f"good reasons why {chr(i)}")
        query_and_save(f"facts about why {chr(i)}")
        query_and_save(f"arguments why {chr(i)}")
        query_and_save(f"arguments on why {chr(i)}")


def bootstrap():
    for i in np.arange(12, 40, 2):
        print(f" ============== \n * i: {i}")
        # read the list of queries
        lines = get_google_query_dump()
        sentences = []
        for line in lines:
            jsonl = json.loads(line)
            # print(jsonl[1])
            # filter out the first few
            for sent in jsonl[1]:
                if "should" in sent:
                    sentences.append(sent[0:i])

        for claim in get_perspectrum_claims():
            sentences.append(claim[0:i])

        sentences = list(set(sentences))
        sentences = sorted(sentences, key=lambda x: len(x))
        print("\n".join(sentences))
        for sent in sentences:
            query_and_save(sent)

def get_google_query_dump():
    with open("queries.txt", "r") as f:
        lines = f.readlines()
    return lines

def get_all_extracted_queries():
    with open("queries_extracted.txt", "r") as f:
        lines = f.readlines()
    return lines

def get_queries_issued_to_google():
    lines = get_google_query_dump()
    queries = []
    for line in lines:
        jsonl = json.loads(line)
        queries.append(jsonl[0])
    # print(queries)
    return queries


def get_perspectrum_claims():
    with open("perspectrum_with_answers_v1.0.json", "r") as f:
        data = json.load(f)
        claims = [item["text"] for item in data]
    # print(claims)
    return claims

def write_claims():
    claims = get_perspectrum_claims()
    f = open("perspectrum_claims.txt", "w")
    f.write("\n".join(claims))
    f.close()

def print_extracted_queries():
    nlp = spacy.load("en_core_web_md")
    lines = get_google_query_dump()
    sentences = []
    for line in tqdm(lines):
        jsonl = json.loads(line)
        for sent in jsonl[1]:
            if len(sent) > 15 and sent.count(" ") > 3 and sent not in sentences:
                doc = nlp(sent)
                verbCount = len([token for token in doc if token.pos_ == "VERB"])
                if verbCount == 0:
                    continue
                sentences.append(sent)

    f = open("queries_extracted.txt", "w")
    sentences = list(set(sentences))
    sentences = sorted(sentences)
    f.write("\n".join(sentences))
    f.close()


def try_spacy():
    sent = "shoulder pain icd 10"
    nlp = spacy.load("en_core_web_md")
    doc = nlp(sent)
    verbCount = len([token for token in doc if token.pos_ == "VERB"])
    print(verbCount)
    print([token.pos_ for token in doc])

def count_queries_per_category():
    query_patterns = [
        "reasons on why ",
        "reasons for ",
        "reasons to ",
        "should ",
        "shouldn't ",
        "should not ",
        "why should ",
        "why shouldn't ",
        "why should not ",
        "reasons why ",
        "good reasons why ",
        "pros and cons of ",
        "facts why ",
        "good reasons why ",
        "facts about why ",
        "arguments why ",
        "arguments on why ",
    ]

    # read all the queries from disk:
    extracted = get_all_extracted_queries()

    union = []
    for query_pattern in query_patterns:
        selected = [q for q in extracted if query_pattern in q]
        f = open("query_category/contains_" + query_pattern.replace(" ", "_") + ".txt", "w")
        f.write("".join(selected))
        f.close()
        print(f" * number of queries that contain `{query_pattern}` is {len(selected)}")

        selected_starts = [q for q in selected if q.startswith(query_pattern)]
        f = open("query_category/starts_" + query_pattern.replace(" ", "_") + ".txt", "w")
        f.write("".join(selected_starts))
        f.close()
        print(f" * number of queries that start with `{query_pattern}` is {len(selected_starts)}")

        union.extend(selected)

    union = list(set(union))
    union = sorted(union)
    f = open("query_category/union.txt", "w")
    f.write("".join(union))
    f.close()

query_patterns = [
    " who ",
    " whom ",
    " whose ",
    " what ",
    " which ",
    " when ",
    " where ",
    " why ",
    " how ",
    " should ",
    " would ",
    " wouldn’t ",
    " can ",
    " can’t ",
    " will ",
    " won’t ",
    " aren’t ",
    " do ",
    " does ",
    " has ",
    " have ",
    " am ",
    " are ",
    " is ",
    " shouldn’t ",
    " isn't ",
    " could ",
    " couldn’t ",
    " does ",
    " don’t ",
    " must ",
    " may ",
    " ought ",
]

def crawl_questions():
    all_results = []

    # first step using the queries only
    for pattern in query_patterns:
        output = query_and_return(pattern)
        for out in output:
            if len(out) < 15:
                continue
            if out not in all_results:
                all_results.append(out)
        print(len(all_results))
        print(all_results[-1])
    all_results = list(set(all_results))

    # then, augment the results
    past_queries = []
    for idx in tqdm(range(0, 30)):
        for result in all_results:
            prefix = result[:4 + idx*1]
            matching_patterns = [q for q in query_patterns if q in f" {prefix} "]
            if len(matching_patterns) <= 0:
                continue
            # if prefix not in query_patterns:
            #     continue
            if prefix in past_queries:
                continue
            else:
                past_queries.append(prefix)

            for i in np.arange(ord('a'), 1 + ord('z')):
                prefix1 = prefix + chr(i)
                print(f" ** {prefix1}")
                output = query_and_return(prefix1)
                # all_results.extend(output)
                for out in output:
                    if len(out) < 15:
                        print(f" ----> {out}: X")
                        continue
                    if out not in all_results:
                        all_results.append(out)
                        print(f" ----> {out}: Y")
                    else:
                        print(f" ----> {out}: X2")
                print(len(all_results))
                print(all_results[-1])
            all_results = list(set(all_results))
            all_results = sorted(all_results)
            f = open("questions_faster.txt", "w")
            f.write("\n".join(all_results))
            f.close()

import re
number_may_space = re.compile(r'\d may ')
number_may_end = re.compile(r'\d may$')
space_may_numbers = re.compile(r' may \d\d')
begin_may_numbers = re.compile(r'^may \d\d')

def crawl_questions_continue():

    # then, augment the results
    all_results = []
    with open("questions_faster3.txt") as f:
        for l in f.readlines():
            all_results.append(l.replace("\n", ""))

    past_queries = []
    for idx in tqdm(range(0, 30)):
        random.shuffle(all_results)
        for result in all_results:
            idx_cut = 35 + idx*2

            # find the index of the next space
            try:
                idx_cut = result.index(" ", idx_cut)
            except:
                print(f" ** skipping `{result}` because no space was found after index {idx_cut} . . .")
                continue

            if len(result) < idx_cut - 1:
                print(" ** skipping because it's too short")
                continue

            # skip is it is of the form `d may`, `may dd`, etc.
            if number_may_space.search(result) is not None:
                print(f" ** skipping because it matches the patten: {number_may_space}")
                continue

            if number_may_end.search(result) is not None:
                print(f" ** skipping because it matches the patten: {number_may_end}")
                continue

            if begin_may_numbers.search(result) is not None:
                print(f" ** skipping because it matches the patten: {begin_may_numbers}")
                continue

            if space_may_numbers.search(result) is not None:
                print(f" ** skipping because it matches the patten: {space_may_numbers}")
                continue


            prefix = result[:idx_cut + 1]

            # if prefix not in query_patterns:
            #     continue
            matching_patterns = [q for q in query_patterns if q in f" {prefix} "]
            if len(matching_patterns) == 0:
                print(f">>>> skipping: {l}")
                continue
            else:
                print(f"matching_patterns: {matching_patterns}")

            if prefix in past_queries:
                continue
            else:
                past_queries.append(prefix)

            for i in np.arange(ord('a'), 1 + ord('z')):
                prefix1 = prefix + chr(i)
                print(f" ** {prefix1}")
                output = query_and_return(prefix1)
                # all_results.extend(output)
                for out in output:
                    if len(out) < 15:
                        print(f" ----> {out}: X")
                        continue
                    if out not in all_results:
                        all_results.append(out)
                        print(f" ----> {out}: Y")
                    else:
                        print(f" ----> {out}: X2")
                print(len(all_results))
                # print(all_results[-1])
            all_results = list(set(all_results))
            all_results = sorted(all_results)
            f = open("questions_faster3.txt", "w")
            f.write("\n".join(all_results))
            f.close()


def clean_up_questions():
    clean_results = []
    str1 = "\n"
    with open("questions_faster2.txt") as f:
        for l in f.readlines():
            matching_patterns = [q for q in query_patterns if q in f" {l} "]

            if len(matching_patterns) > 0:
                clean_results.append(l)
            else:
                print(f">>>> skipping: {l.replace(str1, '')}")
    f = open("questions_faster2_clean.txt", "w")
    f.write("".join(clean_results))
    f.close()


if __name__ == "__main__":
    # example2()
    # query_and_save("should e")
    # query_looper()
    # bootstrap()
    # get_perspectrum_claims()
    # print_extracted_queries()
    # try_spacy()
    # write_claims()
    # count_queries_per_category()
    # crawl_questions()
    crawl_questions_continue()
    # clean_up_questions()
