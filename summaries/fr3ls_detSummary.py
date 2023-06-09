import pandas as pd
from matplotlib import pyplot as plt
from common.settings import *
from common.torch.snapshots import SnapshotManager
from common.utils import read_config_file


class FR3LS_DetSummary:
    def __init__(self,):
        # space holders initialization

        self.dataset_name = None
        self.experiment_path = None
        self.snapshots_dir_path = None
        self.snapshot_manager = None
        self.losses = None

        self.experiment_name = None
        self.embedding_instance_name = None

        self.other_losses = None

        self.horizon = None
        self.n_test_window = None

        self.epoch = None
        self.experiment_training_loss = None
        self.experiment_testing_loss = None
        self.experiment_other_losses = None

        self.config_dict = None

    def load_experiment(self, experiment_path: str):
        assert os.path.exists(experiment_path), "Path to experiment does not exist."
        self.experiment_path = experiment_path
        self.experiment_name = os.path.join(*[i for i in self.experiment_path.split(os.sep)[-1:]])
        config_file_path = os.path.join(experiment_path, 'config.gin')
        self.config_dict = read_config_file(config_file_path)
        self.dataset_name = eval(self.config_dict['ts_dataset_name'])
        self.horizon = eval(self.config_dict['horizon'])
        self.n_test_window = eval(self.config_dict['n_test_windows'])

        self.other_losses = ['MAPE', 'WAPE', 'SMAPE']

        self.snapshots_dir_path = os.path.join(experiment_path, 'snapshots')
        self.snapshot_manager = SnapshotManager(
            snapshot_dir=self.snapshots_dir_path,
            losses=['training', 'testing'],
            other_losses=self.other_losses,
        )
        self.losses = self.snapshot_manager.load_losses()

    def evaluate(self,):
        # Extract the experiment with the most inferior loss combination
        assert self.losses is not None, "Run load_experiment() before evaluate()"

        losses = self.losses.round(decimals=3).sort_values(["MAPE_loss", "testing_loss"]).head(1)

        self.epoch = losses.index[0]
        self.experiment_training_loss = losses['training_loss'].iloc[0]
        self.experiment_testing_loss = losses['testing_loss'].iloc[0]

        self.experiment_other_losses = {}
        for key in self.other_losses:
            self.experiment_other_losses[key + "_LOSS"] = losses[key + "_loss"].iloc[0]

    def summarize(self):
        assert self.experiment_training_loss is not None, "Run evaluate() before summarize()"
        summary = {
            "EXPERIMENT_NAME": [self.experiment_name],
            "DATASET_NAME": self.dataset_name,
            "EPOCH": self.epoch,
            "NUM_TEST_WINDOW": self.n_test_window,
            "HORIZON": self.horizon,
            "TRAINING_LOSS": self.experiment_training_loss,
            "TESTING_LOSS": self.experiment_testing_loss,
        }
        summary.update(self.experiment_other_losses)

        return pd.DataFrame(summary)

    def plot_loss_curves(self):
        assert self.losses is not None, "Run load_experiment() before evaluate()"
        title = self.experiment_name

        fig, axs = plt.subplots(2, 3, figsize=(10, 6))  # create a figure with a 2x3 grid of subplots

        axs[0, 0].plot(self.losses['training_loss'])
        axs[0, 0].set_title('training_loss')
        axs[0, 1].plot(self.losses['testing_loss'])
        axs[0, 1].set_title('testing_loss')

        axs[0, 2].plot(self.losses['MAPE_loss'])
        axs[0, 2].set_title('MAPE_loss')
        axs[1, 0].plot(self.losses['WAPE_loss'])
        axs[1, 0].set_title('WAPE_loss')
        axs[1, 1].plot(self.losses['SMAPE_loss'])
        axs[1, 1].set_title('SMAPE_loss')

        # add a common title for the whole figure
        fig.suptitle(title)

        # adjust the layout to avoid overlapping titles and labels
        fig.tight_layout()

        plt.show()


    def reset(self):
        self.dataset_name = None

        self.experiment_path = None
        self.snapshots_dir_path = None
        self.losses = None
        self.snapshot_manager = None

        self.experiment_name = None
        self.embedding_instance_name = None

        self.other_losses = None

        self.horizon = None
        self.n_test_window = None

        self.epoch = None
        self.experiment_training_loss = None
        self.experiment_testing_loss = None
        self.experiment_other_losses = None

        self.config_dict = None