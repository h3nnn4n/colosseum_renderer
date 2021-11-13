#!/usr/bin/env python3

import json
import logging
import sys

import numpy as np
from utils import (
    deposit_food,
    get_internal_id,
    get_state,
    move,
    object_distance,
    send_commands,
    take_food,
)


AGENT_ID = None
AGENT_NAME = "first"
AGENT_VERSION = "0.0.1"


def main():
    global AGENT_ID

    my_actors = {}

    logging.basicConfig(
        filename=f"{AGENT_NAME}_{get_internal_id()}.log", level=logging.INFO
    )

    logging.debug("starting")
    while True:
        try:
            state = get_state()
            commands = {"actions": []}

            if state.get("stop"):
                logging.info(f"stopping, reason: {state.get('stop')}")
                break

            if state.get("set_agent_id"):
                AGENT_ID = state.get("set_agent_id")
                commands["agent_name"] = AGENT_NAME
                commands["agent_version"] = AGENT_VERSION
                logging.info(f"{AGENT_ID=}")

            if state.get("ping"):
                logging.info("got ping")
                commands["pong"] = "foobar"

            if state.get("actors"):
                logging.debug("got world state")

                # Update the current state of our actors
                for actor in state["actors"]:
                    if actor["owner_id"] != AGENT_ID:
                        continue

                    if actor["id"] not in my_actors:
                        my_actors[actor["id"]] = actor
                        my_actors[actor["id"]]["state"] = "take_food"

                    my_actors[actor["id"]].update(actor)

                actor = list(my_actors.values())[0]

                foods = state.get("foods")
                bases = [
                    base for base in state.get("bases") if base["owner_id"] == AGENT_ID
                ]
                food = foods[0]
                base = bases[0]

                distance_to_food = object_distance(actor, food)
                distance_to_base = object_distance(actor, base)
                food_position = np.array(food.get("position"))
                base_position = np.array(base.get("position"))

                if (
                    actor["state"] == "take_food"
                    and actor["food"] > 100
                    and distance_to_food > 1
                ):
                    actor["state"] = "deposit_food"

                logging.info(
                    f"actor {actor['id']} has state {actor['state']} food {actor['food']}"
                )
                if actor["state"] == "deposit_food":
                    if distance_to_base <= 0.1 and actor["food"] > 0:
                        deposit_food(commands, actor["id"], base["id"])
                    elif distance_to_base <= 0.1:
                        actor["state"] = "take_food"
                    else:
                        move(commands, actor["id"], base_position)

                if actor["state"] == "take_food":
                    if distance_to_food < 1:
                        take_food(commands, actor["id"], food["id"])
                    else:
                        move(commands, actor["id"], food_position)

            if AGENT_ID:
                commands["agent_id"] = AGENT_ID

            logging.debug(f"sending {commands}")
            send_commands(commands)
        except Exception as e:
            logging.exception(e)
            return
    logging.debug("finished")


if __name__ == "__main__":
    main()