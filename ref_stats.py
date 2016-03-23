import csv
from collections import Counter
from datetime import datetime
import sys

filename = sys.argv[1]
reader = csv.reader(open(filename))
separator = "="*80
category_dict = {}
location_dict = {}
content_dict = {}
time_dict = {}


def add_id(fn, reader):
    f = open(fn)
    data = [item for item in csv.reader(f)]
    f.close()

    new_column = ["id"]
    for i in range(0,len(list(reader))):
        new_column.append(i)

    new_data = []

    for i, item in enumerate(data):
        try:
            item.append(new_column[i])
        except IndexError, e:
            item.append("placeholder")
        new_data.append(item)

    f = open(fn+'_id.csv', 'w')
    csv.writer(f).writerows(new_data)
    f.close()


def build_dicts(reader):
    firstline = True
    for rows in reader:
        # skip first row, it's the header.
        if firstline:
            firstline = False
            continue
        # TODO: replace timestamp key with id column value
        location_dict[datetime.strptime(rows[0], '%m/%d/%Y %H:%M:%S')] = rows[2]
        category_dict[datetime.strptime(rows[0], '%m/%d/%Y %H:%M:%S')] = rows[3]
        content_dict[datetime.strptime(rows[0], '%m/%d/%Y %H:%M:%S')] = rows[4]
        time_dict[datetime.strptime(rows[0], '%m/%d/%Y %H:%M:%S')] = rows[8]


def occurrences(input_dict):
    next(reader, None)
    category = Counter(input_dict.values())
    total = len(input_dict)
    print "Percentage\tCount\t\t\tValue"
    print "-"*10 + "\t" + "-"*5 + "\t\t\t" + "-"*5
    for c in category.most_common():
        print "{0:.0f}%".format(float(c[1])/total*100) + "\t\t\t" + str(c[1]) + ": \t\t\t" + c[0]
    print separator

# Add unique id column to csv file
add_id(filename, reader)
reader = csv.reader(open(filename+'_id.csv'))

# Build dictionaries
build_dicts(reader)

# Print out some stats
occurrences(category_dict)
occurrences(location_dict)
occurrences(time_dict)  # TODO: fill in the blank values, match based on timestamp. Update dict, not csv!

# print time_dict.keys()[0].strftime('%H')  # hour
# print time_dict.keys()[0].strftime('%A')  # weekday
