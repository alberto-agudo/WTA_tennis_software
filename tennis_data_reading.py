def main():
    print("Tennis data reading module")

import tennis_data_manipulation as manip
import tennis_rounds as rounds
import csv
from datetime import datetime as dt
import os

def get_csv_files_sorted(directory):
    """Takes a directory of the computer, where csvs are stored in '%YYYY.csv'
    format. Returns a list with the filepath to each csv, sorted by year of the csv.
    """
    # Source of os.listdir: https://stackoverflow.com/a/3207973/15459665
    files = [os.path.join(directory, file) for file in os.listdir(directory) \
             if file.endswith("csv")]
    # Here we sort the files by year, asuming %YYYY format.
    files.sort(key = lambda file: file[len(file) - 8:len(file) - 4])
    return files


def read_wta_csv(file):
    """
    Assumes that file is a csv that represents WTA matches (with one match per row
    and several variables related to the match in it).
    It reads the file, formats the output of each variable, gets the winner of each
    match and stores each row as a dictionary.
    Finally, it returns a list of dictionaries that represent all the WTA matches
    played in one year
    """
    with open(file) as f:
        header_variables = f.readline().strip().lower().replace(" ", "_").split(",")
        reader = csv.reader(f)
        matches = []
        # Source of unpacking an iterable:
        # https://realpython.com/python-zip-function/

        for line in reader:
            # Dictionary of the match
            match = dict(zip(header_variables, line))

            # Data cleaning that relies on other modules functions.
            match["start_date"] = dt.strptime(match["start_date"], "%Y-%m-%d")
            match["end_date"] = dt.strptime(match["end_date"], "%Y-%m-%d")
            match["player_1"] = match["player_1"].strip()
            match["player_2"] = match["player_2"].strip()
            match["best_of"] = int(match["best_of"])
            match["rank_1"] = manip.clean_ranking(match["rank_1"])
            match["rank_2"] = manip.clean_ranking(match["rank_2"])
            match["set_1"] = manip.clean_set(match["set_1"])
            match["set_2"] = manip.clean_set(match["set_2"])
            match["set_3"] = manip.clean_set(match["set_3"])
            match["winner"] = manip.get_winner(match)
            # Finally, it is appended to the list (list of dictionaries).
            matches.append(match)
        return matches


def read_append_all_csvs(directory, include_rounds = True):
    """
    Takes as input a directory of the computer, where csv files with the
    format '%YYYY.csv' are stored. Assumes these csv files represent matches
    from the WTA.
    The include_rounds argument asks whether the rounds of the matches should be added
    as another field of each dictionary in the list.
    It defaults to True.

    Reads and formats the csvs ordered by year, preparing the variables to be
    analyzed in the context of WTA matches, and returns a list of dictionaries
    with all of them.
    """
    all_csvs = []
    for csv_year in get_csv_files_sorted(directory):
        all_csvs.extend(read_wta_csv(csv_year))

    if include_rounds == True:
        rounds.add_round(all_csvs)

    return all_csvs

if __name__ == "__main__":
    main()
