import os
import pandas as pd

#runs fine on python 3.8.10. Not supposed to be running on the server 

main_folder = os.path.join(os.getcwd(), "data")
for user_folder in os.listdir(main_folder):
    print(user_folder+":")

    ###rename gps file(s) - define needed files
    old_file_gps = os.path.join(main_folder, user_folder, "source.csv")
    new_file_gps = os.path.join(main_folder, user_folder, "gps_samples_and_motion_score.csv")

    #rename file
    if os.path.exists(old_file_gps):
        os.rename(old_file_gps, new_file_gps)
    else:
        if os.path.exists(new_file_gps):
            print("\tFile already exists")
        else:
            print("\tNo file '"+ old_file_gps + "' found, can't rename.")



    ###convert mobility_report file(s) - define needed files
    old_file_mr = os.path.join(main_folder, user_folder, "analysis.xlsx")
    new_file_mr = os.path.join(main_folder, user_folder, "mobility_report.csv")
   
    # convert & delete file afterwards
    if os.path.exists(old_file_mr):
        read_file = pd.read_excel (old_file_mr, engine='openpyxl')
        read_file.to_csv (new_file_mr, index = None, header=True)
        os.remove(old_file_mr)
    else:
        if os.path.exists(new_file_mr):
            print("\tFile already exists")
        else:
            print("\tNo file '"+ new_file_mr + "' found, can't convert.")



    ####from Veras align_data.py file:

    # read tracks
    samples_df = pd.read_csv(new_file_gps)

    # read stops
    stops_df = pd.read_csv(os.path.join(main_folder, user_folder, "stops.csv"))

    ##convert timestamps to timezone aware format (important)
    samples_df.ts = pd.to_datetime(samples_df.ts)
    samples_df = samples_df.set_index('ts').tz_convert('Europe/Berlin').reset_index()

    stops_df.start = pd.to_datetime(stops_df.start)
    stops_df = stops_df.set_index('start').tz_convert('Europe/Berlin').reset_index()
    stops_df.stop = pd.to_datetime(stops_df.stop)
    stops_df = stops_df.set_index('stop').tz_convert('Europe/Berlin').reset_index()
    