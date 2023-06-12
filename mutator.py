import random
import yaml

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
        self.mutation_list = []
        self.params = params
        for mutation_dict in params:
            mutation = ParameterMutation(**mutation_dict)
            self.mutation_list.append(mutation)
            setattr(self, mutation.parameter, mutation.value)

    def mutate(self, iter=1):
        for _ in range(iter):
            mutation = random.choice(self.mutation_list)
            mutation.mutate()
            setattr(self, mutation.parameter, mutation.value)

    def breed(self, other, new_id):
        child = ParameterMutationList(self.params, new_id, [self.id, other.id])
        for mutation in self.mutation_list:
            other_v = getattr(other, mutation.parameter)
            child.parameters[mutation.parameter] = random.choice([mutation.value, other_v])
        return child
    
    def __repr__(self):
        return f"[{self.id:2d}] "+' '.join([str(mutation) for mutation in self.mutation_list])

config = yaml.safe_load(open('config.yaml'))
params = ParameterMutationList(config['params'], 0)
print(params)
params.mutate(10)
print(params)
params.mutate(10)