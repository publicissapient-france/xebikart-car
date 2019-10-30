import os
import subprocess

import argparse

import mlflow
import papermill as pm


parser = argparse.ArgumentParser(description='Execute and log notebook to mlflow')
parser.add_argument('--input', dest='notebook_input', required=True,
                    help='path to notebook')
parser.add_argument('--output', dest='notebook_output', required=True,
                    help='path to output notebook')

args, raw_parameters = parser.parse_known_args()


def convert_to_type(arg):
    try:
        return int(arg)
    except ValueError:
        pass
    try:
        return float(arg)
    except ValueError:
        pass
    return arg


parameters = {k[2:]: convert_to_type(v) for k, v in zip(raw_parameters[::2], raw_parameters[1::2])}

print("input", args.notebook_input)
print("output", args.notebook_output)
print("parameters", parameters)


print("Start xvfb :1 screen 0")
subprocess.Popen('/usr/bin/Xvfb :1 -screen 0 600x400x24', shell=True, preexec_fn=os.setsid)

pm.execute_notebook(
   args.notebook_input,
   args.notebook_output,
   parameters=parameters
)

mlflow.log_artifact(args.notebook_output)
