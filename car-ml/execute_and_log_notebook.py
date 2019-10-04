import argparse

import mlflow
import papermill as pm


parser = argparse.ArgumentParser(description='Execute and log notebook to mlflow')
parser.add_argument('--input', dest='notebook_input', required=True,
                    help='path to notebook')
parser.add_argument('--output', dest='notebook_output', required=True,
                    help='path to output notebook')

args, raw_parameters = parser.parse_known_args()

parameters = {k: v for k, v in zip(raw_parameters[::2], raw_parameters[1::2])}

print("input", args.notebook_input)
print("output", args.notebook_output)
print("parameters", parameters)


pm.execute_notebook(
   args.notebook_input,
   args.notebook_output,
   parameters=parameters
)

mlflow.log_artifact(args.notebook_output)
