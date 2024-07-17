import sys
sys.path.insert(0, '../')
from planet_wars import issue_order
import logging
import math


def attack_weakest_enemy_planet(state):
    my_planets = iter(sorted(state.my_planets(), key=lambda p: p.num_ships))

    target_planets = iter(sorted([planet for planet in state.enemy_planets()
                                    if not any(fleet.destination_planet == planet.ID for fleet in state.my_fleets())], 
                                    key=lambda p: enemy_heuristic(state, p)))

    try:
        my_planet = next(my_planets)
        target_planet = next(target_planets)
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
    my_planets = iter(sorted(state.my_planets(), key=lambda p: p.num_ships))
    enemy_planets = iter(sorted(state.enemy_planets(), key=lambda p: p.num_ships))
    source = max(state.my_planets(), key=lambda p: p.growth_rate, default=None)
    if not source:
        return

    target_planets = iter(sorted([planet for planet in state.neutral_planets()
                                    if not any(fleet.destination_planet == planet.ID for fleet in state.my_fleets())], 
                                    key=lambda p: p.num_ships * state.distance(source.ID, p.ID)))

    try:
        my_planet = next(my_planets)
        target_planet = next(target_planets)
        enemy_planet = min(enemy_planets, key=lambda p: state.distance(p.ID, target_planet.ID), default=None)
        while True:
            #required_ships = find_future_value(state, my_planet, target_planet) + 1
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
    my_planets = iter(sorted(state.my_planets(), key=lambda p: p.num_ships))

    target_fleets = iter(sorted([fleet for fleet in state.enemy_fleets()
                                    if not any(ally.destination_planet == fleet.destination_planet for ally in state.my_fleets())], 
                                    key=lambda p: p.num_ships))

    try:
        my_planet = next(my_planets)
        target_fleet = next(target_fleets)
        while True:
            required_ships = target_fleet + find_future_value(state, my_planet, target_fleet.destination_planet)

            if my_planet.num_ships > required_ships:
                issue_order(state, my_planet.ID, target_planet.ID, required_ships)
                my_planet = next(my_planets)
                target_planet = next(target_fleet)
            else:
                my_planet = next(my_planets)

    except:
        return

def find_future_value(state, source, destination):
    distance = state.distance(source.ID, destination.ID)
    return destination.num_ships + destination.growth_rate * distance

def enemy_heuristic(state, enemy):
    my_spawn = max(state.my_planets(), key=lambda p: p.growth_rate, default=None)
    enemy_spawn = max(state.enemy_planets(), key=lambda p: p.growth_rate, default=None)
    if not my_spawn or not enemy_spawn:
        return 0
    
    roamLvl = state.distance(enemy.ID, enemy_spawn.ID)
    dangerLvl = state.distance(enemy.ID, my_spawn.ID)
    value = enemy.growth_rate

    return value * math.sqrt(math.log(enemy.num_ships + 1) / dangerLvl) - roamLvl

def alloc_formula(state, enemy):
    enemy_spawn = max(state.enemy_planets(), key=lambda p: p.growth_rate, default=None)
    if not enemy_spawn:
        return 0
    
    roamLvl = state.distance(enemy.ID, enemy_spawn.ID)
    value = enemy.growth_rate

    try:
        return (enemy_spawn.num_ships / roamLvl)  + value + 1
    
    except:
        return 1


