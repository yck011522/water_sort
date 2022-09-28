import argparse
import json
from copy import deepcopy

ap = argparse.ArgumentParser()
ap.add_argument("-f", "--file", default='image/595.json', help="Path to the analyzed colour group.json")
args = vars(ap.parse_args())

uniq_colors, group_lists = None, None
with open(args["file"], "r") as f:
    dict = json.load(f)
    uniq_colors = dict['uniq_colors']
    group_lists = dict['group_lists']
print("Loaded {} Lists, {} Unique Colors".format(len(group_lists), len(uniq_colors)))
assert len(group_lists) == len(uniq_colors)

# Global properties about the game board
columns = len(group_lists) + 2
height = len(group_lists[0])
initial_board_state = deepcopy(group_lists) + [[], []]

# Implementation to keep track of visited state to avoid unnecessary re-trying
visited_state_hash = set()
hash_len = 0
deepest_search = 0


def state_hash_default(state):
    '''This hashing function is just simple to implement.'''
    return hash(tuple(tuple(i) for i in state))


def state_hash_char(state):
    '''This hashing function first hash each column and then sorts them to avoid visiting equvalent boards.'''
    cols = []
    for col in state:
        cols.append(bytes(col + [255] * (height - len(col))))
    cols.sort()
    return hash(tuple(cols))


def check_state_if_visited(state, verbose=True):
    global hash_len, visited_state_hash
    h = state_hash_char(state)
    # h = state_hash_default(state)

    if h in visited_state_hash:
        return True
    else:
        visited_state_hash.add(h)
        hash_len += 1
        if verbose and hash_len % 100 == 0:
            print("hash_len = {}".format(hash_len))


def perform_action(board_state, column_fm, column_to):
    empty_space = height - len(board_state[column_to])

    # Full
    if empty_space == 0:
        return None

    # No Source
    if len(board_state[column_fm]) == 0:
        return None

    # Color Mismatch
    if len(board_state[column_to]) > 0 and board_state[column_to][-1] != board_state[column_fm][-1]:
        return None

    # Meaningless move to move a whole column set to an empty column
    if len(board_state[column_to]) == 0 and len(set(board_state[column_fm])) == 1:
        return None

    # Meaningless move when source column cannot completely move to target column / having left over
    if len(board_state[column_to]) > 0 and empty_space < height:
        target_color = board_state[column_to][-1]
        if len(board_state[column_fm]) > empty_space:
            if board_state[column_fm][-empty_space - 1] == target_color:
                return None

    # Valid Action
    new_board_state = deepcopy(board_state)
    for i in range(empty_space):
        # Move one tile
        new_board_state[column_to].append(new_board_state[column_fm].pop(-1))
        # Check if the flow continues
        if len(new_board_state[column_fm]) == 0:
            break
        if new_board_state[column_to][-1] != new_board_state[column_fm][-1]:
            break
    return new_board_state


def column_complete(column):
    if len(column) < height:
        return False
    if any(i != column[0] for i in column):
        return False
    else:
        return True


def find_possibilities(board_state):
    actions = []
    for i in range(0, columns):
        for j in range(0, columns):
            if column_complete(board_state[j]):
                # Filter out columns that are already complete
                continue
            if i == j:
                continue
            new_state = perform_action(board_state, i, j)
            if new_state is not None:
                action = (i, j)
                yield (action, new_state)


def is_solved(board_state):
    for column in board_state:
        if len(column) > 0:
            if not column_complete(column):
                return False
    return True


def search(actions, board_states, verbose=0):
    global deepest_search

    # Keep statistics
    depth = len(actions)
    if depth > deepest_search:
        deepest_search = depth
    # Avoid Infinite Loop
    if depth > 100:
        print("Action Stuck?")
        return None

    explored_actions = 0

    # Iterate through possible actions
    for (po_action, po_new_state) in find_possibilities(board_states[-1]):
        # Check if this actions results in a solved board
        if is_solved(po_new_state):
            return ([po_action], [po_new_state])
        # Check if the new action results in one that we have already been before
        if po_new_state in board_states:
            continue

        # Check if state is one that has been visited
        if check_state_if_visited(po_new_state):
            continue

        # Commit to this action and continue to search forward
        explored_actions += 1
        result = search(actions + [po_action], board_states + [po_new_state], verbose=verbose)
        if result is not None:
            deeper_actions, deeper_states = result
            return ([po_action] + deeper_actions, [po_new_state] + deeper_states)

    if verbose >= depth:
        print("Depth = {} , Explored Options = {} , hash_len = {} , actions = {}".format(depth, explored_actions, hash_len, actions))
        print("Last State:", board_states[-1])

    return None


verbose = 20
result = search([], [initial_board_state], verbose)
if result is not None:
    actions, board_states = result
    print("Solution: {} Actions :".format(len(actions)), actions)
    print("Final State:", board_states[-1])
    print("hash_len:", hash_len)
else:
    print("Solution not found")
    print("hash_len:", hash_len)
