import json
from parameter import ParameterMutationList

class Evolution():
    def __init__(self, evaluator, config):
        self.evaluator = evaluator

        self.param_list = config['params']
        self.population = config['population']
        self.state = config['state']

        self.load()

    def load(self):
        state_generations = []
        try:
            with open(self.state, 'r') as f:
                state_generations = json.load(f)
        except FileNotFoundError:
            pass

        self.generations = []
        for gen in state_generations:
            next_gen = [ParameterMutationList(self.param_list, p['id'], p['parent'], p) for p in gen]
            self.generations.append(next_gen)

        ids = [p['id'] for gen in state_generations for p in gen]
        print(ids)
        self.next_id = max(ids)+1 if len(ids) != 0 else 0

    def save(self):
        state_generations = []
        for gen in self.generations:
            next_gen = []
            for p in gen:
                serial_p = p.get_parameters()
                serial_p['id'] = p.id
                serial_p['parent'] = p.parent
                next_gen.append(serial_p)
            state_generations.append(next_gen)

        with open(self.state, 'w') as f:
            json.dump(state_generations, f)

    def display(self, gen = None):
        for idx, g in enumerate(self.generations if gen is None else [self.generations[gen]]):
            print(f"**Generation {idx if gen is None else len(self.generations)-1 if gen == -1 else gen}")
            for p in g:
                print(f"  {p}")

    def calculate_fitness(self):
        for params in self.generations[-1]:
            if self.evaluator.get_evaluation(params) is None:
                self.evaluator.perform_evaluation(params)
        self.evaluator.wait_all()
    
    def rank(self):
        if len(self.generations) == 0:
            return []
        else:
            flat_params = []
            for gen in self.generations:
                for p in gen:
                    if p not in flat_params:
                        flat_params.append(p)

            results = [self.evaluator.get_evaluation(params) for params in flat_params]
            top = sorted(zip(flat_params, results), key=lambda x: x[1] if x[1] is not None else -float('inf'), reverse=True)
            print('---- RANKING ----')
            for param, result in top:
                print(f"  {result} {param}")
            sorted_generation = [x[0] for x in top]
            return sorted_generation
    
    def pick(self, condition, top):
        if 'top' in condition:
            return top[condition['top']]
        elif 'current' in condition:
            return self.generations[-1][condition['current']]
        elif 'last' in condition:
            return self.generations[-2][condition['last']]
        else:
            raise Exception('Invalid condition: '+condition)
        
    def spawn_generation(self, selections):
        top = self.rank()

        new_generation = []
        self.generations.append(new_generation)

        for selection in selections:
            if 'initial' in selection:
                new_generation.append(ParameterMutationList(self.param_list, self.next_id))
                self.next_id += 1
            elif 'pick' in selection:
                new_generation.append(self.pick(selection['pick'], top))                
            elif 'mutate' in selection:
                new_generation.append(self.pick(selection['mutate'], top).mutate(self.next_id, selection['mutate']['iter']))
                self.next_id += 1
            elif 'breed' in selection:
                mom = self.pick(selection['breed']['mom'], top)
                dad = self.pick(selection['breed']['dad'], top)
                new_generation.append(mom.breed(self.next_id, dad))
                self.next_id += 1
            else:
                raise Exception('Invalid selection: '+selection)
            
        self.save()

    def next_generation(self):
        if len(self.generations) == 0:
            self.spawn_generation(self.population['initial'])
        else:
            self.spawn_generation(self.population['selection'])

    def run(self, num_generations = 1):
        for gen in range(num_generations):
            if gen >= len(self.generations):
                self.next_generation()
                self.calculate_fitness()
            self.display(gen)