def main():
    print("Tennis rounds module")

import tennis_data_manipulation as manip

def get_round_linear(rounds_from_beginning):
    """
    Assumes that rounds_from_beginning is an integer, counting rounds from the
    beginning of the tournament.
    Returns the round of a match with a string name.
    """
    rounds_dict = {1 : "First Round",
                   2 : "Second Round",
                   3 : "Third Round",
                   4 : "Fourth Round",
                   5 : "Fifth Round",
                   6 : "Sixth Round",
                   7 : "Seventh Round",
                   8 : "Eighth Round",
                   9 : "Ninth Round",
                  10 : "Tenth Round",
                  11 : "Eleventh Round",
                  12 : "Twelfth Round"}

    return rounds_dict[rounds_from_beginning]

def has_round_robin(tournament, start_date):
    """
    Assumes tournament is a string representing the name of the tournament.
    Start_date is a datetime object showing the start date of the tournament.
    Returns True if the tournament had a Round Robin in that year and False
    otherwise.
    """
    round_robin_tournaments = {
        "Sony Ericsson Championships - 2007":[],
        "Sony Ericsson Championships - 2008":[],
        "Sony Ericsson Championships - 2009":[],
        "Sony Ericsson Championships - 2010":[],
        "Sony Ericsson Championships - 2011":[],
        "Sony Ericsson Championships - 2012":[],
        "Sony Ericsson Championships - 2013":[],
        "Sony Ericsson Championships - 2014":[],
        "Sony Ericsson Championships - 2015":[],
        "Commonwealth Bank Tournament of Champions - 2009": [],
        "Qatar Airways Tournament of Champions Sofia - 2012": [],
        "Garanti Koza WTA Tournament of Champions - 2013": [],
        "Garanti Koza WTA Tournament of Champions - 2014": [],
        "BNP Paribas WTA Finals - 2016": [],
        "BNP Paribas WTA Finals - 2017": [],
        "BNP Paribas WTA Finals - 2018": [],
        "WTA Elite Trophy - 2015": [],
        "WTA Elite Trophy - 2016": [],
        "WTA Elite Trophy - 2017": [],
        "WTA Elite Trophy - 2018": [],
        "WTA Elite Trophy - 2019": [],
        "WTA Finals - 2019": [],
        "WTA Finals - 2021": [],
    }

    # Here we create a string combining the tournament name
    # and the year in which it was played.
    tournament_year = tournament + " - " + str(start_date.date().year)

    if tournament_year in round_robin_tournaments:
        return True
    else:
        return False


def get_round_forward(matches):
    """
    Assumes that matches is a list of ordered matches, which take the shape of
    a dictionary.
    Iterates through them in chronological order
    (assuming they are chronologically ordered),
    setting the round of a match based on previous observations.
    There are three possibilities:
        1) We observe a tournament that is not interrupted by observations of other
        tournaments (either in this year or splitted between New Year's Eve and New
        Year). When one winner repeats, it jumps to the next round (This does not
        affect Round Robin matches, they will be controlled for in the
        get_round_backwards function).
        2) We observe a different tournament in New Year's day that was splitted.
        We store the information of the previous
        tournament in a temporary object, and access it to retrieve the info
        from a splitted tournament, so that later we pick up where we left off.
        3) We observe a different tournament, so we start from scratch (round one). If the
        previous tournament finished on the 31st of December, we store its information.
    """
    rounds_from_beginning = 1
    previous_tournament = matches[0]["tournament"]
    previous_start_date = matches[0]["start_date"]
    previous_end_date = matches[0]["end_date"]
    winners_dict = {}
    splitted_tournaments = {}

    for match in matches:
        # First option:
        if ((previous_tournament == match["tournament"]
        and previous_start_date == match["start_date"]
        and previous_end_date == match["end_date"])
        or
        # Check for the case when the tournaments continue ordered
        # between the 31st of December and the first of January and acknowledge
        # that they are the same tournament.
        (previous_tournament == match["tournament"]
        and manip.get_day_month(previous_end_date) == [31, 12]
        and manip.get_day_month(match["start_date"]) == [1, 1])):
            if match["winner"] not in winners_dict:
                winners_dict[match["winner"]] = []
                match["round"] = get_round_linear(rounds_from_beginning)
            else:
                # If the winner repeats, we are in a different round (Round Robin
                # matches will be controlled for in the other function)
                winners_dict = {}
                winners_dict[match["winner"]] = []
                rounds_from_beginning += 1
                match["round"] = get_round_linear(rounds_from_beginning)

        # Second option
        elif (previous_tournament != match["tournament"]
        and manip.get_day_month(match["start_date"]) == [1, 1]
        and match["start_date"].date().year > 2007
        and match["tournament"] in splitted_tournaments):
            # Store info when needed
            if manip.get_day_month(previous_end_date) == [31, 12]:
                splitted_tournaments[previous_tournament] = {"winners_dict" : winners_dict,
                                                             "rounds_from_beginning": rounds_from_beginning}

            winners_dict = splitted_tournaments[match["tournament"]]["winners_dict"]
            rounds_from_beginning = splitted_tournaments[match["tournament"]]["rounds_from_beginning"]
            previous_tournament = match["tournament"]
            previous_start_date = match["start_date"]
            previous_end_date = match["end_date"]
            del splitted_tournaments[match["tournament"]]

            if match["winner"] not in winners_dict:
                winners_dict[match["winner"]] = []
                match["round"] = get_round_linear(rounds_from_beginning)

            else:
                winners_dict = {}
                winners_dict[match["winner"]] = []
                rounds_from_beginning += 1
                match["round"] = get_round_linear(rounds_from_beginning)

        # Third option:
        else:
            # Store info
            if manip.get_day_month(previous_end_date) == [31, 12]:
                splitted_tournaments[previous_tournament] = {"winners_dict" : winners_dict,
                                                             "rounds_from_beginning": rounds_from_beginning}

            previous_tournament = match["tournament"]
            previous_start_date = match["start_date"]
            previous_end_date = match["end_date"]
            winners_dict = {}
            winners_dict[match["winner"]] = []
            rounds_from_beginning = 1
            match["round"] = get_round_linear(rounds_from_beginning)



def get_round_backwards(matches):
    """
    Assumes that matches is a list of ordered matches, which take the shape of
    a dictionary.
    Iterates through them backwards in time
    (assuming they are chronologically ordered),
    setting the round of a match based on 'future' observations.
    There are three possibilities:
        1) We observe a tournament that is not interrupted by observations of other
        tournaments (either in this year or splitted between New Year and New
        Year's Eve). When the criteria for one round are satisfied it goes back
        to the previous one.
        2) Handle the cases were tournaments might be splitted between New Year
        and New Year's Eve. It stores possible information for further use,
        and it retrieves it when necessary.
        3) We observe a different tournament, so we start from scratch (Final).
    """
    n_matches_played = 0
    rounds_from_final = 0
    winners_dict = {}
    previous_tournament = matches[-1]["tournament"]
    previous_start_date = matches[-1]["start_date"]
    previous_end_date = matches[-1]["end_date"]
    splitted_tournaments = {}

    for match in matches[::-1]:

        # Before checking the cases, we store the information of a possible splitted
        # tournament in a dictionary.
        if (match["tournament"] != previous_tournament
        and manip.get_day_month(previous_start_date) == [1, 1]):
            splitted_tournaments[previous_tournament] = {"rounds_from_final": rounds_from_final,
                                                        "n_matches_played": n_matches_played}

        # First case: Either we continue with the same tournament, or we continue
        # with the same tournament in the previous year.
        # Also Second case, if the tournament was splitted, we retrieve the information
        # from previous matches.
        if (
        (match["tournament"] == previous_tournament
        and match["start_date"] == previous_start_date
        and match["end_date"] == previous_end_date )
        or
        (match["tournament"] == previous_tournament
        and manip.get_day_month(match["end_date"]) == [31, 12]
        and manip.get_day_month(previous_start_date) == [1, 1])
        or
        (match["tournament"] != previous_tournament
        and match["tournament"] in splitted_tournaments
        and manip.get_day_month(match["end_date"]) == [31, 12])):

            # Second case:
            if (manip.get_day_month(match["end_date"]) == [31, 12] and
            match["tournament"] in splitted_tournaments):

                rounds_from_final = splitted_tournaments[match["tournament"]]["rounds_from_final"]
                n_matches_played = splitted_tournaments[match["tournament"]]["n_matches_played"]
                del splitted_tournaments[match["tournament"]]


            if rounds_from_final == 0:
                match["round"] = "Final"
                rounds_from_final += 1
                final_players = {match["player_1"]:[], match["player_2"]:[]}

            # Handle the Third Place match or the Semifinals.
            elif rounds_from_final == 1:
                if match["winner"] not in final_players:
                    match["round"] = "Third Place"
                else:
                    n_matches_played += 1
                    match["round"] = "Semifinals"
                    if n_matches_played == 2:
                        rounds_from_final += 1
                        n_matches_played = 0
                        final_players = {}

            elif (rounds_from_final == 2 and
            has_round_robin(match["tournament"], match["start_date"])):
                match["round"] = "Round Robin"

            elif (rounds_from_final == 2 and not
            has_round_robin(match["tournament"], match["start_date"])):
                n_matches_played += 1
                match["round"] = "Quarterfinals"
                if n_matches_played == 4:
                    rounds_from_final += 1
                    n_matches_played = 0


        # Third case: We find a new tournament that is not splitted and does not start in New Year.
        # Hence, we start from the final again.
        else:
            match["round"] = "Final"
            rounds_from_final = 1
            final_players = {match["player_1"] : [], match["player_2"] : []}
            n_matches_played = 0



        previous_start_date = match["start_date"]
        previous_end_date = match["end_date"]
        previous_tournament = match["tournament"]


def add_round(matches):
    """
    Takes a list of dictionaries, where each dictionary stores the information
    of a match. There are several assumptions about the matches:
        1) The matches come ordered by year (i.e., no 2008 file will appear before
        another 2007 file).
        2) Each tournament comes ordered, i.e., the first match played will belong
        to the first round, while the last match played is considered the final.
        3) There are some exceptions to the previous rule. If a tournament ends
        on the 31st of December of a year and appears again beginning on the 1st
        of January of the next year, we assume that the tournament is splitted. Hence,
        the rounds played will already count (e.g., if all the matches of the first round
        finish before New Year's Eve, the matches of the following year will belong
        to the second round.)
        4) Tournaments with Round Robin have the following schema: Round Robin
        matches, the four winners of these matches play two matches of semifinals
        and the final.

    It first counts the rounds from the beginning of a tournament (First, Second,
    Third, etc.) until the next tournament begins, where it resets.
    Since this procedure cannot know what is a final or a semfinal, another procedure
    goes backwards from the end of the list, assigning finals, semifinals, quarterfinals
    and Round Robins.
    Hence, it modifies the list of matches in place, creating a new field for each
    match: 'Round'.
    """

    get_round_forward(matches)
    get_round_backwards(matches)

if __name__ == "__main__":
    main()
