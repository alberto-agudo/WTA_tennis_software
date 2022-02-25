def main():
    print("Tennis queries module")

from datetime import datetime as dt
import tennis_rounds as rounds

def who_won(matches, tournament, year, tournament_round, order = 1):
    """
    Assumes matches is a list of dictionaries, where each dictionary is a match.
    Assumes tournament and tournament_round are strings, and year is an integer.
    Order defaults to 1, meaning that the matches dictionary will be iterated
    from its beginning until its end. The other option is -1, which will go backwards.
    Returns a string (or list of strings) with the name of the winner (or winners)
    of a certain round of a tournament.
    """
    if year < 2007 or year > 2021:
        raise ValueError("There is no data availability before 2007 or after 2021.")
    winners = []

    for match in matches[::order]:
        if (match["tournament"] == tournament
        and match["start_date"].date().year == year
        and match["round"] == tournament_round):
            # Only one winner
            if tournament_round == "Final":
                return match["winner"]
            else:
                winners.append(match["winner"])

    return winners

def who_vs_who(matches, tournament, year, tournament_round):
    """
    Assumes matches is a list of dictionaries, where each dictionary is a match.
    Assumes tournament and tournament_round are strings, and year is an integer.
    Returns a list of lists with the players of each game in a certain round of a tournament.
    """
    if year < 2007 or year > 2021:
        raise ValueError("There is no data availability before 2007 or after 2021.")
    players = []

    for match in matches:
        if (match["tournament"] == tournament
        and match["start_date"].date().year == year
        and match["round"] == tournament_round):
            players.append([match["player_1"], match["player_2"]])

    return players

def when_eliminated(matches, tournament, year, player, order = 1):
    """
    Assumes matches is a list of dictionaries, where each dictionary is a match.
    Assumes tournament and player are strings. Assumes year is an integer.
    Order defaults to 1, meaning that the matches dictionary will be iterated
    from its beginning until its end. The other option is -1, which will go backwards.
    It follows a different procedure for round robin tournaments.
    Returns a string saying the round in which the player was eliminated.
    """
    if year < 2007 or year > 2021:
        raise ValueError("There is no data availability before 2007 or after 2021.")
    winners = []


    if not rounds.has_round_robin(tournament, dt(year, 1, 1, 0, 0)):
        for match in matches[::order]:
            if (match["tournament"] == tournament
            and match["start_date"].date().year == year
            and player in [match["player_1"], match["player_2"]]):
                if player != match["winner"]:
                    return match["round"]
                elif player == match["winner"] and match["round"] == "Final":
                    return "Winner of the tournament."

            else:
                appeared_in_tournament = 0

        # This only executes after the loop has finished.
        if appeared_in_tournament == 0:
            return "Did not play in this tournament."

    else:
        rounds_from_round_robin = 0
        appeared_in_tournament = 0
        for match in matches:
            if (match["tournament"] == tournament
            and match["start_date"].date().year == year
            and player in [match["player_1"], match["player_2"]]):
                if match["round"] == "Round Robin":
                    appeared_in_tournament = 1

                elif (match["round"] == "Semifinals"
                and player != match["winner"]):
                    return match["round"]

                elif match["round"] == "Final":
                    if player != match["winner"]:
                        return match["round"]
                    else:
                        return "Winner of the tournament."

        if appeared_in_tournament == 1:
            return "Round Robin"
        else:
            return "Did not play in this tournament."


def how_many_matches_played(matches, player, tournament = None, tournament_round = None):
    """
    Assumes matches is a list of dictionaries, where each dictionary is a match.
    Assumes tournament, tournament_round and player are strings.
    Returns the number of matches a player has played of a certain round and tournament.
    """
    n_matches = 0
    if tournament != None and tournament_round != None:
        for match in matches:
            if (match["round"] == tournament_round
            and match["tournament"] == tournament
            and player in [match["player_1"], match["player_2"]]):
                n_matches += 1

    elif tournament == None:
        for match in matches:
            if (match["round"] == tournament_round
            and player in [match["player_1"], match["player_2"]]):
                n_matches += 1

    elif tournament_round == None:
        for match in matches:
            if (match["tournament"] == tournament
            and player in [match["player_1"], match["player_2"]]):
                n_matches += 1

    return n_matches

def nr_duels_played_won(matches, player_1, player_2):
    """
    Assumes matches is a list of dictionaries, where each dictionary is a match.
    Assumes player_1 and player_2 are strings with the names of WTA players
    Returns a dictionary with the total number of matches they played against
    each other, and the number of matches won by each.
    """
    n_matches = 0
    n_wins_player_1 = 0
    n_wins_player_2 = 0
    for match in matches:
        if (player_1 in [match["player_1"], match["player_2"]]
        and player_2 in [match["player_1"], match["player_2"]]):
            n_matches += 1
            if player_1 == match["winner"]:
                n_wins_player_1 += 1
            else:
                n_wins_player_2 += 1

    return {"Number of matches played against each other": n_matches,
            "Number of times " + player_1 + " won": n_wins_player_1,
            "Number of times " + player_2 + " won": n_wins_player_2,}

if __name__ == "__main__":
    main()
