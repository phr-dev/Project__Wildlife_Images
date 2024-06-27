import subprocess
import os
import mlflow
import hyperopt
import tensorflow as tf
import time
import requests

def _is_mlflow_server_running(tracking_url):
    """Check if the MLflow server is running by sending a request to the tracking URL."""
    try:
        response = requests.get(tracking_url)
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        return False

def start_mlflow_server(experiment_name="", timeout=60):
    """Launches an MLflow server in a background process, which can be accessed at http://127.0.0.1:5000
    All files generated by MLflow will be saved in the mlflow folder.

    Args:
        experiment_name (str): Name of the MLflow experiment, must not be empty. Defaults to "".
        timeout (int): Time to wait for the server to start in seconds. Defaults to 60.
    """
    # Disallow empty experiment name
    assert experiment_name != ""

    # Define the path to the MLflow artifacts folder
    relative_artifacts_path = "../mlflow"
    absolute_artifacts_path = os.path.abspath(relative_artifacts_path)

    # Convert the absolute path to a proper file URI
    tracking_url = "http://127.0.0.1:5000"
    if os.name == 'nt':  # Windows
        tracking_uri = f"file:///{absolute_artifacts_path.replace(os.sep, '/')}"
    else:  # macOS and Linux
        tracking_uri = f"file://{absolute_artifacts_path}"

    # Set the tracking URI to the desired folder
    mlflow.set_tracking_uri(tracking_uri)
    print(f"Tracking URI set to: {tracking_uri}")

    # Define the command to start the MLflow server
    command = [
        "mlflow", "server",
        "--backend-store-uri", tracking_uri,
        "--default-artifact-root", tracking_uri
    ]

    # Run the command based on the operating system
    if os.name == "nt":  # Windows
        subprocess.Popen(command, creationflags=subprocess.CREATE_NEW_CONSOLE)
    else:  # macOS and Linux
        subprocess.Popen(command, start_new_session=True)

    print("MLflow server started in the background")

    # Check if the server is running
    start_time = time.time()
    while not _is_mlflow_server_running(tracking_url):
        if time.time() - start_time > timeout:
            raise TimeoutError(f"MLflow server did not start within {timeout} seconds.")
        time.sleep(1)  # wait for 1 second before retrying

    print("MLflow server is running")

    # Set the experiment
    mlflow.set_experiment(experiment_name)



class _MLflowLogger(tf.keras.callbacks.Callback):
    def on_epoch_end(self, epoch, logs=None):
        if logs is not None:
            # Log all metrics at the end of an epoch
            mlflow.log_metrics(logs, step=epoch)



def mlflow_train_keras_model(train_fn, train_data, valid_data, search_space, n_evals, mlflow_tags={}, log_model=True):

    mlflow_logger = _MLflowLogger()

    components = {
        "mlflow_logger": mlflow_logger,
    }

    def _objective_function(search_params=search_space):
        result = train_fn(
            search_params,
            components,
            train_data,
            valid_data
            )
        return result
    
    with mlflow.start_run(tags=mlflow_tags) as run:
        trials = hyperopt.Trials()
        best = hyperopt.fmin(
            fn=_objective_function,
            space=search_space,
            algo=hyperopt.tpe.suggest,
            max_evals=n_evals,
            trials=trials,
            trials_save_file="../mlflow/hyperopt_trials.txt"
        )
        
        best_run = sorted(trials.results, key=lambda x: x["val_accuracy"], reverse=True)[0]
        mlflow.log_params(best)
        mlflow.log_metric("final_val_loss", best_run["loss"])
        mlflow.log_metric("val_accuracy", best_run["val_accuracy"])

        for epoch_idx in range(len(best_run["history"].history["loss"])):
            for key in ("loss", "val_loss", "accuracy", "val_accuracy"):
                mlflow.log_metric(key, best_run["history"].history[key][epoch_idx], step=epoch_idx)

        if len(mlflow_tags) > 0:
            mlflow.set_tags(mlflow_tags)
        if log_model:
            mlflow.tensorflow.log_model(best_run["model"], "model")

    return run