#!/usr/bin/env python3

from util import read_osm_data, great_circle_distance, to_local_kml_url

# NO ADDITIONAL IMPORTS!

def build_auxiliary_structures(nodes_filename, ways_filename):
    """
    Return dictionaries of useful information
    
    Parameters:
        nodes_filename: The filename for the nodes file we are looking at
        ways_filename: The filename for the ways file we are looking at
        
    Returns:
        a list of dictionaries that will be useful in later functions
    """
    
    ALLOWED_HIGHWAY_TYPES = {
    'motorway', 'trunk', 'primary', 'secondary', 'tertiary', 'unclassified',
    'residential', 'living_street', 'motorway_link', 'trunk_link',
    'primary_link', 'secondary_link', 'tertiary_link',
    }


    DEFAULT_SPEED_LIMIT_MPH = {
    'motorway': 60,
    'trunk': 45,
    'primary': 35,
    'secondary': 30,
    'residential': 25,
    'tertiary': 25,
    'unclassified': 25,
    'living_street': 10,
    'motorway_link': 30,
    'trunk_link': 30,
    'primary_link': 30,
    'secondary_link': 30,
    'tertiary_link': 25,
    }
    distance_between_nodes = {}
    neighbouring_nodes = {}
    speed_between_nodes = {}
    
    node_id_to_node = {}  # Build a dictionary where every id is mapped to it's data, so we can use a dictionary to call id's data.
    
    for node in read_osm_data(nodes_filename):
        node_id_to_node[node['id']] = node
    
    for way in read_osm_data(ways_filename):
        tags = way['tags']
        nodes = way['nodes']
        if 'highway' in tags and tags['highway'] in ALLOWED_HIGHWAY_TYPES:  # Make sure we are using valid ways.
            for i in range(len(way['nodes']) - 1):
                    
                # Building the distance between nodes dictionary
                
                    lat1 = node_id_to_node[nodes[i]]['lat']
                    lon1 = node_id_to_node[nodes[i]]['lon']
    
                                        
                    lat2 = node_id_to_node[nodes[i + 1]]['lat']
                    lon2 = node_id_to_node[nodes[i + 1]]['lon']
    
                    distance = great_circle_distance((lat1, lon1), (lat2, lon2))
                
                    if 'oneway' in tags and tags['oneway'] == 'yes':
                        distance_between_nodes[(nodes[i], nodes[i + 1])] = distance
                        if i == len(nodes) - 2 and nodes[i + 1] not in neighbouring_nodes:
                            neighbouring_nodes[nodes[i + 1]] = set()
                    elif 'oneway' not in tags or tags['oneway'] == 'no':
                        distance_between_nodes[(nodes[i], nodes[i + 1])] = distance
                        distance_between_nodes[(nodes[i + 1], nodes[i])] = distance  # For two way paths, add the key value pair of both a -> b and b -> a to the dict.         
                
                 # Building the neighouring nodes dictionary
    
                    if 'oneway' in tags and tags['oneway'] == 'yes':
                        if nodes[i] not in neighbouring_nodes:
                            neighbouring_nodes[nodes[i]] = set()
                        neighbouring_nodes[nodes[i]].add(nodes[i + 1])  # Add the node as a key if it doesn't exist, then add the neighbouring node as it's value.
                                    
                    elif 'oneway' not in tags or tags['oneway'] == 'no':
                        if nodes[i] not in neighbouring_nodes:
                            neighbouring_nodes[nodes[i]] = set()
                        if nodes[i + 1] not in neighbouring_nodes:
                            neighbouring_nodes[nodes[i + 1]] = set()
                            
                        neighbouring_nodes[nodes[i]].add(nodes[i + 1])
                        neighbouring_nodes[nodes[i + 1]].add(nodes[i])  # For two way paths, add the key value pair of both a -> b and b -> a to the dict.
                        
                # Building speed between nodes dictionary
                                
                    if 'maxspeed_mph' in tags and 'oneway' in tags and tags['oneway'] == 'yes':
                        if (nodes[i], nodes[i + 1]) not in speed_between_nodes:
                            speed_between_nodes[(nodes[i], nodes[i + 1])] = 0
                                
                        if tags['maxspeed_mph'] > speed_between_nodes[(nodes[i], nodes[i + 1])]:
                            speed_between_nodes[(nodes[i], nodes[i + 1])] = tags['maxspeed_mph']
                            
                    elif 'maxspeed_mph' in tags and ('oneway' not in tags or tags['oneway'] == 'no'):
                        if (nodes[i], nodes[i + 1]) not in speed_between_nodes:
                            speed_between_nodes[(nodes[i], nodes[i + 1])] = 0
                            
                        if (nodes[i + 1], nodes[i]) not in speed_between_nodes:
                            speed_between_nodes[(nodes[i + 1], nodes[i])] = 0
                            
                        if tags['maxspeed_mph'] > speed_between_nodes[(nodes[i], nodes[i + 1])]:
                            speed_between_nodes[(nodes[i], nodes[i + 1])] = tags['maxspeed_mph']
                            
                        if tags['maxspeed_mph'] > speed_between_nodes[(nodes[i + 1], nodes[i])]:
                            speed_between_nodes[(nodes[i + 1], nodes[i])] = tags['maxspeed_mph']
                        
                    elif 'maxspeed_mph' not in tags:
                        highway_type = tags['highway']
                        speed = DEFAULT_SPEED_LIMIT_MPH[highway_type]
                        
                        if 'oneway' in tags and tags['oneway'] == 'yes':
                            if (nodes[i], nodes[i + 1]) not in speed_between_nodes:
                                speed_between_nodes[(nodes[i], nodes[i + 1])] = 0
                                
                            if speed > speed_between_nodes[(nodes[i], nodes[i + 1])]:
                                speed_between_nodes[(nodes[i], nodes[i + 1])] = speed
                                    
                        elif 'oneway' not in tags or tags['oneway'] == 'no':
                            if (nodes[i], nodes[i + 1]) not in speed_between_nodes:
                                speed_between_nodes[(nodes[i], nodes[i + 1])] = 0
                                
                            if (nodes[i + 1], nodes[i]) not in speed_between_nodes:
                                speed_between_nodes[(nodes[i + 1], nodes[i])] = 0
                                
                            if speed > speed_between_nodes[(nodes[i], nodes[i + 1])]:
                                speed_between_nodes[(nodes[i], nodes[i + 1])] = speed
                                
                            if speed > speed_between_nodes[(nodes[i + 1], nodes[i])]:
                                speed_between_nodes[(nodes[i + 1], nodes[i])] = speed
        
    return [distance_between_nodes, neighbouring_nodes, speed_between_nodes, node_id_to_node]      


def find_short_path_nodes(aux_structures, node1, node2, fast = False):
    """
    Return the shortest path between the two nodes

    Parameters:
        aux_structures: the result of calling build_auxiliary_structures
        node1: node representing the start location
        node2: node representing the end location

    Returns:
        a list of node IDs representing the shortest path (in terms of
        distance) from node1 to node2
    """
    distance_between_nodes = aux_structures[0]
    neighbouring_nodes = aux_structures[1]
    speed_between_nodes = aux_structures[2]
    node_id_to_node = aux_structures[3]
    
    agenda = {0 :[node1]}
    
    expanded = set()
    
    if node1 == node2:
        return [node1]
    
    while agenda:
        lowest = min(agenda)
        current_path = agenda[lowest]  # The current path we look at is the one with the lowest cost, so the first in the agenda. 
        current_cost = lowest  # We then remove that path and save it's current cost.
        del agenda[lowest]

        if current_path[-1] == node2:
            return current_path
        
        if current_path[-1] in expanded:  # If the most recent node has been seen before, we can move to the next path. 
            continue
        else:
            expanded.add(current_path[-1])
        
        if neighbouring_nodes[current_path[-1]] == set(): # If the most recent node of current path is empty, we are at a dead end, and look at the next path.
            continue
        
        # former_heuristic_factor = great_circle_distance((node_id_to_node[current_path[-1]]['lat'], node_id_to_node[current_path[-1]]['lon']), (node_id_to_node[node2]['lat'], node_id_to_node[node2]['lon']))
        
        if fast:
            for node in neighbouring_nodes[current_path[-1]]:
                 if node not in expanded:
                    new_path = current_path + [node]  # We extend the current path with the most recent nodes' neighbours.
                    distance = distance_between_nodes[(current_path[-1], node)]
                    speed = speed_between_nodes[(current_path[-1], node)]  
                    time = distance/speed
                    #heuristic_speed = 70
                    
                    #former_distance = great_circle_distance((node_id_to_node[current_path[-1]]['lat'], node_id_to_node[current_path[-1]]['lon']), (node_id_to_node[node2]['lat'], node_id_to_node[node2]['lon']))
                    #former_time = former_distance/heuristic_speed
                    
                    #new_distance = great_circle_distance((node_id_to_node[node]['lat'], node_id_to_node[node]['lon']), (node_id_to_node[node2]['lat'], node_id_to_node[node2]['lon']))
                    #heuristic_time = new_distance/heuristic_speed
                    
                    new_time = current_cost + time #+ heuristic_time - former_time # Work out the time for the new path
                    agenda[new_time] =  new_path  # We add this path and cost back to the agenda. 
        
        else:
            for node in neighbouring_nodes[current_path[-1]]:
                if node not in expanded:
                    new_path = current_path + [node]  # We extend the current path with the most recent nodes' neighbours.
                    cost = distance_between_nodes[(current_path[-1], node)]  # We can work out the cost to move to this node.
                    heuristic_factor = great_circle_distance((node_id_to_node[node]['lat'], node_id_to_node[node]['lon']), (node_id_to_node[node2]['lat'], node_id_to_node[node2]['lon']))
                    former_heuristic_factor = great_circle_distance((node_id_to_node[current_path[-1]]['lat'], node_id_to_node[current_path[-1]]['lon']), (node_id_to_node[node2]['lat'], node_id_to_node[node2]['lon']))
                    new_cost = current_cost + cost + heuristic_factor - former_heuristic_factor
                    agenda[new_cost] = new_path  # We add this path and cost back to the agenda. 
        
    return None

def closest_node(aux_structures, loc1):
    """
    Returns the closest valid node to loc1
    
    Parameters:
        aux_structures : the result of calling build_auxiliary_structures
        loc1: the location we are trying to find the closest valid node to
        
        
    Returns:
        the node closest to loc1 that is also valid.    
    """
    neighbouring_nodes = aux_structures[1]
    node_id_to_node = aux_structures[3]
    
    smallest_distance = 1000000000  # Set this to a number so large such that no two nodes could be this far apart (I'm certain this number is larger than the distance from the sun to the Earth)
    for node in neighbouring_nodes:
        if (node_id_to_node[node]['lat'], node_id_to_node[node]['lon']) == loc1:  # If the location we are looking at is already known, return it
            return node
        if neighbouring_nodes[node] != set():
            current_distance = great_circle_distance(loc1, (node_id_to_node[node]['lat'], node_id_to_node[node]['lon']))
            if current_distance <= smallest_distance:
                smallest_node = node  # Keep track of the node currently corresponding to the closest node to the location
                smallest_distance = current_distance
    return smallest_node
        
def find_short_path(aux_structures, loc1, loc2):
    """
    Return the shortest path between the two locations

    Parameters:
        aux_structures: the result of calling build_auxiliary_structures
        loc1: tuple of 2 floats: (latitude, longitude), representing the start
              location
        loc2: tuple of 2 floats: (latitude, longitude), representing the end
              location

    Returns:
        a list of (latitude, longitude) tuples representing the shortest path
        (in terms of distance) from loc1 to loc2.
    """
    node_id_to_node = aux_structures[3]
    
    start_node = closest_node(aux_structures, loc1)
    end_node = closest_node(aux_structures, loc2)
    
    smallest_path = find_short_path_nodes(aux_structures, start_node, end_node)  # Work out the path from the node closest to the start to the node closest to the end
    
    if smallest_path == None:
        return None
    
    path = []
    
    for node in smallest_path:
        path.append((node_id_to_node[node]['lat'], node_id_to_node[node]['lon']))
        
    return path

def find_fast_path(aux_structures, loc1, loc2):
    """
    Return the shortest path between the two locations, in terms of expected
    time (taking into account speed limits).

    Parameters:
        aux_structures: the result of calling build_auxiliary_structures
        loc1: tuple of 2 floats: (latitude, longitude), representing the start
              location
        loc2: tuple of 2 floats: (latitude, longitude), representing the end
              location

    Returns:
        a list of (latitude, longitude) tuples representing the shortest path
        (in terms of time) from loc1 to loc2.
    """
    
    node_id_to_node = aux_structures[3]
    
    start_node = closest_node(aux_structures, loc1)
    end_node = closest_node(aux_structures, loc2)
    
    fastest_path =  find_short_path_nodes(aux_structures, start_node, end_node, fast = True)
    
    if fastest_path == None:
        return None
    
    path = []
    
    for node in fastest_path:
        path.append((node_id_to_node[node]['lat'], node_id_to_node[node]['lon']))
        
    return path    
    
if __name__ == '__main__':
    # additional code here will be run only when lab.py is invoked directly
    # (not when imported from test.py), so this is a good place to put code
    # used, for example, to generate the results for the online questions.
    
    # j = 0
    # for i in read_osm_data('resources/cambridge.nodes'):
    #     j += 1
    # print(j)
       
    # count1 = 0
    # for node in read_osm_data('resources/cambridge.nodes'):
    #     if 'name' in node['tags']:
    #         count1 += 1
    # print(count1)
    
    # for node in read_osm_data('resources/cambridge.nodes'):
    #     for key in node['tags']:
    #         if '77 Massachusetts Ave' in node['tags'][key]:
    #             print(node['id'])
    
    # j = 0
    # for i in read_osm_data('resources/cambridge.ways'):
    #     j += 1
    # print(j)
    
    # count2 = 0
    # for way in read_osm_data('resources/cambridge.ways'):
    #     tags = way['tags']
    #     tag_keys = tags.keys()
    #     if 'oneway' in tag_keys:
    #         if tags['oneway'] == 'yes':
    #             count2 += 1
    # print(count2)
    
    # for node in read_osm_data('resources/midwest.ways'):
    #     if node['id'] == 21705939:
    #         node1 = node['nodes']
    
    # total_distance = 0
    # for i in range(len(node1) - 1):
    #     for node in read_osm_data('resources/midwest.nodes'):
    #         if node['id'] == node1[i]:
    #             lat1 = node['lat']
    #             lon1 = node['lon']
                            
    #     for node in read_osm_data('resources/midwest.nodes'):    
    #         if node['id'] == node1[i + 1]:
    #             lat2 = node['lat']
    #             lon2 = node['lon']
            
    #     total_distance += great_circle_distance((lat1, lon1), (lat2, lon2))
    # print(total_distance)
    
    # midwest_data = build_auxiliary_structures('resources/midwest.nodes', 'resources/midwest.ways')
    # print(closest_node(midwest_data, (41.4452463, -89.3161394)))
    
    
    
    # I found how many times we iterated through by setting a count = 0 at the before the BFS, and
    # then doing += 1 for every time we popped something from agenda
    # cambridge_data = build_auxiliary_structures('resources/cambridge.nodes', 'resources/cambridge.ways')
    # loc1 = (42.3858, -71.0783)
    # loc2 = (42.5465, -71.1787)
    # print(find_short_path(cambridge_data, loc1, loc2))  # Without heuristic
    # ans = 688128
    
    # loc1 = (42.3858, -71.0783)
    # loc2 = (42.5465, -71.1787)
    # print(find_short_path(cambridge_data, loc1, loc2))   # With heuristic
    # ans = 85579
    pass
