import argparse

import mlflow.keras

from xebikart.lite_functions import keras_model_to_tflite

parser = argparse.ArgumentParser(description='Execute and log notebook to mlflow')
parser.add_argument('--runid', dest='runid', required=True,
                    help='MLFlow run id')
parser.add_argument('--model-path', dest='model_path', required=True,
                    help='path to the keras model')
parser.add_argument('--output-path', dest='output_path', required=True,
                    help='path to save the model')

args = parser.parse_args()

model = mlflow.keras.load_model(f"runs:/{args.runid}/{args.model_path}")
keras_model_to_tflite(model, args.output_path)
