def main():
    print("Tennis data manipulation module")

def clean_ranking(rank):
    """
    Assumes rank is inputted as a string with float format.
    Transforms it to float, handling the case where no ranking exists.
    """
    if rank == "":
        return float("NaN")
    else:
        return float(rank)

def clean_set(tennis_set):
    """
    Assumes the result of a set is given as a string with the format:
    Games won by player 1 - Games won by player 2.
    Transforms this string into a list [games_player_1, games_player_2]
    If the set was not played it returns NaN.
    """
    if tennis_set == "":
        return float("NaN")
    else:
        return [int(game) for game in tennis_set.split("-")]

def sum_sets(match, best_of):
    """Assumes match is given as a dictionary representing a match of the WTA.
    Also uses best_of as an integer to determine the number of sets won needed
    to win a match.
    Iterates through the sets from the last to the first until one winner is found.
    Returns the name of the winner."""
    sets_pl_1 = 0
    sets_pl_2 = 0
    last_set = best_of

    # Sum sets until one of the players wins (reaches the middle point of best of + 1).
    while sets_pl_1 < ((best_of // 2) + 1) and sets_pl_2 < ((best_of // 2) + 1):
        current_set = "set_" + str(last_set)
        if match[current_set][0] > match[current_set][1]:
            sets_pl_1 += 1
        else:
            sets_pl_2 += 1

        last_set -= 1

    if sets_pl_1 > sets_pl_2:
        return match["player_1"]
    else:
        return match["player_2"]

def get_winner(match):
    """
    Assumes match is given as a dictionary representing a match of the WTA.
    It returns the name of the winner of the match.
    If the match was completed, it checks whether the first two matches were won
    by the same player; otherwise, it sums all the numbers of sets won until
    one player satisfies the best of sets wonrequirement.
    If one player retired, the other is deemed winner.
    """
    best_of = match["best_of"]
    last_set = "set_" + str(best_of)
    previous_set = "set_" + str(best_of - 1)

    # Check for completed match
    if match["comment"].endswith("ompleted"):

        # When the same player won two consecutive matches there was no third
        # match
        if type(match[last_set]) != list:
            if match[previous_set][0] > match[previous_set][1]:
                return match["player_1"]
            else:
                return match["player_2"]

        # Otherwise, we sum the results of the three sets.
        else:
            return sum_sets(match, best_of)

    # Otherwise, one of the players retired
    else:
        if match["player_1"] == match["comment"].replace("Retired", "").strip():
            return match["player_2"]
        else:
            return match["player_1"]

def get_day_month(datetime):
    """
    Assumes datetime is a datetime object.
    Assumes datetime has been imported from the datetime module as dt.
    Returns the day and month in a list format.
    """
    return [datetime.day, datetime.month]


if __name__ == "__main__":
    main()
