from parameter import ParameterMutationList

class Evolution():
    def __init__(self, evaluator, param_list, config):
        self.evaluator = evaluator
        self.param_list = param_list
        self.config = config
        self.generations = []
        self.next_id = 0

    def display(self):
        for idx, g in enumerate(self.generations):
            print(f"**Generation {idx}")
            for p in g:
                print(f"  {p}")

    def rank(self):
        if len(self.generations) == 0:
            return []
        else:
            return self.generations[-1]

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
            elif 'pick' in selection:
                new_generation.append(self.pick(selection['pick'], top))                
            elif 'mutate' in selection:
                new_generation.append(self.pick(selection['mutate'], top).mutate(self.next_id, selection['mutate']['iter']))
            elif 'breed' in selection:
                mom = self.pick(selection['breed']['mom'], top)
                dad = self.pick(selection['breed']['dad'], top)
                new_generation.append(mom.breed(self.next_id, dad))
            else:
                raise Exception('Invalid selection: '+selection)
            self.next_id += 1

    def next_generation(self):
        if len(self.generations) == 0:
            self.spawn_generation(self.config['initial'])
        else:
            self.spawn_generation(self.config['selection'])

    def run(self):
        pass