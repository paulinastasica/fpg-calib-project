"""
Contains functions used in the project, which aim is to recreate and verify results published in the non-peer-reviewed article: 
Paolo Tancioni, Ulisse Gendotti, arXiv:2112.03579,
"Gamma dose rate monitoring using a Silicon Photomultiplier-based plastic scintillation detector" 
"""

import numpy as np

def lin_fun(x_ch, a, b):
    
    """Linear function"""
    
    return a * x_ch + b


def log_fun(x_ch, a, b, c): 
    
    """Logarithmic function (suggested by the authors)"""
    
    return a * np.exp(-b * x_ch) + c 


def get_theo_dose_rate_value(spectrum, calib_data_fpg_meas):
    
    """Gets theoretical dose rate values for a given source and distance"""
    
    source = spectrum.split('_')[0]
    source = source[:2] + '-' + source[2:]
    distance = int(spectrum.split('_')[1].replace('cm', ''))

    return calib_data_fpg_meas[(calib_data_fpg_meas['Source'] == source)
                               & (calib_data_fpg_meas['Distance_cm'] == distance)]['TheorDoseRate_uSvh'].iloc[0]


def make_loss_fun(data_fpg_cps, calib_data_fpg_meas, spectra, fun):
    
    """Produces loss function for a given spectra and energy calibration function"""
    
    def loss_fun(params):
        
        """Loss function definition based on arXiv:2112.03579"""
        
        S=0

        for spectrum in spectra:
            d_exp = np.sum(data_fpg_cps[spectrum] * fun(data_fpg_cps[spectrum].index.values, *params))

            d_theo = get_theo_dose_rate_value(spectrum, calib_data_fpg_meas)
            S += (d_exp - d_theo)**2

        return S
    
    return loss_fun


def compute_accuracy(data_fpg_cps, calib_data_fpg_meas, spectra, opti_results, fun):
    
    """Computes accuracy for a given optimization results."""
    
    acc_list = []

    for spectrum in spectra:
    
        d_exp = np.sum(data_fpg_cps[spectrum] * fun(data_fpg_cps[spectrum].index.values, *opti_results['x']))
        
        d_theo = get_theo_dose_rate_value(spectrum, calib_data_fpg_meas)
    
        acc_list.append(100-((abs(d_theo - d_exp) / d_theo) * 100))

    return acc_list


def print_results(spectra, opti_results, acc_list):
    
    """Displays results in a readable way."""
    
    print('Optimizaton results:\n', opti_results)
    print('\nmeasurement\taccuracy [%]')
    for idx, _ in enumerate(spectra):
        print(f'{spectra[idx]}\t', '{0:.2f}'.format(acc_list[idx]))
    print('\nMean accuracy [%]: {:.2f}'.format(np.mean(acc_list)))
