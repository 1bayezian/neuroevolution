from player_controller import PlayerController
from evoman.environment import Environment
import os
import random
import copy
from itertools import repeat
import math
import numpy as np

EXPERIMENT_NAME = 'deep-neural-net'
ACTIONS = ["left", "right", "jump", "shoot", "release"]
NUM_HIDDEN = 10

if not os.path.exists(EXPERIMENT_NAME):
  os.makedirs(EXPERIMENT_NAME)


class NeuroEvolution:

  def __init__(
    self,
    population: list,
    crossover_probability: float,
    mutation_probability: float,
    display = False
  ):
    self.initial_population = population
    self.crossover_probability = crossover_probability
    self.mutation_probability = mutation_probability
    self.display = display
    
  def rank_players(self, players: list) -> list:
    return sorted(players, key = lambda player: player.fitness, reverse = True)

  def survivor_selection(self, population: list, num_players: int) -> list:
    ranked = self.rank_players(population)

    return ranked[0: (num_players - 1)]

  def evaluate_player(self, player: PlayerController, simulations: int) -> float:
    total_fitness = 0.0

    for simulation in range(0, simulations):
      env = Environment(
        experiment_name = EXPERIMENT_NAME,
        enemies = [2],
        player_mode = "ai",
        player_controller = player,
        sound = "off",
        logs = "off",
        save_logs = "no"
      )

      if self.display:
        env.draw = True
        env.speed = "normal"

      fitness, player_health, enemy_health, time = env.play()
      total_fitness += fitness

    return total_fitness / simulations

  def evaluate(self, population: list, simulations: int):
    for player in population:
      player.fitness = self.evaluate_player(player, simulations)
 
    return population

  def mutate(self, offspring: list, gaussian_mean: float, gaussian_std: float) -> list:
    mutated = list()

    for individual in offspring:
      encoded = individual.encode()
      size = len(encoded)
  
      for i, m, s in zip(range(size), repeat(gaussian_mean, size), repeat(gaussian_std, size)):
        if random.random() < self.mutation_probability:
          encoded[i] += random.gauss(m, s)

      mutant_net = copy.deepcopy(individual.neural_net)
      mutant = PlayerController(mutant_net)
      mutant.decode(encoded)
      mutated.append(mutant)

    return mutated

  def crossover(self, individual1: PlayerController, individual2: PlayerController) -> [PlayerController, PlayerController]:
    encoded1 = copy.deepcopy(individual1.encode())
    encoded2 = copy.deepcopy(individual2.encode())
    size = min(len(encoded1), len(encoded2))

    for i in range(size):
      if random.random() < self.crossover_probability:
        encoded1[i], encoded2[i] = encoded2[i], encoded1[i]

    neural_net1 = copy.deepcopy(individual1.neural_net)
    neural_net1.decode(encoded1)
    offspring1 = PlayerController(neural_net1)

    neural_net2 = copy.deepcopy(individual2.neural_net)
    neural_net2.decode(encoded2)
    offspring2 = PlayerController(neural_net2)

    return offspring1, offspring2

  def mate(self, parents: list):
    quartile_qty = math.ceil(len(parents) / 4)
    quartile_last = len(parents) - 3 * quartile_qty
    percentile75_100 = [0.40 / quartile_qty] * quartile_qty
    percentile50_75 = [0.30 / quartile_qty] * quartile_qty
    percentile25_50 = [0.20 / quartile_qty] * quartile_qty
    percentile0_25 = [0.10 / quartile_last] * quartile_last
    selection_probabilities = [*percentile75_100, *percentile50_75, *percentile25_50, *percentile0_25]

    offspring = list()
    ranked_parents = self.rank_players(parents)
    past_selections = set()

    num_crossovers = math.ceil(len(parents) * 0.5)
    crossovers_completed = 0

    while crossovers_completed < num_crossovers:
      selected_parents = np.random.choice(ranked_parents, 2, p = selection_probabilities)

      hash1 = ''.join(map(str, selected_parents[0].encode()))
      hash2 = ''.join(map(str, selected_parents[1].encode()))

      if hash1 + hash2 in past_selections or hash2 + hash1 in past_selections or hash2 == hash1:
        continue

      past_selections.update([hash1 + hash2, hash2 + hash1])
      parent1 = selected_parents[0]
      parent2 = selected_parents[1]
      offspring1, offspring2 = self.crossover(parent1, parent2)
  
      offspring.append(offspring1)
      offspring.append(offspring2)
      crossovers_completed += 1

    return offspring

  def run(self, num_generations: int) -> [list, list]:
    population = copy.deepcopy(self.initial_population)

    current_generation = 0
    population = self.evaluate(population, 1)
    generation_size = len(population)

    mean_fitness = list()
    max_fitness = list()
    min_fitness = list()

    while current_generation < num_generations:
      # mate and mutate, then update the population
      offspring = self.mate(population)
      mutated = self.mutate(offspring, gaussian_mean = 0.0, gaussian_std = 0.1)
      population = population + mutated

      # evaluate, then select population for the next generation
      population = self.evaluate(population, 1)
      population = self.survivor_selection(population, math.ceil(generation_size))

      # update current generation size
      generation_size = len(population)

      # calculate mean fitness for current generation and append
      generation_fitness = list(player.fitness for player in population)
      mean_fitness.append(np.mean(generation_fitness))
      max_fitness.append(max(generation_fitness))
      min_fitness.append(min(generation_fitness))

      # log info in console, increment the generation
      print(f'mean(fitness): {np.mean(generation_fitness)}; max(fitness): {max(generation_fitness)}; min(fitness): {min(generation_fitness)};')
      current_generation += 1

    return population, mean_fitness, max_fitness, min_fitness
