import sys
import numpy as np
import matplotlib.pyplot as plt
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
DAY = "02-23-2016"  # "02-22-2016" #if you want day to be all, put "all"
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


def build_dicts(rdr):
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


build_dicts(reader)


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


two, five, ten, fifteen, fifteen_plus = process_request_objs(REQUEST_OBJS)

x_axis_length = len(two)

x = np.arange(x_axis_length)

y = np.row_stack((two, five, ten, fifteen, fifteen_plus))

# fig, ax = plt.subplots()
# ax.stackplot(x, y, labels=('1-2', '3-5', '5-10', '10-15', '15+'))
# labels work with plot, but not with stackplot
plt.stackplot(x, two, color="blue", colors="blue")  # , label="2")
plt.stackplot(x, five, color="green", colors="green")  # , label="5")
plt.stackplot(x, ten, color="yellow", colors="yellow")  # , label="10")
plt.stackplot(x, fifteen, color="red", colors="red")  # , label="15")
plt.stackplot(x, fifteen_plus, color="000000", colors="000000")  # , label="15+")

plt.show()

# TODO: add stats output
