"""Run game"""

import pygame

from blocks.block import generate_board
from state import GameData, GameState, MainState
from player import create_players
from renderer import Renderer
from settings import BOARD_SIZE


class Game:
    """A game of Blocky.

    Private Instance Attributes:
    - _renderer: The object that is capable of drawing our Blocky board
                 on the screen.
    - _data: The data of the game that can be shared with other
             GameState objects.
    - _state: The current GameState.
    """
    _renderer: Renderer
    _data: GameData
    _state: GameState

    def __init__(self, max_depth: int,
                 num_human: int,
                 num_random: int,
                 smart_players: list[int]) -> None:
        """Initialize this game, as described in the Assignment 2 handout.

        Preconditions:
        - 2 <= max_depth <= 5
        """
        board = generate_board(max_depth, BOARD_SIZE)
        players = create_players(num_human, num_random, smart_players)

        self._renderer = Renderer(BOARD_SIZE)
        self._data = GameData(board, players)
        self._state = MainState(self._data)

    def run_game(self, num_turns: int) -> None:
        """Start the main game loop and stop after num_turns.

        Preconditions:
        - num_turns >= 1
        """
        self._data.max_turns = num_turns
        clock = pygame.time.Clock()

        while True:
            clock.tick(30)

            # Process events
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    return
                else:
                    self._state.process_event(e)

            # Update the state of the game
            self._state = self._state.update()

            # Render the new state of the game
            self._renderer.clear()
            self._state.render(self._renderer)

            # Update the screen
            pygame.display.flip()


def create_auto_game() -> Game:
    """Run a game with two computer players of different "difficulty"."""
    return Game(4, 0, 0, [10, 10])


def create_two_player_game() -> Game:
    """Run a game with two human players."""
    return Game(4, 1, 0, [100])


def create_solitaire_game() -> Game:
    """Run a game with one human player."""
    return Game(3, 1, 0, [])


def create_sample_game() -> Game:
    """Run a sample game with one human player, one random player,
    and one smart player.
    """
    return Game(3, 1, 1, [6])


if __name__ == '__main__':
    pygame.init()

    # If you want to run the same game sequence each time, to assist with
    # debugging, uncomment-out the call to random.seed.
    # import random
    # random.seed(1001)
    # game = create_sample_game()
    # game = create_auto_game()
    game = create_two_player_game()
    # game = create_solitaire_game()

    # Run the game for 5 turns
    game.run_game(10)

    pygame.quit()
