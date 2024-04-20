#Gather all terminal nodes
def gather_terminal_nodes(node):
    '''Takes a game's root node as an argument. Returns a list of all the game's terminal nodes.'''
    if not node.children:
        return [node]

    #Induction
    terminal_nodes = []
    for child in node.children:
        terminal_nodes.extend(gather_terminal_nodes(child))

    #Return list object
    return terminal_nodes