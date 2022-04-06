"""
Run DQN on grid world.
"""

import gym
from torch import nn as nn

from rlkit.exploration_strategies.base import \
    PolicyWrappedWithExplorationStrategy
from rlkit.exploration_strategies.epsilon_greedy import EpsilonGreedy, EpsilonGreedyWithDecay
from rlkit.policies.argmax import ArgmaxDiscretePolicy
import rlkit.torch.pytorch_util as ptu
from rlkit.torch.reprel.reprel_dqn import RePReLDQNTrainer as HDQNTrainer
import taxi_domain
import argparse
import os, torch
from rlkit.data_management.simple_replay_buffer import SimpleReplayBuffer, SimpleReplayBufferDiscreteAction
from rlkit.launchers.launcher_util import setup_logger
from rlkit.samplers.data_collector.hrl_path_collector import HRLPathCollector, METACONTROLLER
from rlkit.core.reprel_algorithm import RePReLAlgorithm as HRLAlgorithm
import numpy as np
from gym.spaces.discrete import Discrete
import officeworld
from examples.office.office_planner import *


def define_intrinsic_critic(env, step_cost, reward):

    def is_terminal(state, action, next_state, operator):
        facts = state[2:]
        next_facts = next_state[2:]
        terminal = False
        if operator == 'get_coffee':
            terminal = (not facts[has_coffee] and next_facts[has_coffee])
        elif operator == 'get_mail':
            terminal = (not facts[has_mail] and next_facts[has_mail])
        elif operator == 'go_to_office':
            terminal = (not facts[visited_office] and next_facts[visited_office])
        return terminal

    def intrinsic_reward(state, action, next_state, operator, r):
        return reward+r if is_terminal(state, action, next_state, operator) else step_cost+r

    return is_terminal, intrinsic_reward



def experiment(variant):
    expl_env = gym.make(variant['env'])
    eval_env = gym.make(variant['env'])
    data = torch.load(variant['model_file']) #, map_location='cpu' )
    eval_policy = data['evaluation/policy']
    operator_qfs = data['trainer/operator_qfs']
    operator_target_qfs =data['trainer/operator_target_qfs']
    operators = list(operator_qfs.keys())
    operators.remove(METACONTROLLER)
    obs_dim = expl_env.observation_space.shape[0]
    action_dim = eval_env.action_space.n
    is_terminal, internal_critic = define_intrinsic_critic(expl_env, step_cost=variant['intrinsic_cost'],
                                                           reward=variant['intrinsic_reward'])
    replay_buffers = {}
    for operator in operators:
        replay_buffers[operator] = SimpleReplayBufferDiscreteAction(
            max_replay_buffer_size=variant['replay_buffer_size'],
            observation_dim=obs_dim,
            action_dim=action_dim,
            env_info_sizes={})
    replay_buffers[METACONTROLLER] = SimpleReplayBufferDiscreteAction(
        max_replay_buffer_size=variant['replay_buffer_size'],
        observation_dim=obs_dim,
        action_dim=len(operators),
        env_info_sizes={})
    if variant['epsilon_decay']:
        exploration_strategy = EpsilonGreedyWithDecay(
            action_space=expl_env.action_space, num_epochs=variant['algorithm_kwargs']['num_epochs']
        )
        meta_exploration_strategy = EpsilonGreedyWithDecay(
            action_space=Discrete(len(operators)), num_epochs=variant['algorithm_kwargs']['num_epochs']
        )
    else:
        exploration_strategy = EpsilonGreedy(
            action_space=expl_env.action_space,
        )
        meta_exploration_strategy = EpsilonGreedy(
            action_space=Discrete(len(operators)),
        )

    eval_path_collector = HRLPathCollector(
        eval_env,
        operator_qfs,
        policy=ArgmaxDiscretePolicy,
        intrinsic_critic=internal_critic,
        is_terminal=is_terminal,
        operators_list=operators
    )
    expl_path_collector = HRLPathCollector(expl_env,
                                           operator_qfs,
                                           strategy=exploration_strategy,
                                           metacontroller_strategy=meta_exploration_strategy,
                                           policy=ArgmaxDiscretePolicy,
                                           intrinsic_critic=internal_critic,
                                           epsilon_decay=variant['epsilon_decay'],
                                           metacontroller_epsilon_decay=variant['epsilon_decay'],
                                           is_terminal=is_terminal,
                                           operators_list=operators)
    trainer = HDQNTrainer(
        operator_qfs,
        operator_target_qfs,
        **variant['trainer_kwargs']
    )

    algorithm = HRLAlgorithm(
        trainer=trainer,
        exploration_env=expl_env,
        evaluation_env=eval_env,
        exploration_data_collector=expl_path_collector,
        evaluation_data_collector=eval_path_collector,
        replay_buffers=replay_buffers,
        **variant['algorithm_kwargs']
    )
    algorithm.to(ptu.device)
    algorithm.train()




if __name__ == "__main__":




    parser = argparse.ArgumentParser()

    parser.add_argument("--transfer",
                        required=True,
                        help="Path to model for transfer")

    parser.add_argument("--env",
                        default="OfficeWorld-deliver-mail-v0",
                        help="Environment")

    parser.add_argument("--total-epochs",
                        type=int,
                        default=3000,
                        help="Total epochs for training")

    parser.add_argument("--buffer-size",
                        type=int,
                        default=1e6,
                        help="Max buffer size")

    parser.add_argument("--learning-rate",
                        type=float,
                        default=0.0003,
                        help="Max buffer size")


    parser.add_argument("--max-episode-length",
                        type=int,
                        default=100,
                        help="Max Episode Path Length")


    parser.add_argument("--batch-size",
                        type=int,
                        default=128,
                        help="Batch size")

    parser.add_argument('--decay-epsilon', action='store_true', default=False,
                        help="enable the epsilon decay strategy for exploration")


    args = parser.parse_args()

    # noinspection PyTypeChecker
    variant = dict(
        algorithm="HDQN-transfer",
        model_file= args.transfer,
        version=f"HDQN-transfer-{args.env}",
        env =args.env,
        intrinsic_reward=30,
        intrinsic_cost=-0.1,
        epsilon_decay=args.decay_epsilon,
        replay_buffer_size=int(args.buffer_size),
        algorithm_kwargs=dict(
            num_epochs=args.total_epochs,
            num_eval_steps_per_epoch=10*args.max_episode_length,
            num_trains_per_train_loop=10*args.max_episode_length,
            num_expl_steps_per_train_loop=10*args.max_episode_length,
            min_num_steps_before_training=10*args.max_episode_length,
            max_path_length=args.max_episode_length,
            batch_size=args.batch_size,
        ),
        trainer_kwargs=dict(
            discount=0.99,
            learning_rate=args.learning_rate,
        )
    )
    exp_id = os.getpid()
    setup_logger(variant['version'], variant=variant, snapshot_mode="gap_and_last",snapshot_gap=20,exp_id=exp_id)
    if torch.cuda.is_available():
        ptu.set_gpu_mode('gpu') # optionally set the GPU (default=False)
    experiment(variant)
