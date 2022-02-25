def main():
    print("Rankings module")

from datetime import timedelta
import numpy as np

# Winners win ranking functions:
def get_winners_win_dict(matches, year = None):
    """
    Assumes matches is a list of dictionaries, where each dictionary is a match.
    Assumes these matches come ordered by date.
    Assumes year is an integer that defaults to None, it specifies whether
    the number of matches won should be computed throughout the whole dataset
    or for a particular year.
    """
    winners_dict = {}
    for match in matches:
        # Check for specific years.
        if year != None:
            # Assumes matches are chronologically ordered.
            # Matches before our year are skipped
            if match["start_date"].date().year < year:
                continue
            # We break the loop after we have finished with the matches of a year.
            elif match["start_date"].date().year > year:
                break

        # And now we include the victories of the players.
        if match["player_1"] not in winners_dict:
            winners_dict[match["player_1"]] = 0
        if match["player_2"] not in winners_dict:
            winners_dict[match["player_2"]] = 0
        if match["player_1"] == match["winner"]:
             winners_dict[match["player_1"]] += 1
        else:
             winners_dict[match["player_2"]] += 1

    return winners_dict

def winners_win_ranking(matches, year = None):
    """
    Assumes matches is a list of dictionaries, where each dictionary is a match.
    Assumes year is an integer that defaults to None, it specifies whether
    the number of matches won should be computed throughout the whole dataset
    or for a particular year.
    Returns a list of lists [[player, number of matches won, ranking]]
    ordered by ranking (which is defined as the reverse of matches won, compared
    between players).
    """
    if year != None:
        if year < 2007 or year > 2021:
            raise ValueError("There is no data availability before 2007 or after 2021.")

    ranking = 0
    winners_list = []
    winners_dict = get_winners_win_dict(matches, year)
    # Source for using winners_dict.get:
    # https://stackoverflow.com/a/3177911/15459665
    for winner in sorted(winners_dict, key = winners_dict.get, reverse = True):
        ranking += 1
        winners_list.append([winner, winners_dict[winner], ranking])

    return winners_list



# Winners don"t lose ranking functions:
def get_dict_tournaments_rounds(matches):
    """
    Assumes matches is a list of dictionaries, where each dictionary is a match.
    Returns a dictionary of dictionaries, where we can retrieve the round number
    of a round in a certain tournament.

    E.g., {"US Open":{2007: {"First Round": 1, ..., "Final": 5},
                      2008: {"Third Round": 3, "Fourth Round": 4, ..., "Final": 6]}}
    """
    tournaments_dict = {}
    n_round = 0
    for match in matches:
        if match["tournament"] in tournaments_dict:
            if match["start_date"] in tournaments_dict[match["tournament"]]:
                if match["round"] in \
                tournaments_dict[match["tournament"]][match["start_date"]]:
                    continue

            # Tournament in dictionary, but in a different year.
            else:
                tournaments_dict[match["tournament"]][match["start_date"]] = {}
                n_round = 0

        # New tournament in the dataset. In both cases (new year and new tournament)
        # we reset n_round.
        elif match["tournament"] not in tournaments_dict:
            tournaments_dict[match["tournament"]] = {}
            tournaments_dict[match["tournament"]][match["start_date"]] = {}
            n_round = 0


        # Handle the case of splitted tournaments in the following if-statements:
        if n_round == 0 and match["round"] == "Second Round":
            n_round += 2

        # Set the final at the same level of the Third Place match if there is one.
        # (Here we are assuming that the matches are chronologically ordered)
        elif (match["round"] == "Final"
        and "Third Place" in tournaments_dict[match["tournament"]][match["start_date"]]):
            n_round = tournaments_dict[match["tournament"]][match["start_date"]]["Third Place"]

        # In any other circumstance, the number of rounds increases by one.
        else:
            n_round += 1


        tournaments_dict[match["tournament"]][match["start_date"]][match["round"]] = n_round

    return tournaments_dict

def get_winners_dont_lose_dict(matches, year = None):
    """
    Assumes matches is a list of dictionaries, where each dictionary is a match.
    Assumes year is an integer that defaults to None, it specifies whether
    the number of matches won should be computed throughout the whole dataset
    or for a particular year.
    """
    winners_dict = {}
    tournaments_dict = get_dict_tournaments_rounds(matches)
    for match in matches:
        # Same procedure as in get_winners_win_dict to check for the desired year
        if year != None:
            if match["start_date"].date().year < year:
                continue
            elif match["start_date"].date().year > year:
                break

        # Initialize the player in the dict
        if match["player_1"] not in winners_dict:
            winners_dict[match["player_1"]] = 0
        if match["player_2"] not in winners_dict:
            winners_dict[match["player_2"]] = 0

        # Retrieve the match round.
        r = tournaments_dict[match["tournament"]][match["start_date"]][match["round"]]

        # Add or substract points depending on r
        if match["player_1"] == match["winner"]:
            winners_dict[match["player_1"]] += 1 * r
            winners_dict[match["player_2"]] -= 1 / r
        else:
            winners_dict[match["player_1"]] -= 1 / r
            winners_dict[match["player_2"]] += 1 * r

    return winners_dict

def winners_dont_lose_ranking(matches, year = None):
    """
    Assumes matches is a list of dictionaries, where each dictionary is a match.
    Assumes year is an integer that defaults to None, it specifies whether
    the number of matches won should be computed throughout the whole dataset
    or for a particular year.
    Returns a list of lists (player, score and ranking)
    ordered by ranking (which is defined as the reverse of score, compared
    between players). The objective of using a list is to preserve order.
    """
    if year != None:
        if year < 2007 or year > 2021:
            raise ValueError("There is no data availability before 2007 or after 2021.")

    ranking = 0
    winners_list = []
    winners_dict = get_winners_dont_lose_dict(matches, year)
    for winner in sorted(winners_dict, key = winners_dict.get, reverse = True):
        ranking += 1
        winners_list.append([winner, winners_dict[winner], ranking])

    return winners_list


# Winners beat other winners rankings
def get_wbw_dict(matches, year = None, weeks = None, start_date = None):
    """
    Assumes matches is a list of dictionaries, where each dictionary represents
    a match (ordered by date). Assumes year is an integer that shows the year in which the dictionary
    should be calculated; if set to None, it gathers information for all the years.
    Weeks (integer) and start date (datetime) are used to calculate the rankings for
    all matches ended in the previous n weeks to a certain date.
    Year should not be used together with weeks and start_date.

    This function returns a dictionary of players, showing the number of times
    they lost "n_losses" and a dictionary called "lost_to" that represents
    the players to whom they lost and how many times this happened.
    """
    if start_date != None and weeks != None and year != None:
        raise ValueError("Year parameter cannot be specified together with weeks and start_date.")
    if weeks != None and weeks <= 0:
        raise ValueError("The number of previous weeks to take into account must be positive.")
    losers_dict = {}
    if start_date != None and weeks != None:
        first_week = start_date - timedelta(weeks = weeks)
    for match in matches:
        # We use the years procedure to trim the matches.
        # Same counting as in get_winners_win_dict
        if weeks == None and start_date == None:
            if year != None:
                if match["start_date"].date().year < year:
                    continue
                elif match["start_date"].date().year > year:
                    break

        # Or the weeks procedure:
        # Since tournaments and matches are ordered,
        # it breaks the loop after surpassing the inputted
        # start date (in other words, includes tournaments ENDED
        # in the interval of the 52 weeks previous to the current start date).
        else:
            if match["end_date"] < first_week:
                continue
            elif match["end_date"] > start_date:
                break

        # If the players do not appear in the dictionary yet, we include them.
        if match["player_1"] not in losers_dict:
            losers_dict[match["player_1"]] = {}
            losers_dict[match["player_1"]]["n_losses"] = 0
            losers_dict[match["player_1"]]["lost_to"] = {}
        if match["player_2"] not in losers_dict:
            losers_dict[match["player_2"]] = {}
            losers_dict[match["player_2"]]["n_losses"] = 0
            losers_dict[match["player_2"]]["lost_to"] = {}

        # The loser adds one loss, and we create a dictionary with the players to
        # whom she has lost and the number of times this has happened.
        if match["player_1"] != match["winner"]:
            losers_dict[match["player_1"]]["n_losses"] += 1
            if match["player_2"] not in losers_dict[match["player_1"]]["lost_to"]:
                losers_dict[match["player_1"]]["lost_to"][match["player_2"]] = 1
            else:
                losers_dict[match["player_1"]]["lost_to"][match["player_2"]] += 1
        else:
            losers_dict[match["player_2"]]["n_losses"] += 1
            if match["player_1"] not in losers_dict[match["player_2"]]["lost_to"]:
                losers_dict[match["player_2"]]["lost_to"][match["player_1"]] = 1
            else:
                losers_dict[match["player_2"]]["lost_to"][match["player_1"]] += 1

    return losers_dict


def wbw_ranking(matches, year = None, weeks = None, start_date = None,
                epsilon = 1e-10, max_iterations = 150):
    """
    Assumes matches is a list of dictionaries, where each dictionary is a match.
    Year is an integer that shows the year for which the ranking should be calculated.
    Weeks (integer) and start date (datetime) are used to calculate the rankings for
    all matches ended in the previous n weeks to a certain date.
    Year should not be used together with weeks and start_date.

    Epsilon is a float used to determine the convergence criterion of the scores
    in the last algorithm. It shows the average deviation from the scores of each player
    between the previous iteration of the wbw score distribution and the current one.
    Hence, if the algorithm takes too much time or does not converge, the user can raise it.
    On the other hand, max_iterations shows the number of maximum iterations that
    the algorithm should run; it works as a stopping rule in case there is no
    convergence.

    This algorithm implements the WbW (winners beat other winners) ranking.
    It returns two objects:
    The first one is a list of lists (player, score and ranking)
    ordered by ranking (which is defined as the reverse of score, compared
    between players). The objective of using a list is to preserve order.
    The second one is a dictionary of the players, where the values are a list of
    score-ranking pairs. This is a more efficient data structure for comparison
    purposes, whereas the first one is better suited for easily finding the top n players.
    """
    if weeks == None or start_date == None:
        losers_dict = get_wbw_dict(matches, year = year)
    else:
        losers_dict = get_wbw_dict(matches, weeks = weeks, start_date = start_date)
    n_players = len(losers_dict)
    init_score = 1 / n_players

    # Now we add the initial score of the players, calculate the share of each,
    # and distribute their shares to the players to whom they have lost.
    for loser in losers_dict:
        if "score" not in losers_dict[loser]:
            losers_dict[loser]["score"] = 0

        try:
            losers_dict[loser]["share"] = (init_score /
                                           losers_dict[loser]["n_losses"])

        # If n_losses = 0, we handle the DivisionZeroError to avoid a function crash.
        except ZeroDivisionError:
            losers_dict[loser]["score"] += init_score

        # Players who lost at least once give the corresponding shares to other players:
        if losers_dict[loser]["n_losses"] != 0:
            # For each player who beat her
            for player in losers_dict[loser]["lost_to"]:
                if "score" not in losers_dict[player]:
                    losers_dict[player]["score"] = 0
                # The player adds the loser"s share * times the loser lost to the player
                losers_dict[player]["score"] += (losers_dict[loser]["share"] *
                                                losers_dict[loser]["lost_to"][player])

    # Finally, we rescale the score.
    for loser in losers_dict:
        losers_dict[loser]["score"] = ((losers_dict[loser]["score"] * 0.85) +
                                       (0.15 / n_players))

    # We repeat the previous procedure until there is minimum variation among the
    # scores of the players or a maximum level of iterations is reached.
    sd = np.inf
    n_iterations = 1
    while sd > epsilon and n_iterations < max_iterations:
        for loser in losers_dict:
            if "new_score" not in losers_dict[loser]:
                losers_dict[loser]["new_score"] = 0

            try:
                losers_dict[loser]["share"] = (losers_dict[loser]["score"] /
                                               losers_dict[loser]["n_losses"])
            except ZeroDivisionError:
                losers_dict[loser]["new_score"] += losers_dict[loser]["score"]

            # Players who lost at least once give the corresponding shares to other players:
            if losers_dict[loser]["n_losses"] != 0:
                for player in losers_dict[loser]["lost_to"]:
                    if "new_score" not in losers_dict[player]:
                        losers_dict[player]["new_score"] = 0
                    losers_dict[player]["new_score"] += (losers_dict[loser]["share"] *
                                                        losers_dict[loser]["lost_to"][player])

        # Finally, we rescale the score.
        # Here we calculate the standard deviation between
        # the previous and the current scores.
        sum_squared_differences_between_scores = 0
        ranking_dict = {}
        for loser in losers_dict:
            losers_dict[loser]["new_score"] = ((losers_dict[loser]["new_score"] * 0.85) +
                                               (0.15 / n_players))

            sum_squared_differences_between_scores += ((losers_dict[loser]["new_score"] -
                                                      losers_dict[loser]["score"]) ** 2)

            # We fix the previous score for the following iteration.
            losers_dict[loser]["score"] = losers_dict[loser]["new_score"]
            losers_dict[loser]["new_score"] = 0

            # We populate the ranking_dict that we will use later for ordering in
            # case tihs is the last iteration. The value of each key is a list,
            # the second element will be the ranking position.
            ranking_dict[loser] = [losers_dict[loser]["score"]]

        sd = (sum_squared_differences_between_scores / n_players) ** (1 / 2)
        n_iterations += 1


    # We create a list for the printing procedure, and a dictionary if we want
    # to use it for comparing rankings. (It has a higher space complexity if we create both,
    # but a lower time complexity for future tasks).
    ranking = 0
    ranking_list = []
    for loser in sorted(ranking_dict, key = ranking_dict.get, reverse = True):
        ranking += 1
        ranking_list.append([loser, ranking_dict[loser][0], ranking])
        ranking_dict[loser].append(ranking)

    return ranking_list, ranking_dict


def print_top_n_ranking(matches, ranking_function, top_n_players, year = None,
                        epsilon = 1e-10, max_iterations = 150):
    """
    Assumes matches is a list of dictionaries where each match is a dictionary.
    Assumes n_players is an integer with the number of top players (from the beginning),
    according to the winners win ranking of a certain year, to print.
    Ranking_function can take three values:
    "winners_win_ranking", "winners_dont_lose_ranking" and "wbw_ranking".
    Epsilon and max_iterations are arguments predefined for the wbw_ranking function,
    lower epsilon and higher max_iterations are stronger criteria for convergence.
    For further details, please refer to the docstring of the wbw_ranking function.
    Prints the top n_players
    """
    if ranking_function not in [winners_win_ranking,
                                winners_dont_lose_ranking,
                                wbw_ranking]:
        raise TypeError("A ranking function as specified in the docstring should be inputted.")

    elif ranking_function == winners_win_ranking:
        for winner in ranking_function(matches, year)[:top_n_players]:
                if year != None:
                    print("According to the winners win ranking,",
                          winner[0], "was the player ranked", winner[2],
                      "in", year, "with", winner[1], "games won.")
                else:
                    print("According to the winners win ranking,",
                          winner[0], "was the player ranked", winner[2],
                      "in the period 2007-2021, with", winner[1], "games won.")

    elif ranking_function == winners_dont_lose_ranking:
        for winner in ranking_function(matches, year)[:top_n_players]:
            if year != None:
                print("According to the winners don't lose ranking,",
                      winner[0], "was the player ranked", winner[2],
                  "in", year, "with a score of", str(winner[1]) + ".")
            else:
                print("According to the winners don't lose ranking,",
                      winner[0], "was the player ranked", winner[2],
                  "in the period 2007-2021, with a score of", str(winner[1]) + ".")

    elif ranking_function == wbw_ranking:
        for winner in ranking_function(matches, year = year, epsilon = epsilon,
                                       max_iterations = max_iterations)[0][:top_n_players]:
            if year != None:
                print("According to the WbW ranking,",
                      winner[0], "was the player ranked", winner[2],
                  "in", year, "with a score of", str(winner[1]) + ".")
            else:
                print("According to the WbW ranking,",
                      winner[0], "was the player ranked", winner[2],
                  "in the period 2007-2021, with a score of", str(winner[1]) + ".")


if __name__ == "__main__":
    main()
