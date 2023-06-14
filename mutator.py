import yaml
import json
import subprocess
from fitness import FitnessBase
from evolution import Evolution
from pathlib import Path
import glob

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
        eval_files = glob.glob(self.resultglob.replace('{id}', str(params.id)))
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

config = yaml.safe_load(open('config.yaml'))
evaluator = FitnessCanAiCode(
    language = 'both',
    input = 'can-ai-code/results/prepare_junior-dev_python_Vicuna-1p1.ndjson',
    interviewer = 'python3 can-ai-code/interview-llamacpp.py --ssh miner --threads 4 --model /home/miner/ai/models/v3/ggml-vicuna-7b-1.1-q5_0.bin',
    evaluate = 'python3 can-ai-code/evaluate.py',
    paramdir = 'python-vicuna-7b/',
    paramprefix = 'vicuna-7b',
    resultglob = 'can-ai-code/results/eval_junior-dev_python_Vicuna-1p1*vicuna-7b-{id}*.ndjson'
)

evolver = Evolution(evaluator, config['params'], config['population'])
evolver.run(1)