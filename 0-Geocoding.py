"""
This is a script to geocode patients for the recruitment research project. Patient address from the Clarity extract will be transformed into latitude and longitude coordinates.
These coordinates will then be matched up to Census block groups or tracts. This will allow for Social Vulnerability Index and Area Deprivation Index scores to be calculated.
"""

import os
import glob
import time
import arcpy
import pandas as pd
import numpy as np
from datetime import date


# import as df the most recent Clarity extract (generated at 2pm every Tuesday)
latest_clarity_extract_filepath = max(glob.iglob("INSERT_PATH\\*.csv"), key=os.path.getmtime)
clarity_extract = pd.read_csv(latest_clarity_extract_filepath)


# save copy of most recent Clarity extract to local folder or ArcGIS will crash
clarity_extract.to_csv("INSERT_PATH\\clarity_extract_copy.csv")


# remove the intermediate shapefiles / CSVs created during previous geocoding runs
old_geocoded_files = glob.glob("INSERT_PATH\\*")
for f in old_geocoded_files:
    os.remove(f)

old_combined_geoID_files = glob.glob("INSERT_PATH\\*")
for f in old_combined_geoID_files:
    os.remove(f)

old_flattened_files = glob.glob("INSERT_PATH\\*")
for f in old_flattened_files:
    os.remove(f)


def print_header(message):
    print('--------------------------------------------------------')
    print(message)
    print('--------------------------------------------------------')
    return

# print the time that the process starts
print_header('Start process')
ts = time.gmtime()
print(time.strftime("%Y-%m-%d %H:%M:%S", ts))
start_time = str((time.strftime("%Y-%m-%d %H:%M:%S", ts)))


# ensure files can be overwritten
arcpy.env.overwriteOutput = True

# use latest CSV extract from Clarity
#address_table = latest_clarity_extract_filepath
address_table = "INSERT_PATH\\clarity_extract_copy.csv"

# use locator file from StreetMaps Premium extension
address_locator = "INSERT_PATH\\USA.loc"

# specify "address_locator_col_name" : "input_file_col_name"
address_fields = ("Address address VISIBLE NONE;" +
                  "Address2 <None> VISIBLE NONE;" +
                  "Address3 <None> VISIBLE NONE;" +
                  "Neighborhood <None> VISIBLE NONE;" +
                  "City city VISIBLE NONE;" +
                  "County <None> VISIBLE NONE;" +
                  "Subregion <None> VISIBLE NONE;" +
                  "Region state VISIBLE NONE;" +
                  "Postal zip_code VISIBLE NONE;" +
                  "PostalExt <None> VISIBLE NONE;" +
                  "CountryCode <None> VISIBLE NONE")

# set location where geocoded shapefile can be written
geocode_result = "INSERT_PATH\\geocoded.shp"

# do geocoding
arcpy.GeocodeAddresses_geocoding(address_table,     # table of addresses to geocode
                                 address_locator,   # address locator used to geocode addresses
                                 address_fields,    # list of "address_locator_col_name" : "input_file_col_name"
                                 geocode_result)    # location for output geocoded shapefile



print_header('Joining Geocoded File with Census Block Group File')

# join the geocoded shp file with Census Block Group shp file
target_features = geocode_result
join_features = "INSERT_PATH\\tl_2019_06_bg.shp"
out_feature_class = "INSERT_PATH\\combined_with_geoID.shp"
arcpy.SpatialJoin_analysis(target_features,     # subset of attributes to include; dtype=Feature class
                           join_features,       # subset of attributes to include; dtype=Feature class
                           out_feature_class)   # output feature class containing attributes of target & join features



print_header('Exporting to CSV file')

# convert shp file (containing original clarity extract + geocoded data + census block group data) to CSV file
arcpy.conversion.TableToTable(in_rows="INSERT_PATH\\combined_with_geoID.shp",
                              out_path="INSERT_PATH",
                              out_name="flattened.csv")


# print the time that the process ends
print_header('End of process')
ts = time.gmtime()
print(time.strftime("%Y-%m-%d %H:%M:%S", ts))
start_time = str((time.strftime("%Y-%m-%d %H:%M:%S", ts)))


geocoded_and_merged = pd.read_csv("INSERT_PATH\\flattened.csv")

# Census TIGER docs: https://www2.census.gov/geo/pdfs/maps-data/data/tiger/tgrshp2019/TGRSHP2019_TechDoc.pdf
# ArcGIS Geocoder docs: https://pro.arcgis.com/en/pro-app/latest/help/data/streetmap-premium/geocoding-with-streetmap-premium-classic-locators-in-arcgis-pro.htm

# specify relevant columns for use in merging on Census Tract codes at a later time
useful_geocoding_cols = ['USER_study',   # patient study ID from clarity extract
                         'IN_Address',   # patient address from clarity extract
                         'IN_City',      # patient city from clarity extract
                         'IN_Region',    # patient state from clarity extract
                         'IN_Postal',    # patient zip code from clarity extract
                         'X',            # ArcGIS matched longitude
                         'Y',            # ArcGIS matched latitude
                         'Match_addr',   # ArcGIS matched address
                         'Status',       # ArcGIS match status (M-Matched, U-Unmatched, T-Tied diff locations)
                         'Score',        # ArcGIS match score (range 0-100)
                         'STATEFP',      # Census TIGER current state FIPS code
                         'COUNTYFP',     # Census TIGER current county FIPS code
                         'TRACTCE',      # Census TIGER current Census Tract code
                         'BLKGRPCE',     # Census TIGER current Block Group number
                         'GEOID']       # Census TIGER concatenation of state FIPS, county FIPS, Census Tract, and Block Group

clean_geocoded_and_merged = geocoded_and_merged.filter(useful_geocoding_cols).copy()

# rename columns for consistency
clean_geocoded_and_merged.columns = ['study_id',
                                     'INPUT_str_address',
                                     'INPUT_city',
                                     'INPUT_state',
                                     'INPUT_zip_code',
                                     'MATCH_X',
                                     'MATCH_Y',
                                     'MATCH_full_address',
                                     'MATCH_status',
                                     'MATCH_score',
                                     'STATEFP',
                                     'COUNTYFP',
                                     'TRACTCE',
                                     'BLKGRPCE',
                                     'GEOID']


# include current date in filename so the final CSV file is not overwritten
csv_file_name = str(date.today().strftime('%Y%m%d')) + '_pop_cohort_with_geoID.csv'

clean_geocoded_and_merged.to_csv("INSERT_PATH" + csv_file_name, index=False)
