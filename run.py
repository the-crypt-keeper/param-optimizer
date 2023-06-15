import yaml
import json
import subprocess
from fitness import FitnessBase
from evolution import Evolution
from pathlib import Path
import glob
import sys

def stream_shell_command(command):
    try:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        captured_output = ""
        return_code = None

        while True:
            output = process.stdout.readline()
            stripped_output = output.strip()
            print(stripped_output)
            captured_output += stripped_output + '\n'

            # Check for process completion
            return_code = process.poll()
            if return_code is not None:
                # Collect remaining output, if any
                for output in process.stdout.readlines():
                    stripped_output = output.strip()
                    print(stripped_output)
                    captured_output += stripped_output + '\n'
                break

        return captured_output.strip(), return_code

    except subprocess.CalledProcessError as e:
        # Handle any errors that occurred during command execution
        print("Error:", e)
        return None, e.returncode
    
class FitnessCanAiCode(FitnessBase):
    def __init__(self, input, language, interviewer, evaluate, paramdir, paramprefix, resultglob):
        self.language = language
        self.input = input
        self.interviewer = interviewer
        self.evaluate = evaluate
        self.paramdir = paramdir
        self.paramprefix = paramprefix
        self.resultglob = resultglob

    def perform_evaluation(self, params):
        param_file = Path(self.paramdir).joinpath(f"{self.paramprefix}-{params.id}.json")
        with open(param_file, 'w') as f:
            json.dump(params.get_parameters(), f)

        cmd_line = f"{self.interviewer} --input {self.input} --params {param_file}"
        print("Executing Interview:", cmd_line)
        #output, ret = stream_shell_command(cmd_line)

        eval_files = glob.glob(self.resultglob.replace('{id}', str(params.id)))
        if len(eval_files) != 1:
            print('Interview failed: ', params, eval_files)
            return False
        
        cmd_line = f"{self.evaluate} --input {eval_files[0]}"
        print("Executing Evalulation:", cmd_line)
        #output, ret = stream_shell_command(cmd_line)
        
    def get_evaluation(self, params):
        eval_files = glob.glob(self.resultglob.replace('interview_','eval_').replace('{id}', str(params.id)))
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

        return sum(evals) / len(evals)
    
if len(sys.argv) < 3:
    print('usage: run.py <config.yaml> <generations>')
    sys.exit(1)

config = yaml.safe_load(open(sys.argv[1]))
if 'FitnessCanAiCode' in config['fitness']:
    evaluator = FitnessCanAiCode(**config['fitness']['FitnessCanAiCode'])
else:
    raise Exception("Valid fitness not defined")
evolver = Evolution(evaluator, config)
evolver.run(int(sys.argv[2]))
evolver.rank()