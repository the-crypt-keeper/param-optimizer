import yaml
import json
import subprocess
from fitness import FitnessBase
from evolution import Evolution
from pathlib import Path
import glob
import sys
from statistics import mean, stdev

def stream_shell_command(command):
    try:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        # Stream the output to the terminal
        while True:
            output = process.stdout.readline().decode()
            if output:
                print(output, end='')
            if process.poll() is not None:
                break
            
        # Wait for the command to finish and get the return code
        return process.wait()
    except subprocess.CalledProcessError as e:
        # Handle any errors that occurred during command execution
        print("Error:", e)
        return e.returncode
    
class FitnessCanAiCode(FitnessBase):
    def __init__(self, input, language, interviewer, evaluate, paramdir, paramprefix, resultglob, samples):
        self.language = language
        self.input = input
        self.interviewer = interviewer
        self.evaluate = evaluate
        self.paramdir = paramdir
        self.paramprefix = paramprefix
        self.resultglob = resultglob
        self.samples = samples

    def perform_evaluation(self, params):
        # Write param file
        param_file = Path(self.paramdir).joinpath(f"{self.paramprefix}-{params.id}.json")
        with open(param_file, 'w') as f:
            json.dump(params.get_parameters(), f)

        # Execute interviewer
        cmd_line = f"{self.interviewer} --input {self.input} --params {param_file}"
        print("Executing Interview:", cmd_line)
        if stream_shell_command(cmd_line) != 0:
            print('Interview bad result!')

        # Find the interview result file
        interview_files = glob.glob(self.resultglob.replace('{id}', str(params.id)))
        if len(interview_files) != self.samples:
            print('WARNING: Interview iterations incorrect', params.id, len(interview_files))
        
        # Execute evaluator
        for interview_file in interview_files:
            # if the file already exists, skip it
            eval_file = interview_file.replace('interview_', 'eval_')
            if Path(eval_file).exists():
                continue

            cmd_line = f"{self.evaluate} --input {interview_file}"
            print("Executing Evalulation:", cmd_line)
            if stream_shell_command(cmd_line) != 0:
                print('Evaluation bad result!')

    def get_evaluation(self, params):
        # Find evaluator result files
        eval_files = glob.glob(self.resultglob.replace('interview_','eval_').replace('{id}', str(params.id)))
        
        # Read and aggregate them
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

        # Return the average and std. deviation
        return evals
    
if len(sys.argv) < 3:
    print('usage: run.py <config.yaml> <generations>')
    sys.exit(1)

config = yaml.safe_load(open(sys.argv[1]))
if 'FitnessCanAiCode' in config['fitness']:
    evaluator = FitnessCanAiCode(**config['fitness']['FitnessCanAiCode'])
else:
    raise Exception("Valid fitness not defined")
evolver = Evolution(evaluator, config)
evolver.calculate_fitness()
evolver.run(int(sys.argv[2]))
evolver.rank()