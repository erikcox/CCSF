import sys, csv, threading
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from datetime import datetime

# One chart for each entry. Valid input is date: "02-22-2016", all: "all", or day name: "mondays"
DAYS = ["all", "mondays", "02-22-2016"]

filename = sys.argv[1]
# filename = "times.csv" # For testing
reader = csv.reader(open(filename))

FIFTEEN_PLUS = 30 # time alloted to tasks that take "15+ minutes" in minutes
REQUEST_OBJS = []
TWO_MINS = []
FIVE_MINS = []
TEN_MINS = []
FIFTEEN_MINS = []
FIFTEEN_PLUS_MINS = []
LIST_OF_FIGURES = []
OPEN_HOUR = 7  # 7:45 to be exact
OPEN_MINUTE = 45

location_count = {}
duration_count = {}
time_block_count = {}


class RequestObj(object):
    def __init__(self, location, duration_entry, question_content, time_block, datetime_obj, obj_id):
        self.day = None  # this will be changed when mins are set
        self.datetime = datetime_obj
        self.day_of_week = datetime_obj.weekday()
        self.duration_entry = duration_entry
        self.duration_unit = self.format_duration_unit(duration_entry)
        self.min_unit = self.process_datetime_to_mins()
        self.relevant_times_list = self.return_array_of_all_relevant_times()
        self.id = obj_id

    def process_datetime_to_mins(self):
        my_datetime = self.datetime
        this_day = my_datetime.strftime('%m-%d-%Y')
        self.day = this_day
        this_min = int(my_datetime.strftime('%M'))
        this_hour = int(my_datetime.strftime('%H'))
        #print this_hour, this_min
        formatted_hour = this_hour - OPEN_HOUR
        formatted_min = this_min - OPEN_MINUTE
        this_hour_in_mins = formatted_hour * 60
        formatted_mins = this_hour_in_mins + formatted_min
        return formatted_mins

    def format_duration_unit(self, duration_entry):
        if "1-2" in duration_entry:
            duration_unit = 2
            TWO_MINS.append(self)
        elif "3-5" in duration_entry:
            duration_unit = 5
            FIVE_MINS.append(self)
        elif "5-10" in duration_entry:
            duration_unit = 10
            TEN_MINS.append(self)
        elif "10-15" in duration_entry:
            duration_unit = 15
            FIFTEEN_MINS.append(self)
        elif "15+" in duration_entry:
            duration_unit = FIFTEEN_PLUS
            FIFTEEN_PLUS_MINS = []
        else:
            print "Error: improperly formatted duration entry:", self.datetime, duration_entry
            duration_unit = 1
        return duration_unit

    def return_array_of_all_relevant_times(self):
        relevant_times = [self.min_unit]
        for i in range(self.duration_unit):
            relevant_times.append(self.min_unit + i + 1)
        return relevant_times


def get_duration(t):
    hour = int(t.strftime('%H'))

    if hour == 7 or hour == 8:
        return '7:45-9:00 am'
    elif hour == 9:
        return '9-10 am'
    elif hour == 10:
        return '10-11 am'
    elif hour == 11:
        return '11 am-12 pm'
    elif hour == 12:
        return '12-1 pm'
    elif hour == 13:
        return '1-2 pm'
    elif hour == 14:
        return '2-3 pm'
    elif hour == 15:
        return '3-4 pm'
    elif hour == 16:
        return '4-5 pm'
    elif hour == 17:
        return '5-6 pm'
    elif hour == 18:
        return '6-7 pm'
    elif hour == 19:
        return '7-7:45 pm'
    else:
        return ''


def build_objs(spreadsheet):
    obj_id = -1
    firstline = True
    for row in spreadsheet:
        # Skip the first row, it's the header.
        if firstline:
            firstline = False
            continue

        location = row[2]
        duration_entry = row[3]
        question_content = row[4]
        time = datetime.strptime(row[0], '%m/%d/%Y %H:%M:%S')
        time_block = row[8] if len(row[8]) > 0 else get_duration(time)

        REQUEST_OBJS.append(RequestObj(location,
                                       duration_entry,
                                       question_content,
                                       time_block,
                                       time,
                                       obj_id
                                       ))
        obj_id += 1

        # Create dicts of counts for stats
        # TODO: move this into a stats function and build counts based only on time frame (not all data)
        location_count[location] = location_count.get(location, 1) + 1
        duration_count[duration_entry] = duration_count.get(duration_entry, 1) + 1
        time_block_count[time_block] = time_block_count.get(time_block, 1) + 1


def create_graph_for_day(day):
    global REQUEST_OBJS

    target_day_of_week = None
    if day in ["mondays", "tuesdays", "wednesdays", "thursdays", "fridays", "saturdays"]:
        if day in ["mondays"]:
            target_day_of_week = 0
        elif day in ["tuesdays"]:
            target_day_of_week = 1
        elif day in ["wednesdays"]:
            target_day_of_week = 2
        elif day in ["thursdays"]:
            target_day_of_week = 3
        elif day in ["fridays"]:
            target_day_of_week = 4
        elif day in ["saturdays"]:
            target_day_of_week = 5

    two_list = [0] * 12 * 60
    five_list = [0] * 12 * 60
    ten_list = [0] * 12 * 60
    fifteen_list = [0] * 12 * 60
    fifteen_plus_list = [0] * 12 * 60
    list_of_duration_lists = [two_list, five_list, ten_list, fifteen_list, fifteen_plus_list]

    list_dict = {
        2: two_list,
        5: five_list,
        10: ten_list,
        15: fifteen_list,
        FIFTEEN_PLUS: fifteen_plus_list
    }
    days_included_in_screen_set = set([])
    total_days_in_screen = None
    for obj in REQUEST_OBJS:
        if day == "all":
            pass
        elif target_day_of_week is not None:
            if obj.day_of_week != target_day_of_week:
                continue
        elif day != obj.day:
            continue
        elif day == obj.day:
            pass
        else:
            print "Error: day variable improperly formatted"

        relevant_duration_list = list_dict[obj.duration_unit]

        days_included_in_screen_set.add(obj.day)
        total_days_in_screen = len(days_included_in_screen_set)

        if relevant_duration_list is None:
            print "Error: relvant_list is None"

        for time_unit in obj.relevant_times_list:
            #print relevant_duration_list
            if time_unit < len(relevant_duration_list):
                relevant_duration_list[time_unit] += 1
            else:
                #print time_unit, len(relevant_duration_list), "\n"
                pass

    if total_days_in_screen:
        total_days_in_screen = float(total_days_in_screen)
        two_list = [x / total_days_in_screen for x in two_list]
        five_list = [x / total_days_in_screen for x in five_list]
        ten_list = [x / total_days_in_screen for x in ten_list]
        fifteen_list = [x / total_days_in_screen for x in fifteen_list]
        fifteen_plus_list = [x / total_days_in_screen for x in fifteen_plus_list]

    two     = np.array(two_list)
    five    = np.array(five_list),
    ten     = np.array(ten_list),
    fifteen = np.array(fifteen_list),
    fifteen_plus = np.array(fifteen_plus_list)

    x_axis_length = len(two)

    x = np.arange(x_axis_length)

    y = np.row_stack((two, five, ten, fifteen, fifteen_plus))

    plt.figure(DAYS.index(day))

    plt.stackplot(x, two, color="limegreen", colors="g")
    plt.stackplot(x, five, color="b", colors="b")
    plt.stackplot(x, ten, color="yellow", colors="yellow")
    plt.stackplot(x, fifteen, color="r", colors="r")
    plt.stackplot(x, fifteen_plus, color="dimgray", colors="k") # k = black
    plt.suptitle(str.title(day), fontsize=22)

    # Build legend
    # The fill_between() command in stackplot creates a PolyCollection that is not supported by the legend() command,
    # therefore we have to manually build it

    two_label = "1-2"
    five_label = "3-5"
    ten_label = "5-10"
    fifteen_label = "10-15"
    fifteen_plus_label = "15+"

    label1 = mpatches.Rectangle((0, 0), 1, 1, fc="g")
    label2 = mpatches.Rectangle((0, 0), 1, 1, fc="b")
    label3 = mpatches.Rectangle((0, 0), 1, 1, fc="yellow")
    label4 = mpatches.Rectangle((0, 0), 1, 1, fc="r")
    label5 = mpatches.Rectangle((0, 0), 1, 1, fc="k") # k = black

    plt.legend([label1, label2, label3, label4, label5],
               [two_label, five_label, ten_label, fifteen_label, fifteen_plus_label], loc='best', shadow=True)

    locs, labels = plt.xticks()
    #print(locs, labels)

    plt.xticks( np.arange(8),
           (
            "7:45",
            "9:25",
            "11:05",
            "12:45",
            "2:25",
            "4:05",
            "5:45",
            "7:25",
            ) )

    #print labels
    plt.xticks(locs, labels)
    plt.xlim(0, 720)




def build_chart():
    for day in reversed(DAYS):
        create_graph_for_day(day)
    plt.show()


def print_stats():
    dicts = (time_block_count.items(), location_count.items(), duration_count.items())
    total = 0
    # TODO: order the output of timeblocks, durations, and location properly
    # Currently sorting by highest count
    for d in dicts:
        for i in d:
            total += int(i[1])

        print '#' * 100
        for k, v in sorted(d, key=lambda x: int(x[1]), reverse=True):
            print k[:11], "\t--->  Percent: ", "{0:.0f}%".format(float(v) / total * 100), "--->  Count: ", v

    print '#' * 100

def convert_time_unit_to_time(raw_minute):
    #start at 7:45 = 0, so we need to subtract
    raw = raw_minute
    if raw < 15:
        h, m = -1, 45+raw
    zeroed = raw - 15 # set the minute to 0
    h, m = divmod(zeroed, 60)
    h = h+8
    if h > 12:
        h = h - 12
    if m < 10:
        return str(h)+":0"+str(m)
    else:
        return str(h)+":"+str(m)


build_objs(reader)
print_stats()
build_chart()


# TODO: Enhance stats output and add it to bottom of charts
# TODO: account for Friday's closing early and  being open on Saturdays.
# FALL & SPRING SEMESTER HOURS
# Monday - Thursday: 7:45am - 7:45pm
# Friday: 7:45am - 2:45pm
# Saturday: 10am - 1:45pm
# Sunday: Closed
