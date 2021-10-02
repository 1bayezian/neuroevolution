################################
# EvoMan FrameWork - V1.0 2016 #
# Author: Karine Miras         #
# karine.smiras@gmail.com      #
################################

import gzip
import pickle
from pygame.locals import *
from evoman import tmx as tmx
from evoman.player import *
from evoman.controller import Controller
import evoman.enemy1
import evoman.enemy2
import evoman.enemy3
import evoman.enemy4
import evoman.enemy5
import evoman.enemy6
import evoman.enemy7
import evoman.enemy8

enemies = {
    1: evoman.enemy1,
    2: evoman.enemy2,
    3: evoman.enemy3,
    4: evoman.enemy4,
    5: evoman.enemy5,
    6: evoman.enemy6,
    7: evoman.enemy7,
    8: evoman.enemy8,
}


# main class
class Environment(object):

    # simulation parameters
    def __init__(
        self,
        experiment_name="test",
        multiple_mode= "no",  # yes or no
        enemies=[1],  # array with 1 to 8 items, values from 1 to 8
        load_player= "yes",  # yes or no
        load_enemy= "yes",  # yes or no
        level=2,  # integer
        player_mode= "ai",  # ai or human
        enemy_mode= "static",  # ai or static
        speed="fastest",  # normal or fastest
        inputs_coded= "no",  # yes or no
        random_ini= "no",  # yes or no
        sound="off",  # on or off
        contact_hur= "player",  # player or enemy
        logs="on",  # on or off
        save_logs= "yes",  # yes or no
        clock_precision= "low",
        time_expire=3000,  # integer
        overture_time=100,  # integer
        solutions=None,  # any
        full_screen=False,  # True or False
        player_controller=None,  # controller object
        enemy_controller=None,  # controller object
        use_joystick=False,
        draw = False
    ):

        # initializes parameters
        self.experiment_name = experiment_name
        self.multiple_mode = multiple_mode
        self.enemies = enemies
        self.enemy_n = enemies[0]  # initial current enemy
        self.load_player = load_player
        self.load_enemy = load_enemy
        self.level = level
        self.player_mode = player_mode
        self.enemy_mode = enemy_mode
        self.speed = speed
        self.inputs_coded = inputs_coded
        self.random_ini = random_ini
        self.sound = sound
        self.contact_hurt = contact_hur
        self.logs = logs
        self.full_screen = full_screen
        self.save_logs = save_logs
        self.clock_precision = clock_precision
        self.time_expire = time_expire
        self.overture_time = overture_time
        self.solutions = solutions
        self.joy = 0
        self.use_joystick = use_joystick
        self.draw = draw

        # initializes default random controllers

        if self.player_mode == "ai" and player_controller is None:
            self.player_controller = Controller()
        else:
            self.player_controller = player_controller

        if self.enemy_mode == "ai" and enemy_controller is None:
            self.enemy_controller = Controller()
        else:
            self.enemy_controller = enemy_controller

        # initializes log file
        if self.logs == "on" and self.save_logs == "yes":
            file_aux = open(self.experiment_name + "/evoman_logs.txt", "w")
            file_aux.close()

        # initializes pygame library
        pygame.init()
        self.print_logs("MESSAGE: Pygame initialized for simulation.")

        # initializes sound library for playing mode
        if self.sound == "on":
            pygame.mixer.init()
            self.print_logs("MESSAGE: sound has been turned on.")

        # initializes joystick library
        if self.use_joystick:
            pygame.joystick.init()
            self.joy = pygame.joystick.get_count()

        self.clock = pygame.time.Clock()  # initializes game clock resource

        if self.full_screen:
            flags = DOUBLEBUF | FULLSCREEN
        else:
            flags = DOUBLEBUF

        self.screen = pygame.display.set_mode((736, 512), flags)
        self.screen.set_alpha(None)  # disables uneeded alpha
        pygame.event.set_allowed([QUIT, KEYDOWN, KEYUP])  # enables only needed events

        self.load_sprites()

    def load_sprites(self):
        # loads enemy and map
        enemy = enemies[self.enemy_n]
        self.tilemap = tmx.load(enemy.tilemap, self.screen.get_size())  # map

        self.sprite_e = tmx.SpriteLayer()
        start_cell = self.tilemap.layers["triggers"].find("enemy")[0]
        self.enemy = enemy.Enemy((start_cell.px, start_cell.py), self.sprite_e)
        self.tilemap.layers.append(self.sprite_e)  # enemy

        # loads player
        self.sprite_p = tmx.SpriteLayer()
        start_cell = self.tilemap.layers["triggers"].find("player")[0]
        self.player = Player(
            (start_cell.px, start_cell.py), self.enemy_n, self.level, self.sprite_p
        )
        self.tilemap.layers.append(self.sprite_p)

        self.player.sensors = Sensors()
        self.enemy.sensors = Sensors()

    # updates environment with backup of current solutions in simulation
    def get_solutions(self):
        return self.solutions

        # method for updating solutions bkp in simulation

    def update_solutions(self, solutions):
        self.solutions = solutions

    # method for updating simulation parameters
    def update_parameter(self, name, value):

        if type(value) is str:
            exec("self." + name + "= '" + value + "'")
        else:
            exec("self." + name + "= " + str(value))

        self.print_logs("PARAMETER CHANGE: " + name + " = " + str(value))

    def print_logs(self, msg):
        if self.logs == "on":
            print("\n" + msg)  # prints log messages to screen

            if self.save_logs == "yes":  # prints log messages to file
                file_aux = open(self.experiment_name + "/evoman_logs.txt", "a")
                file_aux.write("\n\n" + msg)
                file_aux.close()

    def get_num_sensors(self):

        if hasattr(self, "enemy") and self.enemy_mode == "ai":
            return len(self.enemy.sensors.get(self))
        else:
            if hasattr(self, "player") and self.player_mode == "ai":
                return len(self.player.sensors.get(self))
            else:
                return 0

    # writes all variables related to game state into log
    def state_to_log(self):

        self.print_logs("########## Simulation state - INI ###########")
        if self.solutions == None:
            self.print_logs("# solutions # : EMPTY ")
        else:
            self.print_logs("# solutions # : LOADED ")

        self.print_logs("# sensors # : " + str(self.get_num_sensors()))
        self.print_logs(" ------  parameters ------  ")
        self.print_logs("# contact hurt (training agent) # : " + self.contact_hurt)

        self.print_logs("multiple mode: " + self.multiple_mode)

        en = ""
        for e in self.enemies:
            en += " " + str(e)
        self.print_logs("enemies list:" + en)

        self.print_logs("current enemy: " + str(self.enemy_n))
        self.print_logs("player mode: " + self.player_mode)
        self.print_logs("enemy mode: " + self.enemy_mode)
        self.print_logs("level: " + str(self.level))
        self.print_logs("clock precision: " + self.clock_precision)
        self.print_logs("inputs coded: " + self.inputs_coded)
        self.print_logs("random initialization: " + self.random_ini)
        self.print_logs("expiration time: " + str(self.time_expire))
        self.print_logs("speed: " + self.speed)
        self.print_logs("load player: " + self.load_player)
        self.print_logs("load enemy: " + self.load_enemy)
        self.print_logs("sound: " + self.sound)
        self.print_logs("overture time: " + str(self.overture_time))
        self.print_logs("logs: " + self.logs)
        self.print_logs("save logs: " + self.save_logs)
        self.print_logs("########## Simulation state - END ###########")

    # exports current environment state to files
    def save_state(self):

        # saves configuration file for simulation parameters
        file_aux = open(self.experiment_name + "/evoman_paramstate.txt", "w")
        en = ""
        for e in self.enemies:
            en += " " + str(e)
        file_aux.write("\nenemies" + en)
        file_aux.write("\ntime_expire " + str(self.time_expire))
        file_aux.write("\nlevel " + str(self.level))
        file_aux.write("\nenemy_n " + str(self.enemy_n))
        file_aux.write("\noverture_time " + str(self.overture_time))
        file_aux.write("\nplayer_mode " + self.player_mode)
        file_aux.write("\nenemy_mode " + self.enemy_mode)
        file_aux.write("\ncontact_hur " + self.contact_hurt)
        file_aux.write("\nclock_precision " + self.clock_precision)
        file_aux.write("\ninputs_coded " + self.inputs_coded)
        file_aux.write("\nrandom_ini " + self.random_ini)
        file_aux.write("\nmultiple_mode " + self.multiple_mode)
        file_aux.write("\nspeed " + self.speed)
        file_aux.write("\nload_player " + self.load_player)
        file_aux.write("\nload_enemy " + self.load_enemy)
        file_aux.write("\nsound " + self.sound)
        file_aux.write("\nlogs " + self.logs)
        file_aux.write("\nsave_logs " + self.save_logs)
        file_aux.close()

        # saves state of solutions in the simulation
        file = gzip.open(
            self.experiment_name + "/evoman_solstate", "w", compresslevel=5
        )
        pickle.dump(self.solutions, file, protocol=2)
        file.close()

        self.print_logs("MESSAGE: state has been saved to files.")

    # loads a state for environment from files
    def load_state(self):

        try:

            # loads parameters
            state = open(self.experiment_name + "/evoman_paramstate.txt", "r")
            state = state.readlines()
            for idp, p in enumerate(state):
                pv = p.split(" ")

                if idp > 0:  # ignore first line
                    if idp == 1:  # enemy list
                        en = []
                        for i in range(1, len(pv)):
                            en.append(int(pv[i].rstrip("\n")))
                        self.update_parameter(pv[0], en)
                    elif idp < 6:  # numeric inputs
                        self.update_parameter(pv[0], int(pv[1].rstrip("\n")))
                    else:  # string inputs
                        self.update_parameter(pv[0], pv[1].rstrip("\n"))

            # loads solutions
            file = gzip.open(self.experiment_name + "/evoman_solstate")
            self.solutions = pickle.load(file, encoding="latin1")
            self.print_logs("MESSAGE: state has been loaded.")

        except IOError:
            self.print_logs("ERROR: could not load state.")

    def checks_params(self):

        # validates parameters values

        if self.multiple_mode == "yes" and len(self.enemies) < 2:
            self.print_logs(
                "ERROR: 'enemies' must contain more than one enemy for multiple mode."
            )
            sys.exit(0)

        if self.enemy_mode not in ("static", "ai"):
            self.print_logs("ERROR: 'enemy mode' must be 'static' or 'ai'.")
            sys.exit(0)

        if self.player_mode not in ("human", "ai"):
            self.print_logs("ERROR: 'player mode' must be 'human' or 'ai'.")
            sys.exit(0)

        if self.load_player not in ("yes", "no"):
            self.print_logs("ERROR: 'load player' value must be 'yes' or 'no'.")
            sys.exit(0)

        if self.load_enemy not in ("yes", "no"):
            self.print_logs("ERROR: 'load enemy' value must be 'yes' or 'no'.")
            sys.exit(0)

        if self.inputs_coded not in ("yes", "no"):
            self.print_logs("ERROR: 'inputs coded' value must be 'yes' or 'no'.")
            sys.exit(0)

        if self.multiple_mode not in ("yes", "no"):
            self.print_logs("ERROR: 'multiple_mode' value must be 'yes' or 'no'.")
            sys.exit(0)

        if self.random_ini not in ("yes", "no"):
            self.print_logs("ERROR: 'random ini' value must be 'yes' or 'no'.")
            sys.exit(0)

        if self.save_logs not in ("yes", "no"):
            self.print_logs("ERROR: 'save logs' value must be 'yes' or 'no'.")
            sys.exit(0)

        if self.speed not in ("normal", "fastest"):
            self.print_logs("ERROR: 'speed' value must be 'normal' or 'fastest'.")
            sys.exit(0)

        if self.logs not in ("on", "off"):
            self.print_logs("ERROR: 'logs' value must be 'on' or 'off'.")
            sys.exit(0)

        if self.clock_precision not in ("low", "medium"):
            self.print_logs("ERROR: 'clock_precision' value must be 'low' or 'medium'.")
            sys.exit(0)

        if self.sound not in ("on", "off"):
            self.print_logs("ERROR: 'sound' value must be 'on' or 'off'.")
            sys.exit(0)

        if self.contact_hurt not in ("player", "enemy"):
            self.print_logs("ERROR: 'contact_hur' value must be 'player' or 'enemy'.")
            sys.exit(0)

        if type(self.time_expire) is not int:
            self.print_logs("ERROR: 'time_expire' must be integer.")
            sys.exit(0)

        if type(self.level) is not int:
            self.print_logs("ERROR: 'level' must be integer.")
            sys.exit(0)

        if type(self.overture_time) is not int:
            self.print_logs("ERROR: 'overture_time' must be integer.")
            sys.exit(0)

        # checks parameters consistency

        if self.multiple_mode == "no" and len(self.enemies) > 1:
            self.print_logs(
                "MESSAGE: there is more than one enemy in 'enemies' list although the mode is not multiple."
            )

        if self.level < 1 or self.level > 3:
            self.print_logs("MESSAGE: 'level' chosen is out of recommended (tested).")

            # default fitness function for single solutions

    def fitness_single(self):
        return (
            0.9 * (100 - self.get_enemylife())
            + 0.1 * self.get_playerlife()
            - numpy.log(self.get_time())
        )

    # default fitness function for consolidating solutions among multiple games
    def cons_multi(self, values):
        return values.mean() - values.std()

    # measures the energy of the player
    def get_playerlife(self):
        return self.player.life

    # measures the energy of the enemy
    def get_enemylife(self):
        return self.enemy.life

    # gets run time
    def get_time(self):
        return self.time

    # runs game for a single enemy
    def run_single(self, enemyn, pcont, econt):

        # sets controllers
        self.pcont = pcont
        self.econt = econt

        self.checks_params()

        self.enemy_n = enemyn  # sets the current enemy
        ends = 0
        self.time = 0
        self.freeze_p = False
        self.freeze_e = False
        self.start = False

        enemy = enemies[self.enemy_n]

        self.load_sprites()

        # game main loop

        while 1:

            # adjusts frames rate for defining game speed

            if self.clock_precision == "medium":  # medium clock precision
                if self.speed == "normal":
                    self.clock.tick_busy_loop(30)
                elif self.speed == "fastest":
                    self.clock.tick_busy_loop()

            else:  # low clock precision

                if self.speed == "normal":
                    self.clock.tick(30)
                elif self.speed == "fastest":
                    self.clock.tick()

            # game timer
            self.time += 1
            if self.player_mode == "human" and self.sound == "on":
                # sound effects
                if self.sound == "on" and self.time == 1:
                    sound = pygame.mixer.Sound("evoman/sounds/open.wav")
                    c = pygame.mixer.Channel(1)
                    c.set_volume(1)
                    c.play(sound, loops=10)

                if (
                    self.time > self.overture_time
                ):  # delays game start a little bit for human mode
                    self.start = True
            else:
                self.start = True

            # checks screen closing button
            self.event = pygame.event.get()
            for event in self.event:
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return

            # updates objects and draws its items on screen
            self.tilemap.update(33 / 1000.0, self)

            if self.draw:
                self.screen.fill((250, 250, 250))
                self.tilemap.update(33 / 1000.0, self)
                self.tilemap.draw(self.screen)

                # player life bar
                vbar = int(100 * (1 - (self.player.life / float(self.player.max_life))))
                pygame.draw.line(self.screen, (0, 0, 0), [40, 40], [140, 40], 2)
                pygame.draw.line(self.screen, (0, 0, 0), [40, 45], [140, 45], 5)
                pygame.draw.line(self.screen, (150, 24, 25), [40, 45], [140 - vbar, 45], 5)
                pygame.draw.line(self.screen, (0, 0, 0), [40, 49], [140, 49], 2)

                # enemy life bar
                vbar = int(100 * (1 - (self.enemy.life / float(self.enemy.max_life))))
                pygame.draw.line(self.screen, (0, 0, 0), [590, 40], [695, 40], 2)
                pygame.draw.line(self.screen, (0, 0, 0), [590, 45], [695, 45], 5)
                pygame.draw.line(
                    self.screen, (194, 118, 55), [590, 45], [695 - vbar, 45], 5
                )
                pygame.draw.line(self.screen, (0, 0, 0), [590, 49], [695, 49], 2)

            # gets fitness for training agents
            fitness = self.fitness_single()

            # returns results of the run
            def return_run():
                self.print_logs(
                    "RUN: run status: enemy: "
                    + str(self.enemy_n)
                    + "; fitness: "
                    + str(fitness)
                    + "; player life: "
                    + str(self.player.life)
                    + "; enemy life: "
                    + str(self.enemy.life)
                    + "; time: "
                    + str(self.time)
                )

                return fitness, self.player.life, self.enemy.life, self.time

            if self.start == False and self.player_mode == "human":
                myfont = pygame.font.SysFont("Comic sams", 100)
                pygame.font.Font.set_bold
                self.screen.blit(myfont.render("Player", 1, (150, 24, 25)), (50, 180))
                self.screen.blit(myfont.render("  VS  ", 1, (50, 24, 25)), (250, 180))
                self.screen.blit(
                    myfont.render("Enemy " + str(self.enemy_n), 1, (194, 118, 55)),
                    (400, 180),
                )

            # checks player life status
            if self.player.life == 0:
                ends -= 1

                # tells user that player has lost
                if self.player_mode == "human":
                    myfont = pygame.font.SysFont("Comic sams", 100)
                    pygame.font.Font.set_bold
                    self.screen.blit(
                        myfont.render(" Enemy wins", 1, (194, 118, 55)), (150, 180)
                    )

                self.player.kill()  # removes player sprite
                self.enemy.kill()  # removes enemy sprite

                if self.player_mode == "human":
                    # delays run finalization for human mode
                    if ends == -self.overture_time:
                        return return_run()
                else:
                    return return_run()

            # checks enemy life status
            if self.enemy.life == 0:
                ends -= 1

                self.screen.fill((250, 250, 250))
                self.tilemap.draw(self.screen)

                # tells user that player has won
                if self.player_mode == "human":
                    myfont = pygame.font.SysFont("Comic sams", 100)
                    pygame.font.Font.set_bold
                    self.screen.blit(
                        myfont.render(" Player wins ", 1, (150, 24, 25)), (170, 180)
                    )

                self.enemy.kill()  # removes enemy sprite
                self.player.kill()  # removes player sprite

                if self.player_mode == "human":
                    if ends == -self.overture_time:
                        return return_run()
                else:
                    return return_run()

            if self.load_player == "no":  # removes player sprite from game
                self.player.kill()

            if self.load_enemy == "no":  # removes enemy sprite from game
                self.enemy.kill()

                # updates screen
            pygame.display.flip()

            # game runtime limit
            if self.player_mode == "ai":
                if self.time >= enemy.timeexpire:
                    return return_run()

            else:
                if self.time >= self.time_expire:
                    return return_run()

    # repeats run for every enemy in list
    def multiple(self, pcont, econt):

        vfitness, vplayerlife, venemylife, vtime = [], [], [], []
        for e in self.enemies:

            fitness, playerlife, enemylife, time = self.run_single(e, pcont, econt)
            vfitness.append(fitness)
            vplayerlife.append(playerlife)
            venemylife.append(enemylife)
            vtime.append(time)

        vfitness = self.cons_multi(numpy.array(vfitness))
        vplayerlife = self.cons_multi(numpy.array(vplayerlife))
        venemylife = self.cons_multi(numpy.array(venemylife))
        vtime = self.cons_multi(numpy.array(vtime))

        return vfitness, vplayerlife, venemylife, vtime

    # checks objective mode
    def play(self, pcont = "None", econt = "None"):
        if self.multiple_mode == "yes":
            return self.multiple(pcont, econt)
        else:
            return self.run_single(self.enemies[0], pcont, econt)
