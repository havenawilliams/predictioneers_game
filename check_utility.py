def check_utility_decreasing(round_number, round_recorder):
    '''
    This function checks whether the sum of all player utilities is decreasing in the next round.
    If this function is True, it indicates waning future utilities and the game ends.
    '''
    #Utility sum skips the first round.
    if round_number == 0:
        return False  # Can't compare with a previous round
    
    #Calculate the sum of utilities for the current round
    current_round_sum = sum(round_recorder[round_number].values())
    
    #Calculate the sum of utilities for the previous round
    previous_round_sum = sum(round_recorder[round_number - 1].values())
    
    #Check if the utility sum is decreasing
    return previous_round_sum >= current_round_sum