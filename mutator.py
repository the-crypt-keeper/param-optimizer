import random
import yaml
from copy import copy

# A single mutatable parameter
class ParameterMutation:
    def __init__(self, parameter, initial_value, mutation_type, mutation_value, max_value = None, min_value = None):
        self.parameter = parameter
        self.value = initial_value
        self.mutation_type = mutation_type
        self.mutation_value = mutation_value
        self.min_value = min_value
        self.max_value = max_value

    def gen_value(self):
        if 'uniform' in self.mutation_value:
            v = random.uniform(*self.mutation_value['uniform'])
        elif 'constant' in self.mutation_value:
            v = self.mutation_value['constant']
        if self.min_value is not None and v < self.min_value:
            v = self.min_value
        elif self.max_value is not None and v > self.max_value:
            v = self.max_value
        return v

    def mutate(self):
        if self.mutation_type == 'additive':
            self.value += self.gen_value()
        elif self.mutation_type == 'geometric':
            self.value *= self.gen_value()

    def __repr__(self):
        value_str = f'{self.value}' if isinstance(self.value, int) else f'{self.value:.3f}'
        return f'{self.parameter}: {value_str}'

# A set of mutatable parameters
class ParameterMutationList:
    def __init__(self, params, id, parent = []):
        self.id = id
        self.parent = parent
        self.mutation_list = [ParameterMutation(**mutation_dict) for mutation_dict in params]

    def get_parameters(self):
        return {mutation.parameter: mutation.value for mutation in self.mutation_list}
    
    def clone(self, new_id):
        params = [copy(mutation.__dict__) for mutation in self.mutation_list]
        for p in params:
            p['initial_value'] = p.pop('value')
        return ParameterMutationList(params, new_id, [self.id])
    
    def mutate(self, new_id, iter):
        mutant = self.clone(new_id)
        for _ in range(iter):
            mutation = random.choice(mutant.mutation_list)
            mutation.mutate()
        return mutant

    def breed(self, new_id, other):
        child = self.clone(new_id)
        child.parent = [self.id, other.id]
        other_params = other.get_parameters()
        for mutation in child.mutation_list:
            mutation.value = random.choice([mutation.value, other_params[mutation.parameter]])
        return child

    def __repr__(self):
        return f"[{self.id:2d}] "+' '.join([str(mutation) for mutation in self.mutation_list])

class FitnessEvaluator():
    def get_evaluation(self, id):
        return None
    
    def perform_evaluation(self, id):
        pass

    def wait_all(self):
        pass

class Evolution():
    def __init__(self, param_list, evaluator, config):
        self.evaluator = evaluator
        self.param_list = param_list
        self.config = config
        self.generations = []

    def pick(self):

    def create_generation(self):
        pass

    def run(self):
        pass

config = yaml.safe_load(open('config.yaml'))
p1 = ParameterMutationList(config['params'], 0)
print(p1)
p2 = p1.mutate(1, 10)
print(p2)
p3 = p1.breed(2, p2)
print(p3)
print(p3.get_parameters())