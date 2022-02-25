def main():
    print("Comparisons module")

import tennis_data_manipulation as manip
import rankings
import matplotlib.pyplot as plt
import numpy as np

def compare_wta_wbw_rankings(matches, year = 2008, n_weeks = 52,
                             epsilon = 1e-4):
    """
    Assumes matches is a list of dictionaries, where each match is a dictionary.
    Year is an integer showing the beginning year from which comparisons will be made.
    N_weeks is an integer showing the number of weeks before the start date of
    a tournament that will be used to calculate the wbw ranking.
    Epsilon sets the criterion for convergence on the underlying wbw ranking
    algorithm. If it is set higher, the comparison finishes earlier.

    This function compares the rankings of players as calculated by the WTA
    with the WbW rankings taking into account the tournaments ended in the
    52 weeks previous to the start of a tournament. If the player had not played in the
    previous years, it sets its ranking to NaN.
    It returns a dictionary with three lists,
    two of them show the WbW and the WTA rankings of each player for each tournament.
    The third list shows the year in which the tournament was played.
    """
    # Here we count the matches to begin with the first match of the desired year.
    # The n_match of the whole dataset.
    n_match = 0
    for match in matches:
        if match["start_date"].date().year == year:
            break
        n_match += 1

    previous_tournament = matches[n_match]["tournament"]
    previous_start_date = matches[n_match]["start_date"]
    previous_end_date = matches[n_match]["end_date"]
    updated_ranking = rankings.wbw_ranking(matches, year = year - 1, epsilon = epsilon)[1]

    # This will serve as a basis for the comparisons between the WTA ranking and the WbW ranking.
    # Players_included will be a dictionary that stores the players that have been
    # already taken into account in the current tournament (so that we only record
    # the first time they appear in each tournament).
    comparison_dict = {"players_included": {},
                       "wta_ranking": [],
                       "wbw_ranking": [],
                       "year": []}

    # This dictionary is used to store information about players included in a
    # possibly splitted tournament.
    split_info = {}

    for match in matches[n_match:]:
        # If the current tournament is different from the previous one, we check whether
        # it might be splitted, whether we should retrieve info from a splitted tournament,
        # or if simply we should update the rankings for previous tournaments.
        # Else: We assume we continue with the same tournament, and use the
        # players already included in the dictionary.
        if match["tournament"] != previous_tournament:
            # We store the information of possible splitted tournaments.
            if manip.get_day_month(previous_end_date) == [31, 12]:
                split_info[previous_tournament] = {}
                split_info[previous_tournament]["ranking_used"] = updated_ranking
                split_info[previous_tournament]["players_included"] = comparison_dict["players_included"]

            # If it is a splitted tournament, we retrieve its information and delete it.
            if (match["tournament"] in split_info
            and manip.get_day_month(match["start_date"]) == [1, 1]):
                updated_ranking = split_info[match["tournament"]]["ranking_used"]
                comparison_dict["players_included"] = split_info[match["tournament"]]["players_included"]
                del split_info[match["tournament"]]


            # Any other different non_splitted tournament should update the ranking
            # (only if it does not share the same start_date) and renew the
            # players whose rankings should be taken into account.
            else:
                if match["start_date"] != previous_start_date:
                    updated_ranking = rankings.wbw_ranking(matches, weeks = 52, start_date = match["start_date"])[1]
                    comparison_dict["players_included"] = {}
                else:
                    comparison_dict["players_included"] = {}

            # After the first of January, tournaments cannot be splitted. Hence,
            # if there is any remaining information about splitted tournaments,
            # it should be eliminated. (.month != 12 to avoid splitted tournaments)
            # info to be destroyed in December.
            if (match["start_date"].day >= 2 and match["start_date"].month != 12
            and split_info != {}):
                split_info = {}

        # Until we do not change tournament, we continue adding to the list
        # rankings from players that have not appeared in this tournament.
        if match["player_1"] not in comparison_dict["players_included"]:
            comparison_dict["players_included"][match["player_1"]] = []
            comparison_dict["wta_ranking"].append(match["rank_1"])
            comparison_dict["year"].append(match["start_date"].date().year)
            # Check if the player has played in the last year.
            if match["player_1"] in updated_ranking:
                comparison_dict["wbw_ranking"].append(updated_ranking[match["player_1"]][1])
            # Otherwise: NaN.
            else:
                comparison_dict["wbw_ranking"].append(np.nan)

        if match["player_2"] not in comparison_dict["players_included"]:
            comparison_dict["players_included"][match["player_2"]] = []
            comparison_dict["wta_ranking"].append(match["rank_2"])
            comparison_dict["year"].append(match["start_date"].date().year)
            if match["player_2"] in updated_ranking:
                comparison_dict["wbw_ranking"].append(updated_ranking[match["player_2"]][1])
            else:
                comparison_dict["wbw_ranking"].append(np.nan)

        # Finally, we set the information to be compared for the next match.
        previous_tournament = match["tournament"]
        previous_start_date = match["start_date"]
        previous_end_date   = match["end_date"]

    # After the loop we delete the sub-dictionary that stored information about
    # the players included in the current tournament.
    del comparison_dict["players_included"]

    return comparison_dict


def plot_comparison_wbw_wta(wta_ranking_list, wbw_ranking_list, year, rescale = False):
    """
    Assumes wta_ranking_list, wbw_ranking_list and year are lists of the same length.
    Wta_ranking_list should represent the WbW and the WTA rankings of each player for each tournament.
    The year list shows the year in which the tournament was played.
    Rescale is an argument used to set a different x axis and y axis range. If set to True
    it makes both axis the same length.
    Plots a scatterplot where of WbW against WTA, assigning a color to the year in
    which the tournament was played.
    """
    # Source for the use of the legend:
    # https://matplotlib.org/stable/gallery/lines_bars_and_markers/scatter_with_legend.html
    # On changing the legend title font size:
    # https://stackoverflow.com/questions/12402561/how-to-set-font-size-of-matplotlib-axis-legend
    plt.figure(figsize = [15, 10])
    scatter = plt.scatter(x = wta_ranking_list,
                          y = wbw_ranking_list,
                          c = year,
                          alpha = 0.7)

    # We add a line to compare what would be a perfect fit.
    plt.plot([i for i in range(350)],
             [i for i in range(350)],
             color = "k",
             alpha = 0.5)

    legend = plt.legend(*scatter.legend_elements(),
                        loc = (1.04, 0),
                        title = "Year of the tournament",
                        fontsize = 14)
    legend.get_title().set_fontsize("14")
    plt.xlabel("WTA ranking",
               fontsize = 16)
    plt.ylabel("WbW ranking (52 weeks before the start of the tournament)",
               fontsize = 16)
    plt.title(("A comparison of the WTA and WbW rankings for each player per tournament\n\
    Black line shows a hypothetical perfect fit between WTA and WbW rankings"),
              fontsize = 18)
    plt.xticks(fontsize = 14)
    plt.yticks(fontsize = 14)
    if rescale == True:
        plt.xlim(-5, 360)
        plt.ylim(-5, 360)

    plt.show()


if __name__ == "__main__":
    main()
