import csv
from os import listdir
from os.path import isfile, join

def main():
    output = []
    mypath = "/Users/danielk/ideaProjects/should-X/people_also_ask/csv/"
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    for f in onlyfiles:
        print(f)
        with open(mypath + f) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=';')
            line_count = 0
            for row in csv_reader:
                print(row)
                print(len(row))
                if line_count == 0:
                    print(f'Column names are {", ".join(row)}')
                    line_count += 1
                else:
                    output.append([row[1], row[2]])
                    output.append([row[1], row[3]])
                    # print(f'\t{row[0]} works in the {row[1]} department, and was born in {row[2]}.')
                    line_count += 1
            print(f'Processed {line_count} lines.')

    output = list(set(["\t".join(x) for x in output]))
    output.sort()
    output_file = open("/Users/danielk/ideaProjects/should-X/people_also_ask/aggregated.tsv", "w+")
    for line in output:
        output_file.write(line + "\n")

if __name__ == '__main__':
    main()
