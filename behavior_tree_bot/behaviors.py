import sys
sys.path.insert(0, '../')
from planet_wars import issue_order
import logging
import math


def attack_weakest_enemy_planet(state):
    #(1) Create an interable list of all my planets, sorted by their number of ships.
    my_planets = iter(sorted(state.my_planets(), key=lambda p: p.num_ships))

    #(2) Create a list of all target planets that are not currently being attacked. Make it iterable and sorted to specific heuristic.
    target_planets = iter(sorted([planet for planet in state.enemy_planets()
                                    if not any(fleet.destination_planet == planet.ID for fleet in state.my_fleets())], 
                                    key=lambda p: enemy_heuristic(state, p)))
    
    try:
        my_planet = next(my_planets)
        target_planet = next(target_planets)

        #(3) Iterate through all planets send a fleet as long as the planet has enough ships.
        while True:
            required_ships = find_future_value(state, my_planet, target_planet) + alloc_formula(state, target_planet)

            if my_planet.num_ships > required_ships:
                issue_order(state, my_planet.ID, target_planet.ID, required_ships)
                my_planet = next(my_planets)
                target_planet = next(target_planets)
            else:
                my_planet = next(my_planets)

    except:
        return

def spread_to_weakest_neutral_planet(state):

    #(1) Create an interable list of all my planets, sorted by their number of ships.
    my_planets = iter(sorted(state.my_planets(), key=lambda p: p.num_ships))
    
    #(2) Create an iterable list of all enemy planets.
    enemy_planets = iter(sorted(state.enemy_planets(), key=lambda p: p.num_ships))
    
    #(3) Find my planet with the highest growth rate. This will act as my center.
    source = max(state.my_planets(), key=lambda p: p.growth_rate, default=None)
    if not source:
        return

    #(4) Create a list of all neutral planets that are not currently being attacked. Make it iterable and sorted to number of ships * distance from my center
    target_planets = iter(sorted([planet for planet in state.neutral_planets()
                                    if not any(fleet.destination_planet == planet.ID for fleet in state.my_fleets())], 
                                    key=lambda p: p.num_ships * state.distance(source.ID, p.ID)))

    try:
        my_planet = next(my_planets)
        target_planet = next(target_planets)
        enemy_planet = min(enemy_planets, key=lambda p: state.distance(p.ID, target_planet.ID), default=None)

        #(5) Iterate through all planets send a fleet as long as the planet has enough ships.
        while True:
            
            # Ships needed determined by the how close the target planet is to my center compared to the closest enemy ship to the target.
            #                      E|xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxOOO|S
            required_ships = (target_planet.num_ships + 1) if enemy_planet and state.distance(enemy_planet.ID, target_planet.ID) > state.distance(my_planet.ID, target_planet.ID)+10 \
                        else find_future_value(state, my_planet, target_planet)

            if my_planet.num_ships > required_ships:
                issue_order(state, my_planet.ID, target_planet.ID, required_ships)
                my_planet = next(my_planets)
                target_planet = next(target_planets)
            else:
                my_planet = next(my_planets)

    except:
        return
    
def send_reinforcements(state):

    #(1) Create an interable list of all my planets, sorted by their number of ships.
    my_planets = iter(sorted(state.my_planets(), key=lambda p: p.num_ships))
    
    #(2) Create a list of all enemy fleets that are not currently being countered. Make it iterable and sorted to their number of ships
    target_fleets = iter(sorted([fleet for fleet in state.enemy_fleets()
                                    if not any(ally.destination_planet == fleet.destination_planet for ally in state.my_fleets())], 
                                    key=lambda p: p.num_ships))
    
    try:
        my_planet = next(my_planets)
        target_fleet = next(target_fleets)

        #(5) Iterate through all fleets and planets and send a fleet as long as the sender has enough ships.
        while True:
            try:
                target_planet = [planet for planet in state.my_planets() if planet.ID == target_fleet.destination_planet][0]
            except:
                target_planet = max(state.my_planets(), key=lambda p: p.growth_rate, default=None)
            
            required_ships = find_future_value(state, my_planet, target_planet)

            if my_planet.num_ships > required_ships:
                issue_order(state, my_planet.ID, target_planet.ID, required_ships)
                my_planet = next(my_planets)
                target_fleet = next(target_fleets)
            else:
                my_planet = next(my_planets)

    except StopIteration:
        return

###-------------------------------HELPER FUNCTIONS-----------------------------------

def find_future_value(state, source, destination):

    # Number of ships already owned + (Turns needed to reach * Growth rate)
    distance = state.distance(source.ID, destination.ID)
    return destination.num_ships + destination.growth_rate * distance

def enemy_heuristic(state, enemy):

    # Find enemy's and my centers.
    my_spawn = max(state.my_planets(), key=lambda p: p.growth_rate, default=None)
    enemy_spawn = max(state.enemy_planets(), key=lambda p: p.growth_rate, default=None)
    if not my_spawn or not enemy_spawn:
        return 0
    
    # Determine the level of roam the enemy target has (how close it is to their center).
    roamLvl = state.distance(enemy.ID, enemy_spawn.ID)

    # Determine the inverse danger level it has (how close it is to our center).
    dangerLvl = state.distance(enemy.ID, my_spawn.ID)

    # Determine its value (rate of ships produced).
    value = enemy.growth_rate

    # Heuristic used. Prioritizes the value and inverse roam level to a high degree. 
    # Having a negative value doesn't matter in this case, places it lower as a target.
    return value * math.sqrt(math.log(enemy.num_ships + 1) / dangerLvl) - roamLvl

def alloc_formula(state, enemy):

    # Determine the enemy center
    enemy_spawn = max(state.enemy_planets(), key=lambda p: p.growth_rate, default=None)
    if not enemy_spawn:
        return 0
    
    # Determine the level of roam the enemy target has (how close it is to their center).
    roamLvl = state.distance(enemy.ID, enemy_spawn.ID)

    # Determine its value (rate of ships produced).
    value = enemy.growth_rate

    # Return formula. If roamLvl is 0, then enemy being looked at is the spawner.
    try:
        return (enemy_spawn.num_ships / roamLvl)  + value + 1
    
    except:
        return 1

"""
    Defensive Version Score:  | Offensive Version Score:
                              |  
      Easy: Win (157)         |  Easy: Win (126)
      Spread: Win (143)       |  Spread: Win (166)
      Aggressive: Win (137)   |  Aggressive: Win (158)
      Defensive: Win (121)    |  Defensive: Win (124)
      Production: Win (75)    |  Production: Win (125)
     Total: 633               | Total: 699 (+66)

"""
