# MLFlow

`MLFLOW_TRACKING_URI` is set to `/workspace/mlruns` in docker image.

To access mlflow ui, start your docker image with an additional port 

    -p 5000:5000
    
And from a jupyterlab terminal, execute

    mlflow server --host 0.0.0.0
    
Then you can access mlflow ui from : http://localhost:5000/