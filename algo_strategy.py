from asyncio import constants
from distutils.command.build import build
import gamelib
import random
import math
import warnings
from sys import maxsize
import json


"""
Most of the algo code you write will be in this file unless you create new
modules yourself. Start by modifying the 'on_turn' function.

Advanced strategy tips: 

  - You can analyze action frames by modifying on_action_frame function

  - The GameState.map object can be manually manipulated to create hypothetical 
  board states. Though, we recommended making a copy of the map to preserve 
  the actual current map state.
"""

class AlgoStrategy(gamelib.AlgoCore):
    def __init__(self):
        super().__init__()
        seed = random.randrange(maxsize)
        random.seed(seed)
        gamelib.debug_write('Random seed: {}'.format(seed))

    def on_game_start(self, config):
        """ 
        Read in config and perform any initial setup here 
        """
        gamelib.debug_write('Configuring your custom algo strategy...')
        self.config = config
        global WALL, SUPPORT, TURRET, SCOUT, DEMOLISHER, INTERCEPTOR, MP, SP
        WALL = config["unitInformation"][0]["shorthand"]
        SUPPORT = config["unitInformation"][1]["shorthand"]
        TURRET = config["unitInformation"][2]["shorthand"]
        SCOUT = config["unitInformation"][3]["shorthand"]
        DEMOLISHER = config["unitInformation"][4]["shorthand"]
        INTERCEPTOR = config["unitInformation"][5]["shorthand"]
        MP = 1
        SP = 0
        # This is a good place to do initial setup
        self.scored_on_locations = []
        self.current_enemy_health = 30
        self.wreck_havoc = False
        self.deploy_troop = False

    def on_turn(self, turn_state):
        """
        This function is called every turn with the game state wrapper as
        an argument. The wrapper stores the state of the arena and has methods
        for querying its state, allocating your current resources as planned
        unit deployments, and transmitting your intended deployments to the
        game engine.
        """
        game_state = gamelib.GameState(self.config, turn_state)
        # game_state.attempt_spawn(DEMOLISHER, [24, 10], 3)
        gamelib.debug_write('Performing turn {} of your custom algo strategy'.format(game_state.turn_number))
        game_state.suppress_warnings(True)  #Comment or remove this line to enable warnings.

        if self.deploy_troop:
          gamelib.debug_write(f'Before deploying troop\nEnemy health: {self.current_enemy_health}')
          gamelib.debug_write(f'After deploying troop\nEnemy health: {game_state.enemy_health}')
          if self.current_enemy_health <= game_state.enemy_health + 2:
            # scout aren't effective anymore, have to spawn demolisher
            self.wreck_havoc = True
          else:
            # scout are still effective keep spawning scouts
            self.wreck_havoc = False
          self.current_enemy_health = game_state.enemy_health
        
        self.deploy_troop = False
        self.starter_strategy(game_state)

        game_state.submit_turn()



    """
    NOTE: All the methods after this point are part of the sample starter-algo
    strategy and can safely be replaced for your custom algo.
    """
    def starter_strategy(self, game_state):
        # defense
        self.build_defense(game_state)
        # attack
        self.spawn_scout(game_state)

    def build_defense(self, game_state):
        # build
        self.build_defense_maze(game_state)
        self.build_defense_corner(game_state)
        self.build_defense_mid(game_state)
        self.build_defense_addition(game_state)

        # update
        self.upgrade_defense_maze(game_state)
        self.upgrade_defense_corner(game_state)
        self.upgrade_defense_mid(game_state)

    def build_defense_maze(self, game_state):
        WALL_LOCATIONS = [[0, 13], [1, 13], [2, 13], [3, 13], [5, 12], [6, 9], [7, 8], [8, 8]]
        TURRET_LOCATIONS = [[3, 12], [3, 11], [5, 11], [5, 10]]

        game_state.attempt_spawn(WALL, WALL_LOCATIONS, 1)
        game_state.attempt_spawn(TURRET, TURRET_LOCATIONS, 1)
        if (game_state.get_resource(SP, 0) > 30):
          game_state.attempt_upgrade(WALL_LOCATIONS)

    def build_defense_corner(self, game_state):
        WALL_LOCATIONS_RIGHT = [[24, 13], [25, 13], [26, 13], [27, 13], [24, 12], [23, 11], [22, 10], [22, 9], [22, 8]]
        TURRET_LOCATIONS_RIGHT = [[25, 12], [24, 11]]

        game_state.attempt_spawn(WALL, WALL_LOCATIONS_RIGHT, 1)
        game_state.attempt_spawn(TURRET, TURRET_LOCATIONS_RIGHT, 1)

        if (game_state.get_resource(SP, 0) > 30):
          game_state.attempt_upgrade(WALL_LOCATIONS_RIGHT)
          game_state.attempt_upgrade(TURRET_LOCATIONS_RIGHT)

        
    def build_defense_mid(self, game_state):
        WALL_LOCATIONS_MID =  [[10, 8], [11, 8], [12, 8], [13, 8], [14, 8], [15, 8], [16, 8], [17, 8], [18, 8], [19, 8], [20, 8], [21, 8], [9, 7]]
        game_state.attempt_spawn(WALL, WALL_LOCATIONS_MID)

    def build_defense_addition(self, game_state):
        add_turret = [[3, 10], [6, 10], [23, 10]]
        add_support = [[1, 12], [2, 12], [2, 11]]

        game_state.attempt_spawn(SUPPORT, add_support)
        game_state.attempt_spawn(TURRET, add_turret)

    def upgrade_defense_maze(self, game_state):
        WALL_LOCATIONS = [[0, 13], [1, 13], [2, 13], [3, 13], [5, 12], [6, 9], [7, 8], [8, 8]]
        TURRET_LOCATIONS = [[3, 12], [3, 11], [5, 11], [5, 10], [3, 10], [6, 10]]
        SUPPORT_LOCATIONS = [[1, 12], [2, 12], [2, 11]]
        game_state.attempt_upgrade(WALL_LOCATIONS)
        game_state.attempt_upgrade(TURRET_LOCATIONS)
        game_state.attempt_upgrade(SUPPORT_LOCATIONS)
      
    def upgrade_defense_corner(self, game_state):
        WALL_LOCATIONS_RIGHT = [[24, 13], [25, 13], [26, 13], [27, 13], [24, 12], [23, 11], [22, 10], [22, 9], [22, 8]]
        TURRET_LOCATIONS_RIGHT = [[25, 12], [24, 11], [23, 10]]
        game_state.attempt_upgrade(WALL_LOCATIONS_RIGHT)
        game_state.attempt_upgrade(TURRET_LOCATIONS_RIGHT)

    def upgrade_defense_mid(self, game_state):
        pass
      
    def spawn_scout(self, game_state):
        if (game_state.get_resource(MP, 0) < 15):
          return
        self.deploy_troop = True
        if not self.wreck_havoc:
          num_scout = game_state.attempt_spawn(SCOUT, [4, 9], 20)
          gamelib.debug_write(f'spawn {num_scout} scouts')
        else:
          num_demolisher = game_state.attempt_spawn(DEMOLISHER, [4, 9], 20)
          gamelib.debug_write(f'spawn {num_demolisher} demolishers')
          
    def on_action_frame(self, turn_string):
        """
        This is the action frame of the game. This function could be called 
        hundreds of times per turn and could slow the algo down so avoid putting slow code here.
        Processing the action frames is complicated so we only suggest it if you have time and experience.
        Full doc on format of a game frame at in json-docs.html in the root of the Starterkit.
        """
        # Let's record at what position we get scored on
        state = json.loads(turn_string)
        events = state["events"]
        breaches = events["breach"]
        for breach in breaches:
            location = breach[0]
            unit_owner_self = True if breach[4] == 1 else False
            # When parsing the frame data directly, 
            # 1 is integer for yourself, 2 is opponent (StarterKit code uses 0, 1 as player_index instead)
            if not unit_owner_self:
                gamelib.debug_write("Got scored on at: {}".format(location))
                self.scored_on_locations.append(location)
                gamelib.debug_write("All locations: {}".format(self.scored_on_locations))


if __name__ == "__main__":
    algo = AlgoStrategy()
    algo.start()
