import csv
from collections import Counter
from datetime import datetime
import sys
import matplotlib.pyplot as plt
import collections

filename = sys.argv[1]
reader = csv.reader(open(filename))

category_dict = {} # request duration category
location_dict = {} # request location
content_dict = {} # type of request
time_dict = {} # request timestamp

one_dict = {}  # 1-2 minute requests
three_dict = {}  # 3-5 minute requests
five_dict = {}  # 5-10 minute requests
ten_dict = {}  # 10-15 minute requests
fifteen_dict = {}  # 15+ minute requests


# Add a unique id column to a new copy of the csv file
def add_id_csv(fn, reader):
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


# Build the dictionaries
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


# Print percentage count and values for dictionaries
def occurrences(input_dict):
    next(reader, None)
    category = Counter(input_dict.values())
    total = len(input_dict)
    print "Percentage\tCount\t\t\tValue"
    print "-"*10 + "\t" + "-"*5 + "\t\t\t" + "-"*5
    for c in category.most_common():
        print "{0:.0f}%".format(float(c[1])/total*100) + "\t\t\t" + str(c[1]) + ": \t\t\t" + c[0]
    print "="*80


# Create and initialize 60 slots for each of the time slot dictionaries
# 12 time slots in a day, 5 days in a week = 60 slots
def create_plot_dicts():
    times = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    days = ['A', 'B', 'C', 'D', 'E']

    for time in times:
        for day in days:
            one_dict[day+str(time)] = 0
            three_dict[day+str(time)] = 0
            five_dict[day+str(time)] = 0
            ten_dict[day+str(time)] = 0
            fifteen_dict[day+str(time)] = 0


# Populate each time category dict's time slot with the counts of requests in that time period
def populate_plot_dicts():
    for key in category_dict:
        hour = key.hour
        day = key.weekday() # Monday is 0 and Sunday is 6
        category = category_dict.get(key)[0:3]
        timeslot = get_timeslot(day, hour)

        if timeslot[:1] != 'Z': # Ignore Saturday & Sunday for now
            if category == '1-2':
                try:
                    one_dict[timeslot] += 1
                except:
                   print 'ERROR! ***** Category: %s - Hour: %s Day: %s Timeslot: %s' % (category, hour, day, timeslot)
            elif category == '3-5':
                try:
                    three_dict[timeslot] += 1
                except:
                    print 'ERROR! ***** Category: %s - Hour: %s Day: %s Timeslot: %s' % (category, hour, day, timeslot)
            elif category == '5-1':
                try:
                    five_dict[timeslot] += 1
                except:
                    print 'ERROR! ***** Category: %s - Hour: %s Day: %s Timeslot: %s' % (category, hour, day, timeslot)
            elif category == '10-':
                try:
                    ten_dict[timeslot] += 1
                except:
                    print 'ERROR! ***** Category: %s - Hour: %s Day: %s Timeslot: %s' % (category, hour, day, timeslot)
            elif category == '15+':
                try:
                    fifteen_dict[timeslot] += 1
                except:
                    print 'ERROR! ***** Category: %s - Hour: %s Day: %s Timeslot: %s' % (category, hour, day, timeslot)


# Map the time stamp to the right group (A-E, + 0-11) = (M-F, 8am-7pm)
def get_timeslot(day, hour):
    timeslot_key = ''

    if day == 0:
        timeslot_key = 'A'
    elif day == 1:
        timeslot_key = 'B'
    elif day == 2:
        timeslot_key = 'C'
    elif day == 3:
        timeslot_key = 'D'
    elif day == 4:
        timeslot_key = 'E'
    else:
        timeslot_key = 'Z'

    if hour == 7 or hour == 8:
        timeslot_key += '0'
    elif hour == 9:
        timeslot_key += '1'
    elif hour == 10:
        timeslot_key += '2'
    elif hour == 11:
        timeslot_key += '3'
    elif hour == 12:
        timeslot_key += '4'
    elif hour == 13:
        timeslot_key += '5'
    elif hour == 14:
        timeslot_key += '6'
    elif hour == 15:
        timeslot_key += '7'
    elif hour == 16:
        timeslot_key += '8'
    elif hour == 17:
        timeslot_key += '9'
    elif hour == 18:
        timeslot_key += '10'
    elif hour == 19:
        timeslot_key += '11'

    return timeslot_key


def build_chart():
    create_plot_dicts()
    populate_plot_dicts()

    # Turn the dictionaries into OrderedDict's
    od_one = collections.OrderedDict(sorted(one_dict.items()))
    od_three = collections.OrderedDict(sorted(three_dict.items()))
    od_five = collections.OrderedDict(sorted(five_dict.items()))
    od_ten = collections.OrderedDict(sorted(ten_dict.items()))
    od_fifteen = collections.OrderedDict(sorted(fifteen_dict.items()))

    x_datetime = [datetime(2015, 1, i, j) for i in range(1, 6) for j in range(1,13)]
    print len(x_datetime)

    # Plot the chart
    plt.xkcd()

    x_axis_fifteen = range(0,len(od_fifteen.items()))
    # Use sub-plots. Plot each day (5) individually. You'll have 25 lines. 5 day for each of the 5 request types.
    # plt.subplot(511) / 521, 531, 541, 551 / number of plots, rows, demos
    # Switch chart to bar chart (vs. line)
    # Fn+alt+F7 to see useages

    plt.plot(x_datetime, od_one.values(), color='blue', label='1-2 min')
    plt.plot(x_datetime, od_three.values(), color='orange', label='3-5 min')
    plt.plot(x_datetime, od_five.values(), color='purple', label='5-10 min')
    plt.plot(x_datetime, od_ten.values(), color='green', label='10-15 min')
    plt.plot(x_datetime, od_fifteen.values(), color='red', label='15+ min')

    plt.title('Reference stats')  # Add week range in title? Date.
    plt.xlabel('Time (M-F)')
    plt.ylabel('Number of requests')

    # Add the legend
    legend = plt.legend(loc='best', shadow=True)

    # The frame is matplotlib.patches.Rectangle instance surrounding the legend.
    frame = legend.get_frame()
    frame.set_facecolor('0.90')

    # Set the font size
    for label in legend.get_texts():
        label.set_fontsize('small')

    for label in legend.get_lines():
        label.set_linewidth(1.5)  # the legend line width

    plt.show()

# Add unique id column to new csv file and use that  file
add_id_csv(filename, reader)
reader = csv.reader(open(filename+'_id.csv'))

# Build dictionaries
build_dicts(reader)

# Print out some stats
occurrences(category_dict)
occurrences(location_dict)
occurrences(time_dict)

# Initialize and populate the dictionaries for the chart
build_chart()

# How to get the hour and day of the week:
# print time_dict.keys()[0].strftime('%H')  # hour
# print time_dict.keys()[0].strftime('%A')  # weekday

