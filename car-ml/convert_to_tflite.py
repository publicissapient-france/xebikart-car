import argparse

import mlflow.keras


parser = argparse.ArgumentParser(description='Execute and log notebook to mlflow')
parser.add_argument('--runid', dest='runid', required=True,
                    help='MLFlow run id')
parser.add_argument('--model-path', dest='model_path', required=True,
                    help='path to the keras model')
parser.add_argument('--output-path', dest='output_path', required=True,
                    help='path to save the model')

args = parser.parse_args()


def keras_model_to_tflite(model, out_filename):
    import tensorflow as tf

    inputs = model.inputs
    outputs = model.outputs
    with tf.keras.backend.get_session() as sess:
        converter = tf.lite.TFLiteConverter.from_session(sess, inputs, outputs)
        converter.optimizations = [tf.lite.Optimize.OPTIMIZE_FOR_SIZE]
        tflite_model = converter.convert()
        open(out_filename, "wb").write(tflite_model)


model = mlflow.keras.load_model(f"runs:/{args.runid}/{args.model_path}")
keras_model_to_tflite(model, args.output_path)
