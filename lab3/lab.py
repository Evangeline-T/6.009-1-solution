#!/usr/bin/env python3

import pickle
# NO ADDITIONAL IMPORTS ALLOWED!

# Note that part of your checkoff grade for this lab will be based on the
# style/clarity of your code.  As you are working through the lab, be on the
# lookout for things that would be made clearer by comments/docstrings, and for
# opportunities to rearrange aspects of your code to avoid repetition (for
# example, by introducing helper functions).


def transform_data(raw_data):
    """
    Parameters:
        raw_data : The data being input that is turned into a more useful
                   format.
        
    Returns:
        acted_with : A dictionary where each key is an actor ID, and each value 
                     is a set of the actor IDs that actor has acted with.
                     
        movie_pairings : A dictionary where each key is a film ID, and the
                         each key's value is a list of all the actors' IDs
                         that where in that film.
    """
    
    acted_with = {}
    for (a, b, c) in raw_data:
        
        if a not in acted_with:
            acted_with[a] = set()
        
        if b not in acted_with:
            acted_with[b] = set()
            
        acted_with[a].add(b)                                                   #Add value b to the a key and vice versa 
        acted_with[b].add(a)
        
    movie_pairings = {}
    for (a, b, c) in raw_data:
        if c not in movie_pairings:                                            #Add the the film key if not present, then add the actors to that film if also not already present 
            movie_pairings[c] = []
            
        if a not in movie_pairings[c]:
            movie_pairings[c].append(a)
            
        if b not in movie_pairings[c]:
            movie_pairings[c].append(b)
    
    return [acted_with, movie_pairings]



def acted_together(data, actor_id_1, actor_id_2):
    """
    Parameters : 
        data : Data that has been transformed using transform_data.
        
        actor_id_1 : An actor ID.
        
        actor_id_2 : Another actor ID.
        
    Returns:
        Returns True if actor_if_1 has acted with actor_id_2, else returns False.
    """
    
    useful_data = data[0]
    if actor_id_1 == actor_id_2:
        return True
    
    if actor_id_1 in useful_data:
        return (actor_id_2 in useful_data[actor_id_1])
    
    return False


def BFS(data, start_point, goal_function):
    """
    Parameters : 
        data : Data that has been transformed using transform_data.
        
        start_point : The actor ID that we are beginning our BFS on.
        
        goal_function : The test we are using to determine whether we have met
                        the end condition.

    Returns :
        Returns a list of the path from the start point to the ID that met the 
        end condition. If condition is never met, return None.             

    """
    
    useful_data = data[0]
    to_visit = [start_point]
    parents = {start_point: None}                                              #Create a dictionary so that every actor ID is a child of a former actor. 
    visited = parents
    i = 0                                                                      #Initialize i for this while loop to improve runtime.
        
    if goal_function(start_point):                                             #Check if the condition is met initially 
        return [start_point]
    
    while i < len(to_visit):                                                   #i has to be less than the length of to_visit, if not, then we have visited all possible nodes and not found a path.
        current_actor = to_visit[i]
        i += 1
        
        for neighbour in useful_data.get(current_actor, set()):
            if goal_function(neighbour):                                       #Check if goal is met 
                path = [current_actor, neighbour]
                
                intermediate = current_actor
                
                while parents[intermediate] != None:                           #Trackback through the parents dictionary and find the path to the actor .
                    path.insert(0, parents[intermediate])
                    intermediate = parents[intermediate]
                return path
        
            if neighbour not in visited:
                to_visit.append(neighbour)                                     #Append the neighbours of the current actor so that they get visited later.
                parents[neighbour] = current_actor                             #Add to the dictionary such that each key is the parent to the current actor. 
    return None

    


def actors_with_bacon_number(data, n):
    """
    Paramters:
        data : Data that has been transformed using transform_data.
        
        n : The bacon number we are using to determine how far our target 
            actors are.
        
    Returns:
        Returns a set of actor IDs that are a bacon number of n away from 
        Kevin Bacon.
    """
    
    useful_data = data[0]
    
    Kevin_Bacon_id = 4724
    
    if n == 0:
        return {Kevin_Bacon_id}
    
    if type(n) != int or n < 0:
        return None
    
    
    this_layer = {4724}
    parents = {4724}                                                            
    while this_layer:       
        for i in range(n): 
            next_layer = set()
            for ID in this_layer:
                for actor in useful_data[ID]:
                    if actor not in parents:
                        next_layer.add(actor)                                  #We only look at the actors who haven't come up before, and we look at who they have acted with. 
                    parents.add(ID)
            for j in next_layer:                                               #Add everyone in the next layer into parents too, because when we go back to the top of the loop they will be considered as having come up earlier. 
                if j not in parents:
                    parents.add(j)
            this_layer = next_layer
            if this_layer == set():                                            #If n is so large such that the next layer is empty, we break out of the loop. 
                break            
        return next_layer
    return set()


def bacon_path(data, actor_id):
    """
    Parameters:
        data : Data that has been transformed using transform_data.
        
        actor_id : The target actor ID that we want to find the path from Kevin
            Bacon to.
            
    Returns : 
        Returns the path in a list type from Kevin Bacon to actor_id,
        if it doens't exist, Return None. 
    """
    
    return BFS(data, 4724, lambda p: p == actor_id)                            #For our lambda function, we check if the actor id is equal to Kevin Bacons. 


def actor_to_actor_path(data, actor_id_1, actor_id_2):
    """
    Parameters:
        data : Data that has been transformed using transform_data.
        
        actor_id_1 : An actor ID.
            
        actor_id_2 : The other actor we are checking to see if a path exists 
                     with actor_id_1
            
    Returns:
        Returns the path in a list type from actor_id_1 to actor_id_2,
        if it doens't exist, Return None.
            
    """
    
    return BFS(data, actor_id_1, lambda p: p == actor_id_2)                    #For our lambda function, we check if the actor id 1 is equal to actor id 2. 


def movies_between_actors(data, actor_id_1, actor_id_2):
    """
    Parameters:
        data : Data that has been transformed using transform_data.
        
        actor_id_1 : An actor ID.
        
        actor_id_2 : The other actor we are checking to see that actor_id_1
                     has a path of films to.   
                     
    Returns:
        A sequence of films in a list that represent the path from actor_id_1 to
        actor_id_2. If it doesn't exist, return None.
    """
    movie_data = data[1]
    
    actor_to_actor = actor_to_actor_path(data, actor_id_1, actor_id_2)
    
    if actor_to_actor == None:                                                 #We know if actor_to_actor does not exist, then there cannot be a possible path of films.     
        return None
    
    movie_sequence = []
    
    for i in range(len(actor_to_actor) - 1):
        for movie in movie_data: 
            if actor_to_actor[i] in movie_data[movie] and actor_to_actor[i + 1] in movie_data[movie]:
                movie_sequence.append(movie)
    return movie_sequence
    
    
def actor_path(data, actor_id_1, goal_test_function):
    """
    Parameters:
        data : Data that has been transformed using transform_data.
        
        actor_id_1 : An actor ID
        
        goal_test_function: A function to check if actor_id_1 meets a certain
                            condition.
                            
    Returns:
        A path from actor_id_1 to another actor if goal_test_function returns
        True on actor_id_1, else Returns False
    """
    
    return BFS(data, actor_id_1, goal_test_function)
 


def actors_connecting_films(data, film1, film2):
    """
    Parameters:
        data : Data that has been transformed using transform_data.
        
        film1 : A film ID
        
        film2 : Another film ID we are checking, to see if there is a path from
                film1 to film2
                
    Returns:
        Returns a path of films in a list from film1 to film2. There exists
        an actor from film 1 such that actors that person has acted with can
        link to film2 using actor_to_actor_path.
    """
    
    movie_data = data[1]                                                       #We use the movie data dictionary this time, it has the films with actors associated with them. 
    possible_paths = []
    
    for actor1 in movie_data[film1]:
        for actor2 in movie_data[film2]:
            if actor_to_actor_path(data, actor1, actor2) != None:              #Check if there exists a path from an actor in film1 to  an actor in film2.
                possible_paths.append(actor_to_actor_path(data, actor1, actor2))
    return min(possible_paths, key = lambda p : len(p))
            
if __name__ == '__main__':
    with open('resources/small.pickle', 'rb') as f:
        smalldb = pickle.load(f)

    with open('resources/names.pickle', 'rb') as g:
        actors = pickle.load(g)
        
    with open('resources/tiny.pickle', 'rb') as h:
        tinydb = pickle.load(h)
    
    with open('resources/large.pickle', 'rb') as j:
        largedb = pickle.load(j)
        
    with open('resources/movies.pickle', 'rb') as k:
        moviesdb = pickle.load(k)
        
        
    # additional code here will be run only when lab.py is invoked directly
    # (not when imported from test.py), so this is a good place to put code
    # used, for example, to generate the results for the online questions.
    
    
    # print(actors['Abraham Benrubi'])
    # print(list(actors.keys())[list(actors.values()).index(124002)])
    # Phil_Hartman_id = actors['Phil Hartman']
    # Bill_Murray_id = actors['Bill Murray']
    # print(acted_together(transform_data(smalldb), Phil_Hartman_id, Bill_Murray_id))
    
    # Kristen_Bone_id = actors['Kristen Bone']
    # Steve_Park_id = actors['Steve Park']
    # print(acted_together(transform_data(smalldb), Kristen_Bone_id, Steve_Park_id))
    
    # actors_flipped = {value:key for key, value in actors.items()}

    # Antonia_Torrens = actors['Antonia Torrens']
    
    # bacon_path_AT = bacon_path(transform_data(largedb), Antonia_Torrens)
    # print([actors_flipped[a_id] for a_id in bacon_path_AT])
    
    # Mae_Busch = actors['Mae Busch']
    # Weeraprawat_Wongpuapan = actors['Weeraprawat Wongpuapan']
    
    # path = actor_to_actor_path(transform_data(largedb), Mae_Busch, Weeraprawat_Wongpuapan)
    # print([actors_flipped[a_id] for a_id in path])
    
    # Rainn_Wilson = actors['Rainn Wilson']
    # Sven_Batinic = actors['Sven Batinic']
    
    # path1 = movies_between_actors(transform_data(largedb), Rainn_Wilson, Sven_Batinic)
    # movies_flipped = {value:key for key, value in moviesdb.items()}
    # print([movies_flipped[a_id] for a_id in path1])
    
    pass
