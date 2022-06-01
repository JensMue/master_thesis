""" A module to evaluate model performance:"""

import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import mean_absolute_percentage_error
from sklearn.metrics import r2_score


def evaluate(y_true, y_pred, mse=True, rmse=True, mae=True, mape=True, r2=True):
    """Prints and plots a model evaluation:"""

    print("Model performance")
    print("--------------------------------------")
    if mse:
        print('MSE: {}'.format(round(mean_squared_error(y_true, y_pred), 2)))
    if rmse:
        print('RMSE: {}'.format(round(np.sqrt(mean_squared_error(y_true, y_pred)), 2)))
    if mae:
        print('MAE: {}'.format(round(mean_absolute_error(y_true, y_pred), 2)))
    if mape:
        print('MAPE: {}%'.format(round(100 * mean_absolute_percentage_error(y_true, y_pred), 2)))
    if r2:
        print('R2: {}'.format(round(r2_score(y_true, y_pred), 2)))
    print("\n")

    
def plot_performance(y_true, y_pred):
    """Plots model performance."""

    residuals = y_true - y_pred
    fig, axs = plt.subplots(1, 3, figsize=(12,4))
    
    axs[0].set(xlabel='y_true', ylabel='y_pred')
    axs[0].scatter(y_true, y_pred, s=3, alpha=0.3)
    axs[0].plot(y_true, y_true, color='k', linestyle='--')
    axs[0].set_title('True vs Predicted', fontsize=16)
    axs[0].ticklabel_format(axis="both", style="sci", scilimits=(0, 0))
    
    axs[1].set_title('Normality of errors', fontsize=16)
    axs[1].hist(residuals, bins=200)
    axs[1].set_xlim((-10000,10000))
    axs[1].set(xlabel='Prediction error', ylabel='Count')
    axs[1].axvline(x=0.0, color='k', linestyle='--')
    axs[1].ticklabel_format(axis="both", style="sci", scilimits=(0, 0))
    
    axs[2].set_title('Scedasticity of errors', fontsize=16)
    axs[2].scatter(y_true, residuals, s=3, alpha=0.3)
    axs[2].axhline(y=0.0, color='k', linestyle='--')
    axs[2].set(xlabel='True value', ylabel='Prediction error')
    axs[2].ticklabel_format(axis="both", style="sci", scilimits=(0, 0))
    
    plt.tight_layout()
    plt.show()