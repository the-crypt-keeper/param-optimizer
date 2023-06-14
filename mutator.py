import yaml
from fitness import FitnessBase
from evolution import Evolution

config = yaml.safe_load(open('config.yaml'))
evaluator = FitnessBase()

evolver = Evolution(evaluator, config['params'], config['population'])
evolver.run(2)