class FitnessBase():
    def get_evaluation(self, id):
        print("FitnessBase: get_evaluation", id)
        return None
    
    def perform_evaluation(self, id):
        print("FitnessBase: perform_evaluation", id)
        pass

    def wait_all(self):
        print("FitnessBase: wait_all")
        pass

class FitnessCanAiCode(FitnessBase):
    def __init__(self, language = 'both'):
        self.language = language

    def get_evaluation(self, id):
        pattern = f"../can-ai-code/results/eval*params?{id}_mzedp-vicuna-13b*.ndjson"
        eval_files = glob.glob(pattern)
        if len(eval_files) == 0:
            return None
        
        evals = []
        for eval in eval_files:
            total = 0
            passed = 0
            with open(eval, 'r') as f:
                tests = [json.loads(x) for x in f.readlines()]
                for test in tests:
                    if test['language'] == self.language or self.language == 'both':
                        total += test['total']
                        passed += test['passed']
            evals.append(passed / total if total != 0 else 0)

        return evals