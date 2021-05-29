#!/usr/bin/env python3
"""6.009 Lab 6 -- Boolean satisfiability solving"""

import sys
sys.setrecursionlimit(10000)
# NO ADDITIONAL IMPORT

def find_first_unit_clause(formula):
    """
    Parameters
    ----------
    formula : Array
        A boolean formula in CNF form.

    Returns
    -------
    String
        The first variable in the unit clause, or if there are no unit clauses,
        the first variable in the formula.
    """
    
    for clause in formula:
        if len(clause) == 1:
            return clause[0][0]
    return formula[0][0][0]


def set_variable_setting(formula, setting = True):
    """
    Parameters
    ----------
    formula : Array
        A boolean formula in CNF form.
    setting : bool, optional
        The setting for the variable we are testing.
        The default is True.

    Returns
    -------
    Array
        The updated formula when the selected variable is
        propagated through.
    Dictionary
        A dictionary of the veraible we selected and what we
        set it to.
    """
    
    updated_formula = []
    variable = find_first_unit_clause(formula)  # We find the first variable in the unit clause.
    for clause in formula:
        if (variable, setting) in clause:
            continue  # If the variable and the setting we have selected is in the clause, we can skip the clause, and not add it to the updated formula.
        elif (variable, not setting) in clause:
            new_clause = []
            for literal in clause:
                if literal != (variable, not setting):
                    new_clause.append(literal)  # If the variable and opposite setting is in the clause, we can add that clause without that literal to the updated formula.
            if new_clause == []:  # If the new clause is empty, it means that both settings don't work, and the formula is invalid.
                return 'falsified', {}
            else:
                updated_formula.append(new_clause)
        else:
            updated_formula.append(clause)  # If the variable is not in the clause, we can just add the clause to the updated formula.
            
    dictionary = {variable: setting}
    return updated_formula, dictionary
    



def satisfying_assignment(formula):
    """
    Find a satisfying assignment for a given CNF formula.
    Returns that assignment if one exists, or None otherwise.

    >>> satisfying_assignment([])
    {}
    >>> x = satisfying_assignment([[('a', True), ('b', False), ('c', True)]])
    >>> x.get('a', None) is True or x.get('b', None) is False or x.get('c', None) is True
    True
    >>> satisfying_assignment([[('a', True)], [('a', False)]])
    """
    
    if len(formula) == 0:
        return dict()  # When we reach an empty formula, return an empty dictionary, and go back up the recursion.
    if formula == 'falsified':  # If the recursion returns 'falsified', return None and go back up the recursion.
        return None
    
    updated_formula, current_assignment_dict = set_variable_setting(formula)  # Pick the first thing unit clause, or thing we see, to be True, and test it.
    overall_assignment_dict = satisfying_assignment(updated_formula)
    if overall_assignment_dict != None:   # If the formula becomes empty and the overall dict becomes empty, we update it with each truth variable we set.
        overall_assignment_dict.update(current_assignment_dict)
        return overall_assignment_dict
    else:  # If the formula gets falsified, and the overall dict becomes None, we try setting the variable to false and see if it works.
        new_formula, current_assignment_dict = set_variable_setting(formula, False)
        overall_assignment_dict = satisfying_assignment(new_formula)
        if overall_assignment_dict != None:
            overall_assignment_dict.update(current_assignment_dict) 
            return overall_assignment_dict
    return None  # Return None if neither option works.
    

def CNF_of_student_preferences(student_preferences):
    """
    Parameters
    ----------
    student_preferences : Dictionary
        A mapping of students to what rooms they prefer.

    Returns
    -------
    student_preference_cnf : Array
        Students with their room preferences in CNF form.

    """
    student_preference_cnf = []
    
    for student in student_preferences:  # Iterate through each student and the rooms they prefer.
        student_clause = []
        for preference in student_preferences[student]:
            student_preference = str(student) + '_' + str(preference)  # Create the student_location and set it to true in the clause.
            student_clause.append((student_preference, True))
        student_preference_cnf.append(student_clause)  # Add each clause of student_location, True to the CNF.
    return student_preference_cnf


def all_possible_student_locations(student_preferences):
    """
    Parameters
    ----------
    student_preferences : Dictionary
        A mapping of students to what rooms they prefer.

    Returns
    -------
    locations : set
        Set of all the possible locations students can be in.
    """
    possible_locations = student_preferences.values()
    locations = set()
    for location_set in possible_locations:
        for location in location_set:
            locations.add(location)  # As we are using a set, there's no need to check if the location is already in the set.
    return locations

def student_location_combinations(student_preferences):
    """
    Parameters
    ----------
    student_preferences : Dictionary
        A mapping of students to what rooms they prefer.

    Returns
    -------
    student_combinations : Array
        All possible student_location combinations.
    """
    student_combinations = []
    all_locations = all_possible_student_locations(student_preferences)
    for student in student_preferences:
        one_student_info = []
        for location in all_locations:
            info = str(student) + '_' + str(location)  # For each individual student, give them each possible location from all locations.
            one_student_info.append(info)
        student_combinations.append(one_student_info)
    return student_combinations


def generate_subsets(student_list, n):
    """
    Parameters
    ----------
    student_list : List
        List of student_locations.
    n : Int
        Size of the subsets we want to generate.

    Returns
    -------
    List
        List of sets of all the possible subsets of size n.
    """
    if n == 1:
        return [{student} for student in student_list]  # Return a list of a set of the students currently in the list.
    else:
        sublist = []
        index = 0  # Index gets rest of the list.
        for student in student_list:
            new_subset = generate_subsets(student_list[index + 1:], n - 1)  # This will be a list of sets.
            index += 1
            for set_ in new_subset:
                combination = {student}|set_  # Add the student we are on the to the set iteratively to create all combinations.
                sublist.append(combination)
        return sublist
    
def each_student_in_one_location(student_preferences):
    """
    Parameters
    ----------
    student_preferences : Dictionary
        A mapping of students to what rooms they prefer.

    Returns
    -------
    cnf : Array
        A description of how each student can only be in one location.

    """
    student_location_combs = student_location_combinations(student_preferences)
    cnf = []
    for student in student_location_combs:
        possible_subsets = generate_subsets(student, 2)  # For each possible student_location, find another for a clause.
        for subset in possible_subsets:
            subset = list(subset)
            cnf.append([(subset[0], False), (subset[1], False)])  # For each subset of 2 student_location, set it to False.
    return cnf
    
def no_oversubscribed_locations(student_preferences, room_capacities):
    """
    Parameters
    ----------
    student_preferences : Dictionary
        A mapping of students to what rooms they prefer.
    room_capacities : Dictionary
        A dictionary mapping each location to how many students it can hold.

    Returns
    -------
    cnf : Array
        A description of how students can fill in the rooms and keep them in capacity.
    """
    cnf = []
    number_of_students = len(student_preferences)  # The number of students will be the size of the preferences.
    students = list(student_preferences.keys())
    for room in room_capacities:
        student_location = []
        for student in students:
            student_info = str(student) + '_' + str(room)
            student_location.append(student_info)  # We create a list of the number of all the students going in that room.
        room_size = room_capacities[room]
        if room_size < number_of_students:  # We only need to check if the room can't fit all the students.
            subsets = generate_subsets(student_location, room_size + 1)
            for set_ in subsets:
                set_ = list(set_)
                clause = [(set_[i], False) for i in range(len(set_))]  # Only one person does not need to be in the set if we have N + 1 people.
                cnf.append(clause)
    return cnf


def boolify_scheduling_problem(student_preferences, room_capacities):
    """
    Convert a quiz-room-scheduling problem into a Boolean formula.

    student_preferences: a dictionary mapping a student name (string) to a set
                         of room names (strings) that work for that student

    room_capacities: a dictionary mapping each room name to a positive integer
                     for how many students can fit in that room

    Returns: a CNF formula encoding the scheduling problem, as per the
             lab write-up

    We assume no student or room names contain underscores.
    """
    rules = CNF_of_student_preferences(student_preferences) + each_student_in_one_location(student_preferences) + no_oversubscribed_locations(student_preferences, room_capacities)
    return rules


if __name__ == '__main__':
    import doctest
    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    doctest.testmod(optionflags=_doctest_flags)
