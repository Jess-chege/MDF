"""This module contains implementations of ACT-R functions using the ccm library."""
import random
import ccm.scheduler
import ccm.pattern
ccm.pattern.basestring = str
from ccm.lib.actr import *


def chunk_to_string(chunk):
    """Converts a chunk dict to a string format."""
    chunk_copy = chunk.copy()
    if "name" in chunk_copy.keys():
        del chunk_copy["name"]
    return " ".join(list(chunk_copy.values()))


def pattern_to_string(pattern):
    """Converts a pattern dict to a string format."""
    return " ".join(list(pattern.values())[1:]).replace("-=", "!?").replace("=", "?")


def change_goal(pattern, curr_goal):
    """Modifies the goal buffer using the given pattern."""
    if curr_goal == 0:
        return {}
    curr_goal.update(pattern)
    if "buffer" in curr_goal.keys():
        del curr_goal["buffer"]
    return curr_goal


def retrieve_chunk(pattern, dm_chunks, types):
    """Retrieve a chunk from declarative memory given a pattern."""
    if pattern == {}:
        return {}
    retrieve = Buffer()
    memory = Memory(retrieve)
    for chunk in dm_chunks:
        memory.add(chunk_to_string(chunk))
    memory.sch = ccm.scheduler.Scheduler()
    matches = memory.find_matching_chunks(pattern_to_string(pattern))
    if matches == []:
        return {}
    match = matches[0]
    isa = match[0]
    retrieved = {"ISA": isa}
    for i in range(1, len(match.values())):
        retrieved[types[isa][i-1]] = match[i]
    return retrieved


def match_production(production, context):
    """Returns True if the production lhs matches the given context and adds
    the matching bindings to the production."""
    patterns = {}
    for p in production["lhs"]:
        patterns[p["buffer"]] = pattern_to_string(p)
    patt = ccm.pattern.Pattern(patterns)
    match_bindings = patt.match(context)
    if match_bindings is None:
        return False
    production["bindings"] = match_bindings
    return True


def pattern_matching_function(productions, goal, retrieval):
    """Returns the productions that match the given goal and retrieval buffers."""
    context = {
        "goal": Chunk(chunk_to_string(goal)), 
        "retrieval": Chunk(chunk_to_string(retrieval)) if retrieval != {} else None
    }
    return [p for p in productions if match_production(p, context)]
    

def conflict_resolution_function(productions):
    """ACT-R conflict resolution function. Currently selects a production at
    random from the already matched productions, since utility values and learning
    are not implemented yet."""
    if len(productions) == 0:
        return {}
    else:
        return random.choice(productions)


def update_buffer(production, buffer):
    """Returns a pattern to update the given buffer with."""
    if len(production) == 0:
        return {}
    pattern = {}
    for p in production["rhs"]:
        if p["buffer"] == buffer:
            pattern = p.copy()
    for k, v in pattern.items():
        v_name = v.replace("=", "")
        if v_name in production["bindings"].keys():
            pattern[k] = production["bindings"][v_name]
    return pattern


def update_goal(production):
    """Returns a pattern to update the goal buffer with."""
    return update_buffer(production, "goal")


def update_retrieval(production):
    """Returns a pattern to update the retrieval buffer with."""
    return update_buffer(production, "retrieval")


def check_termination(production):
    """Function used to check if no production was selected."""
    return production == {}


def get_actr_functions():
    """Returns a list of all the ACT-R functions as MDF specifications."""
    actr_funcs = []
    actr_funcs.append(
        dict(
            name="change_goal",
            description="ACT-R change goal buffer function",
            arguments=["pattern", "curr_goal"],
            expression_string="actr_functions.change_goal(pattern, curr_goal)"
        )
    )
    actr_funcs.append(
        dict(
            name="retrieve_chunk",
            description="ACT-R retrieve chunk function",
            arguments=["pattern", "dm_chunks", "types"],
            expression_string="actr_functions.retrieve_chunk(pattern, dm_chunks, types)"
        )
    )
    actr_funcs.append(
        dict(
            name="pattern_matching_function",
            description="ACT-R pattern matching function",
            arguments=["productions", "goal", "retrieval"],
            expression_string="actr_functions.pattern_matching_function(productions, goal, retrieval)"
        )
    )
    actr_funcs.append(
        dict(
            name="conflict_resolution_function",
            description="ACT-R conflict resolution function",
            arguments=["productions"],
            expression_string="actr_functions.conflict_resolution_function(productions)"
        )
    )
    actr_funcs.append(
        dict(
            name="update_goal",
            description="ACT-R update goal buffer function",
            arguments=["production"],
            expression_string="actr_functions.update_goal(production)"
        )
    )
    actr_funcs.append(
        dict(
            name="update_retrieval",
            description="ACT-R update retrieval buffer function",
            arguments=["production"],
            expression_string="actr_functions.update_retrieval(production)"
        )
    )
    actr_funcs.append(
        dict(
            name="check_termination",
            description="check_termination",
            arguments=["production"],
            expression_string="actr_functions.check_termination(production)"
        )
    )
    return actr_funcs