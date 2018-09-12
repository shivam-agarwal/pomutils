import json
import os
import numpy as np
import pommerman
from pommerman.characters import Bomber as Bomber
from pommerman.characters import Bomb as Bomb
from pommerman.characters import Flame as Flame
import argparse
import time


def import_gamestate(filename) :
    with open(filename, 'r') as f:
        pm_gamestate = json.loads(f.read())
        states = pm_gamestate['state']
        # Values in state dict are actually json encoded
        # decode them
        new_states = []
        for s in states:
            new_state = {}
            for key, value in s.items():
                new_state[key] =  json.loads(value)
            new_states.append(new_state)

        # Sort states by step count
        new_states.sort(key=lambda state: state['step_count'])

        # Remove intended_actions from states and add it as actions
        # to previous state

        for i in range(len(new_states) - 1):
            actions =  new_states[i+1].pop('intended_actions')
            new_states[i]['action'] = actions

        # replace old state array
        pm_gamestate['state'] = new_states
        return pm_gamestate

def stateToScene(state) :
    agents = []
    for agent_state in state['agents']:
        agent = Bomber(agent_id = agent_state['agent_id'])
        position =  tuple(agent_state['position'])
        agent.set_start_position(position)
        agent.reset( int(agent_state['ammo']),
                     bool(agent_state['is_alive']),
                     int(agent_state['blast_strength']),
                    bool(agent_state['can_kick']))
        agents.append(agent)

    bombs = []
    for bomb_state in state['bombs']:
        direction = bomb_state['moving_direction']
        if direction is not None:
           direction = pommerman.constants.Action(direction)
        bomb = Bomb(agents[bomb_state['bomber_id']],
             tuple(bomb_state['position']),
             int(bomb_state['life']),
             int(bomb_state['blast_strength']),
             direction)
        bombs.append(bomb)

    items = {}
    for item_state in state['items']:
        items[tuple(item_state[0])] = item_state[1]

    flames = []
    for flame_state in state['flames']:
        flame = Flame(tuple(flame_state['position']),
                                 flame_state['life'])
        flames.append(flame)


    board =   np.asarray(state['board'], np.uint8)

    return board, agents, bombs, items, flames


def main(args):

    viewer = None

    if (None == args.gamefile) :
        print("Please add --gamefile <file>")
        return

    verify = not args.noverify
    render = args.render

    gs = import_gamestate(args.gamefile)

    board, agents, bombs, items, flames = stateToScene(gs['state'][0])

    for i in range(len(gs['state'])-1):

        action= gs['state'][i]['action'];

        if (args.verbose) :
            print ("Step: ", i, "Action: ", action);
            print (board)

        board, agents, bombs, items, flames = pommerman.forward_model.ForwardModel.step(action,  board, agents, bombs, items, flames)

        if render:
            if viewer is None:
                viewer = pommerman.graphics.PommeViewer()
            viewer.set_board(board)
            viewer.set_agents(agents)
            if hasattr(viewer, 'set_bombs'):
                 viewer.set_bombs(bombs)
            viewer.set_step(i)
            viewer.render()
            time.sleep(0.1)

        if verify:
            tboard, tagents, tbombs, titems, tflames = stateToScene(gs['state'][i+1])
            if ( not np.array_equal(board,tboard)):
                print ("failed at step:", i)
                return

    if (args.verbose) :
         print ("Step: ", len(gs['state']) - 1);
         print (board)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Replay Flags.')

    parser.add_argument(
        "--noverify",
        default=False,
        action='store_true',
        help="Whether to skip verifying. Defaults to False.")


    parser.add_argument(
        '--gamefile',
        default=None,
        help='Game file to replay')

    parser.add_argument(
        "--verbose",
        default=False,
        action='store_true',
        help="Print out map at each step")

    parser.add_argument(
        "--render",
        default=False,
        action='store_true',
        help="Render Game")



    args = parser.parse_args()
    main(args)
