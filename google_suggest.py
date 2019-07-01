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


def query_looper():
    for i in np.arange(ord('a'), 1 + ord('z')):
        # print(chr(i))
        query_and_save(f"should {chr(i)}")

def bootstrap():
    for i in np.arange(9, 40, 1):
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

def print_extracted_queries():
    nlp = spacy.load("en_core_web_sm")
    lines = get_google_query_dump()
    sentences = []
    for line in tqdm(lines):
        jsonl = json.loads(line)
        for sent in jsonl[1]:
            if len(sent) > 10 and sent.count(" ") > 2:
                doc = nlp(sent)
                verbCount = len([token for token in doc if token.pos_ == "VERB"])
                if verbCount == 0:
                    continue
                sentences.append(sent)

    f = open("queries_extracted.txt", "w")
    f.write("\n".join(sentences))
    f.close()


def try_spacy():
    sent = "cnn top 10 food country"
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(sent)
    verbCount = len([token for token in doc if token.pos_ == "VERB"])
    print(verbCount)
    print([token.pos_ for token in doc])

if __name__ == "__main__":
    # example2()
    # query_and_save("should e")
    # query_looper()
    # bootstrap()
    # get_perspectrum_claims()
    print_extracted_queries()
    # try_spacy()