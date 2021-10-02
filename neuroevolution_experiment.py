from player_controller import PlayerController
from neuroevolution import NeuroEvolution
from evoman.environment import Environment
from deep_net import DeepNet
import os

EXPERIMENT_NAME = 'neuroevo-experiment'
ACTIONS = ["left", "right", "jump", "shoot", "release"]
NUM_HIDDEN_NODES = 10

if not os.path.exists(EXPERIMENT_NAME):
  os.makedirs(EXPERIMENT_NAME)

os.environ["SDL_VIDEODRIVER"] = "dummy"

population_size = 100
max_generations = 10
# update to include more enemies
enemies = [2]

env = Environment(
  experiment_name = EXPERIMENT_NAME,
  enemies = [2],
  player_mode = "ai",
  enemy_mode = "static",
  speed = "fastest"
)

num_sensors = env.get_num_sensors()

# initialize the initial initial_population
population = list()
for i in range(0, population_size):
  mlp = DeepNet(num_sensors, NUM_HIDDEN_NODES, len(ACTIONS))
  player = PlayerController(mlp)
  population.append(player)

evo = NeuroEvolution(population, 0.5, 0.5)
population, mean_fitness, max_fitness, min_fitness = evo.run(num_generations = max_generations)
fittest = sorted(population, key = lambda player: player.fitness, reverse = True)

pass
# write a test for this
# p1 = PlayerController()
# n1 = DeepNet(num_sensors, NUM_HIDDEN, len(ACTIONS))
# p1.set_neural_net(n1)
# encoded = p1.encode()
#
# p2 = PlayerController()
# n2 = DeepNet(num_sensors, NUM_HIDDEN, len(ACTIONS))
# n2.decode(encoded)
# p2.set_neural_net(n2)
# decoded = p2.neural_net
#
# p1_weights = encoded
# p2_weights = p2.encode()

# n1 = DeepNet(num_sensors, NUM_HIDDEN_NODES, len(ACTIONS))
# p1 = PlayerController(n1)
# initial_population.append(p1)
#
# evo = NeuroEvolution(
#   crossover_probability = 0.01,
#   mutation_probability = 0.50,
#   display = True
# )
#
# fitness_original = evo.evaluate(p1, 1)
# mutated = evo.mutate(p1, gaussian_mean = 0.0, gaussian_std = 0.5)
# fitness_mutated = evo.evaluate(mutated, 1)
