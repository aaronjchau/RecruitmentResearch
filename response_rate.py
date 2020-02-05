import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt

# import logging file from REDCap (REDCap > Sidebar > Logging > Export all logging (CSV))
# NOTE: place CSV file in same location as this script, replace filename below
log = pd.read_csv('UCIInternalREDCapPCORIProject_Logging_2020-02-03_2248.csv')

# make a new df with only REDCap Patient Record Updates
log_updates = log[log['Action'].str.contains("Updated")].copy()

# make a new df with only REDCap Patient Record Updates + Phone Call 1 Attempts
log_updates_call = log_updates[log_updates['List of Data Changes OR Fields Exported'].str.contains("contact1_dt", na=False)].copy()

# convert dtype from string to datetime
log_updates_call['Time / Date'] = pd.to_datetime(log_updates_call['Time / Date'])


def convert_time(hour):
    # function to convert an int to a datetime
    return datetime.strptime(str(hour), '%H').strftime('%I:%M %p')

def get_hourly_df(hour):
    # function to return a dataframe of calls made during a given hour
    return log_updates_call[log_updates_call['Time / Date'].dt.hour == hour]

def get_hourly_calls(hour):
    # function to return the number of total calls made during a given hour
    return get_hourly_df(hour).shape[0]

def get_hourly_responses(hour):
    # function to return the number of patients who answered the phone during a given hour
    # NOTE: see REDCap Codebook for contact1_output mutliple choice keycodes ('1' is no answer, '2' is voicemail)
    all_calls_df = get_hourly_df(hour)
    responses_df = all_calls_df[(all_calls_df['List of Data Changes OR Fields Exported'].str.contains("contact1_output = '1' | contact1_output = '2'")) == False].copy()
    return responses_df.shape[0]

def get_hourly_response_rate(hour):
    # function to calculate response rate of phone calls
    try:
        rate = (get_hourly_responses(hour) / get_hourly_calls(hour))*100
        return rate
    except ZeroDivisionError:
        return 0


calls_by_hour = pd.DataFrame(columns=['Time', 'Responses', 'Total Calls', 'Response Rate'])

# calculate and store the number of responses, calls, and the response rate for each hour
for i in range(24):
    calls_by_hour.at[i, 'Time'] = convert_time(i)
    calls_by_hour.at[i, 'Responses'] = get_hourly_responses(i)
    calls_by_hour.at[i, 'Total Calls'] = get_hourly_calls(i)
    calls_by_hour.at[i, 'Response Rate'] = round(get_hourly_response_rate(i), 1)

print(calls_by_hour)


SMALL_SIZE = 9
MEDIUM_SIZE = 12
BIGGER_SIZE = 17
plt.rc('font', size=SMALL_SIZE)
plt.rc('axes', titlesize=BIGGER_SIZE)
plt.rc('axes', labelsize=MEDIUM_SIZE)
plt.rc('xtick', labelsize=SMALL_SIZE)
plt.rc('ytick', labelsize=SMALL_SIZE)
plt.rc('legend', fontsize=SMALL_SIZE)
plt.rc('figure', titlesize=BIGGER_SIZE)
plt.rc('axes', titleweight='bold')
plt.rc('axes', labelweight='bold')

plt.bar(calls_by_hour['Time'], calls_by_hour['Response Rate'], color='#00305F')
xlocs, xlabs = plt.xticks(rotation = 0)
plt.xlabel("Call Time")
plt.ylabel("Response Rate (%)")
plt.title("Patient Response Rates at Different Times of Day")
# limit time from 8am to 8pm, feel free to change as applicable
plt.xlim(8, 20)

# print the response rate above each bar
for i, v in enumerate(calls_by_hour['Response Rate']):
    plt.text(xlocs[i] - 0.15, v + 0.5, str(v))

plt.show()
