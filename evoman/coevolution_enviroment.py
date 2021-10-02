import numpy as np
from evoman.environment import Environment


class CoEvolutionEnvironment(Environment):
  
  def fitness_single(self):
    if self.contact_hurt == "player":
      return 0.9 * (100 - self.get_enemylife()) + 0.1 * self.get_playerlife() - np.log(self.get_time())
    
    return 0.9 * (100 - self.get_playerlife()) + 0.1 * self.get_enemylife() - np.log(self.get_time())