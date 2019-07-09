import json
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
        "should ",
        "shouldn't ",
        "should not ",
        "why should ",
        "why shouldn't ",
        "why should not ",
        "reasons why ",
        "good reasons why ",
        "pros and cons of ",
        " facts why ",
        "reasons on why ",
        "reasons for ",
        "reasons to ",
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
        f = open("query_category/" + query_pattern.replace(" ", "_") + ".txt", "w")
        f.write("\n".join(selected))
        f.close()
        print(f" * number of queries in the category `{query_pattern}` is {len(selected)}")
        for q in selected:
            if q not in union:
                union.append(q)
    f = open("query_category/union.txt", "w")
    f.write("\n".join(union))
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
    count_queries_per_category()