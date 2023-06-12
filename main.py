import random
import json
import sys
import glob
from statistics import mean, stdev

class SamplingParameter():
    def __init__(self, id, temperature=1.0, repetition_penalty=1.176, top_k=1, top_p=1.0, repeat_last_n=256, parents = []):
        self.temperature = temperature
        self.repetition_penalty = repetition_penalty
        self.top_k = top_k
        self.top_p = top_p
        self.repeat_last_n = repeat_last_n
        self.parents = parents
        self.id = id

    def __str__(self):
        return f"[{self.id}] temperature={self.temperature:0.3f}, repetition_penalty={self.repetition_penalty:0.3f}, top_k={self.top_k}, top_p={self.top_p:0.3f}, repeat_last_n={self.repeat_last_n}"

    def json(self):
        return json.dumps(self.__dict__)
    
    def breed(self, other, new_id):
        return SamplingParameter(id=new_id,
                                 temperature=random.choice([self.temperature, other.temperature]),
                                 repetition_penalty=random.choice([self.repetition_penalty, other.repetition_penalty]),
                                 top_k=random.choice([self.top_k, other.top_k]),
                                 top_p=random.choice([self.top_p, other.top_p]),
                                 repeat_last_n=random.choice([self.repeat_last_n, other.repeat_last_n]),
                                 parents=[self.id, other.id])
    
    def mutate(self, iter = 1):
        for i in range(iter):
            param = random.choice(['temperature', 'repetition_penalty', 'top_k', 'top_p', 'repeat_last_n'])
            if param == 'temperature':
                self.temperature *= random.uniform(0.9, 1.05)
            elif param == 'repetition_penalty':
                self.repetition_penalty *= random.uniform(0.95, 1.05)
            elif param == 'top_k':
                self.top_k += random.randint(-1, 1)
                if self.top_k < 1:
                    self.top_k = 1
            elif param == 'top_p':
                self.top_p *= random.uniform(0.9, 1.1)
                if self.top_p > 1.0:
                    self.top_p = 1.0
            elif param == 'repeat_last_n':
                self.repeat_last_n += random.randint(-32, 8)
                if self.repeat_last_n < 8:
                    self.repeat_last_n = 8

def get_eval_data(id, language = 'both'):
    pattern = f"../can-ai-code/results/eval*params?{id}_mzedp-vicuna-13b*.ndjson"
    eval_files = glob.glob(pattern) 
    evals = []
    for eval in eval_files:
        total = 0
        passed = 0
        with open(eval, 'r') as f:
            tests = [json.loads(x) for x in f.readlines()]
            for test in tests:
                if test['language'] == language or language == 'both':
                    total += test['total']
                    passed += test['passed']
        evals.append(passed / total if total != 0 else 0)

    return evals

if len(sys.argv) == 1:
    print('bad usage')
    sys.exit(1)

if sys.argv[1] == 'seed':
    params = [SamplingParameter(i) for _ in range(10)]
    for i in range(5):
        params[i].mutate(iter=10)
        with open(f"params-{i}.json", "w") as f:
            f.write(params[i].json())
        print(i, params[i])
elif sys.argv[1] == 'eval':
    files = glob.glob('params-*.json')
    for file in sorted(files):
        with open(file, 'r') as f:
            params = json.load(f)
        params = SamplingParameter(**params)

        eval_both = get_eval_data(params.id)
        eval_js = get_eval_data(params.id, 'javascript')
        eval_py = get_eval_data(params.id, 'python')

        print(file, params, f"both {mean(eval_both):.3f} {stdev(eval_both):.3f} JS {mean(eval_js):.3f} {stdev(eval_js):.3f} PY {mean(eval_py):.3f} {stdev(eval_py):.3f}")
elif sys.argv[1] == 'breed':
    files = glob.glob('params-*.json')
    next_id = len(files)

    if len(sys.argv) != 4:
        print('usage: breed id0 id1')
        sys.exit(1)

    id0 = sys.argv[2]
    id1 = sys.argv[3]

    with open(f"params-{id0}.json", 'r') as f:
        params0 = SamplingParameter(**json.load(f))

    with open(f"params-{id1}.json", 'r') as f:
        params1 = SamplingParameter(**json.load(f))

    child = params0.breed(params1, next_id)
    child.mutate(iter=1)
    print('Spawned:', child)
    with open(f"params-{next_id}.json", "w") as f:
        f.write(child.json())