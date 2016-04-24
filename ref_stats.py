import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import csv
from datetime import datetime

filename = sys.argv[1]
reader = csv.reader(open(filename))

REQUEST_OBJS = []
TWO_MINS = []
FIVE_MINS = []
TEN_MINS = []
FIFTEEN_MINS = []
FIFTEEN_PLUS_MINS = []
DAY = "all"  # Enter single days in format: "02-22-2016". If you want all days , put "all".
OPEN_HOUR = 7  # 7:45 to be exact


class RequestObj(object):
    def __init__(self, location, duration_entry, question_content, time_block, datetime_obj, obj_id):
        self.day = None  # this will be changed when mins are set
        self.datetime = datetime_obj
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
        formatted_hour = this_hour - OPEN_HOUR
        this_hour_in_mins = formatted_hour * 60
        formatted_mins = this_hour_in_mins + this_min
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
            duration_unit = 20
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


def build_objs(rdr):
    obj_id = -1
    firstline = True
    for row in rdr:
        # skip first row, it's the header.
        if firstline:
            firstline = False
            continue
        location = row[2]
        duration_entry = row[3]
        question_content = row[4]
        time_block = row[8]
        time = datetime.strptime(row[0], '%m/%d/%Y %H:%M:%S')
        obj_id += 1
        REQUEST_OBJS.append(RequestObj(location,
                                       duration_entry,
                                       question_content,
                                       time_block,
                                       time,
                                       obj_id
                                       ))


def process_request_objs(list_of_request_objects):
    global DAY

    two_list = [0] * 12 * 60
    five_list = [0] * 12 * 60
    ten_list = [0] * 12 * 60
    fifteen_list = [0] * 12 * 60
    fifteen_plus_list = [0] * 12 * 60
    list_dict = {
        2: two_list,
        5: five_list,
        10: ten_list,
        15: fifteen_list,
        20: fifteen_plus_list
    }
    for obj in list_of_request_objects:
        if not DAY in [obj.day, "all"]:
            continue

        relevant_list = list_dict[obj.duration_unit]

        if relevant_list is None:
            print "Error: relvant_list is None"

        for time_unit in obj.relevant_times_list:
            # print relevant_list
            if time_unit < len(relevant_list):
                relevant_list[time_unit] += 1
            else:
                # print time_unit
                # print len(relevant_list), "\n"
                pass

    five_tuple_of_all_lists = (np.array(two_list),
                               np.array(five_list),
                               np.array(ten_list),
                               np.array(fifteen_list),
                               np.array(fifteen_plus_list)
                               )
    return five_tuple_of_all_lists


def build_chart():
    # plt.xkcd()
    two, five, ten, fifteen, fifteen_plus = process_request_objs(REQUEST_OBJS)
    x_axis_length = len(two)
    x = np.arange(x_axis_length)
    y = np.row_stack((two, five, ten, fifteen, fifteen_plus))

    plt.stackplot(x, two, color="g", colors="g")
    plt.stackplot(x, five, color="y", colors="y")
    plt.stackplot(x, ten, color="b", colors="b")
    plt.stackplot(x, fifteen, color="r", colors="red")
    plt.stackplot(x, fifteen_plus, color="000000", colors="000000")

    # The fill_between() command in stackplot creates a PolyCollection that is not supported by the legend() command.
    two_label = "1-2"
    five_label = "3-5"
    ten_label = "5-10"
    fifteen_label = "10-15"
    fifteen_plus_label = "15+"

    p1 = mpatches.Rectangle((0, 0), 1, 1, fc="g")
    p2 = mpatches.Rectangle((0, 0), 1, 1, fc="y")
    p3 = mpatches.Rectangle((0, 0), 1, 1, fc="b")
    p4 = mpatches.Rectangle((0, 0), 1, 1, fc="r")
    p5 = mpatches.Rectangle((0, 0), 1, 1, fc="000000")

    plt.legend([p1, p2, p3, p4, p5], [two_label, five_label, ten_label, fifteen_label, fifteen_plus_label])

    plt.show()


build_objs(reader)
build_chart()

# TODO: add stats output
# TODO: plot 5 charts. One for each day of the week, averaged out. Make x-axis label working hours of the day.
