#!/usr/bin/env python3

import json
import logging
import sys

from colosseum.games.food_catcher.game import World
from colosseum.manager import Manager
from colosseum.utils import get_internal_id


def main():
    agent_paths = sys.argv[1:]

    logging.basicConfig(filename=f"game_{get_internal_id()}.log", level=logging.INFO)

    world = World()

    manager = Manager(world, agent_paths)
    manager.start()
    manager.ping()
    manager.loop()
    manager.stop()

    scores = manager.scores

    print(json.dumps(scores))


if __name__ == "__main__":
    main()
