# Patient Call Response Rates

 ## Overview
This repository contains a script to calculate the patient response rate to phone calls by hour, using the logs from REDCap. Only first attempt calls are considered so each call represents one patient. The time of the call is based on the timestamp when the "Phone Contact #1 Date" field was updated in REDCap. If data was not entered in real time, the time of call will not be accurate. A patient response is defined by the selection of any "Phone Contact #1 Output" except, "Left a message" or	"No answer/unable to leave VM/busy/disconnected."

## Data Source
The data source is the REDCap audit logging file, which can be exported by going to REDCap > Sidebar > Logging > Export all logging (CSV). No changes need to be made to the CSV file. 
