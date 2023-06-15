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
        state = { 'species': [], 'generations': [] }
        try:
            with open(self.state, 'r') as f:
                state = json.load(f)
        except FileNotFoundError:
            pass

        self.species = [ParameterMutationList(self.param_list, s['id'], s['parent'], s['values']) for s in state['species']]
        self.generations = [[self.species[p] for p in g] for g in state['generations']]
        self.next_id = len(self.species)

    def save(self):
        state = {
            'species': [{'id': s.id, 'parent': s.parent, 'values': s.get_parameters()} for s in self.species],
            'generations': [[p.id for p in gen] for gen in self.generations]
        }
        with open(self.state, 'w') as f:
            json.dump(state, f)

    def display(self, gen = None):
        for idx, g in enumerate(self.generations if gen is None else [self.generations[gen]]):
            print(f"**Generation {idx if gen is None else len(self.generations)-1 if gen == -1 else gen}")
            for p in g:
                print(f"  {p}")

    def calculate_fitness(self):
        for params in self.species:
            if self.evaluator.get_evaluation(params) is None:
                self.evaluator.perform_evaluation(params)
        self.evaluator.wait_all()
    
    def rank(self):
        results = [self.evaluator.get_evaluation(params) for params in self.species]
        top = sorted(zip(self.species, results), key=lambda x: x[1][0] if x[1] is not None else -float('inf'), reverse=True)
        
        print('---- RANKING ----')
        for param, result in top:
            print(f"  {result[0]:.3f} {result[1]:.3f} {param}")
        
        return [x[0] for x in top]
    
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
                s = ParameterMutationList(self.param_list, self.next_id)
                new_generation.append(s)
                self.species.append(s)                
                self.next_id += 1
            elif 'pick' in selection:
                new_generation.append(self.pick(selection['pick'], top))                
            elif 'mutate' in selection:
                s = self.pick(selection['mutate'], top).mutate(self.next_id, selection['mutate']['iter'])
                new_generation.append(s)
                self.species.append(s) 
                self.next_id += 1
            elif 'breed' in selection:
                mom = self.pick(selection['breed']['mom'], top)
                dad = self.pick(selection['breed']['dad'], top)
                s = mom.breed(self.next_id, dad)
                new_generation.append(s)
                self.species.append(s) 
                self.next_id += 1
            else:
                raise Exception('Invalid selection: '+selection)
            
        self.save()

    def run(self, num_generations = 1):
        for gen in range(num_generations):
            # New generation?
            if gen >= len(self.generations):
                # Spawn
                if gen == 0:
                    self.spawn_generation(self.population['initial'])
                else:
                    self.spawn_generation(self.population['selection'])
                # Evaluate
                self.calculate_fitness()
            # Display
            self.display(gen)