from google_suggest import query_patterns

def main():
    with open("questions_faster3.txt") as f:
        for line in f.readlines():
            line = line.replace("\n", "")
            print(f" ** {line} -> {is_clean(line)}")

def is_clean(query):
    matching_patterns = [q for q in query_patterns if q in f" {query} "]
    if len(matching_patterns) > 0:
        return True
    else:
        return False


if __name__ == '__main__':
    main()