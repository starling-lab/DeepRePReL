# Deep RePReL

Combining Planning and Deep RL for acting in relational domains

This repository contains batch RL based implementation of RePReL with deep reinforcement learning as well as deep relational reinforcement learning. More details about the batch RePReL learning algorithm can be found in our paper [here](https://openreview.net/forum?id=ffLKUFlsFK0). 

> Implementation of [Hybrid Deep RePReL](https://starling.utdallas.edu/papers/HybridDeepRePReL/) to be added soon.

## Installation

1. Clone the github repo
   
```
$ git clone https://github.com/harshakokel/DeepRePReL.git ./DeepRePReL
$ cd DeepRePReL
```

2. Create a python virtual env and installing the requirements

```
$ virtualenv -p python3 reprel_venv
$ source reprel_venv/bin/activate
(reprel_venv) $ pip install -r environment/reprel-requirements.txt
```

3. Install gym environment and respective requirements.

Taxi domain and office world requirements 
* `pip install git+https://github.com/harshakokel/RePReL-domains.git@main`

FetchBlockConstruction domain requirements
* `pip install git+https://github.com/harshakokel/fetch-block-construction.git@master`
* `pip install mujoco-py>=2.0.2`

4. Run experiments from [examples](./examples). Refer to the [RePReL documentation](./docs/RePReL.md) for more details.

> The tabular reinforcement learning implementation is available in the other repository [here](https://github.com/harshakokel/RePReL).

## Citation

Please consider citing the following paper if you find our codes helpful. Thank you!

For RePReL framework,
```
@article{KokelMNRT21,
   title={RePReL: Integrating Relational Planning and Reinforcement Learning for Effective Abstraction},
    author={Kokel, Harsha and Manoharan, Arjun and Natarajan, Sriraam and Balaraman, Ravindran and Tadepalli, Prasad},
    journal={Proceedings of the International Conference on Automated Planning and Scheduling},
    number={1},
    volume={31},
    year={2021},
    month={May},
    pages={533--541},
    url={https://ojs.aaai.org/index.php/ICAPS/article/view/16001}
 }

```

For Deep RePReL framework and the batch learning algorithm,

```
@article{KokelMNBTDRL,
   title={Deep RePReL-Combining Planning and Deep RL for acting in relational domains},
   author={Kokel, Harsha and Manoharan, Arjun and Natarajan, Sriraam and Ravindran, Balaraman and Tadepalli, Prasad},
   journal={Deep {RL} Workshop at {NeurIPS}},
   year={2021},
   url={https://openreview.net/forum?id=ffLKUFlsFK0}
}
```

For D-FOCI and use of SRL,

```
@article{KokelMNBTSTARAI,
   title={Dynamic probabilistic logic models for effective abstractions in RL},
   author={Kokel, Harsha and Manoharan, Arjun and Natarajan, Sriraam and Ravindran, Balaraman and Tadepalli, Prasad},
   journal = {{StarAI} Workshop at {IJCLR}},
   url={https://arxiv.org/abs/2110.08318}
   year={2021},
}
```

## Credits

The core of this repository is the [RLkit](https://github.com/rail-berkeley/rlkit) library by RAIL Berkeley organization. ReNN code for FetchBlockConstruction domain is obtained from the [rlkit-relational](https://github.com/richardrl/rlkit-relational) repository made available by the authors of Li et al. [1]. The repository also includes implementation of taskable RL framework proposed in Illanes et al. [2]

## References

[1] Li, Richard, Allan Jabri, Trevor Darrell, and Pulkit Agrawal. "Towards practical multi-object manipulation using relational reinforcement learning." In 2020 IEEE International Conference on Robotics and Automation (ICRA), pp. 4051-4058. IEEE, 2020.  

[2] Illanes, León, Xi Yan, Rodrigo Toro Icarte, and Sheila A. McIlraith. "Symbolic plans as high-level instructions for reinforcement learning." In Proceedings of the International Conference on Automated Planning and Scheduling, vol. 30, pp. 540-550. 2020.
