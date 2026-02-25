#!/usr/bin/env python
# coding: utf-8

#  ## Functions notebook
#  
# This notebook consists of functions for data analysis in `SCENES` project

# ## Create the data tree and count the number of files 

# In[4]:


import os
import re
import datetime
import pandas as pd
import numpy as np
from scipy.fft import fft2, fftshift
from scipy.stats import linregress


# In[5]:


# Create a function to accept a stat path and store a data tree as a text file in the 'results' folder

def data_tree(input_path, output_dir, output_file):
    """
    Generate directory tree from input_path and save to output_dir/output_file.
    Excludes only temporary files starting with '~$'.
    """

    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, output_file)

    exclude_pattern = re.compile(r'^~\$')

    with open(output_path, 'w', encoding='utf-8') as f_out:

        for dirpath, dirnames, filenames in os.walk(input_path, topdown=True):

            # exclude temporary files only
            filenames[:] = [f for f in filenames if not exclude_pattern.match(f)]

            level = os.path.relpath(dirpath, input_path).count(os.sep)
            indent = ' ' * 4 * level

            f_out.write(f"{indent}{os.path.basename(dirpath)}/\n")

            subindent = ' ' * 4 * (level + 1)
            for fname in filenames:
                f_out.write(f"{subindent}{fname}\n")



# In[6]:


# Create a function to count all files in the datatree

def count_files(startpath):
    file_count = 0
    for dirpath, _, filenames in os.walk(startpath):
        file_count += len(filenames)

    return file_count


# In[7]:


# Create a function to count all measurement folders in the datatree

def count_folders(startpath):
    folder_count = 0
    pattern = re.compile(r'^\w{4}_\w{8}T\w{4}$')  # Regular expression pattern for the folder name format

    for dirpath, dirnames, _ in os.walk(startpath):
        for dirname in dirnames:
            if pattern.match(dirname):
                folder_count += 1

    return folder_count


# In[8]:


# This function give warning message for any subdirectoris that doesn't have correct data files number.

def missing_files(startpath, output_file):

    # Open the output file for writing
    output_path = os.path.join(result_dir, output_file)
    with open(output_path, 'w') as f_out:

        different_file_counts = {}

        exclude_pattern = re.compile(r'.*(_gopro)$|^\..*|~$')

        for dirpath, dirnames, filenames in os.walk(startpath, topdown=True):
            dirnames[:] = [d for d in dirnames if not exclude_pattern.match(d)]
            filenames = [f for f in filenames if not exclude_pattern.match(f)]
            #dirnames[:] = [d for d in dirnames if d not in ('results', 'pilot', 'derivatives', 'metadata', 'temporary')]

            level = dirpath.replace(startpath, '').count(os.sep)
            file_count = len(filenames)

            if level == 2:
                if any(filename.startswith('acttrust') for filename in filenames):
                    if file_count != 4:
                        missing_file_count = 4 - file_count
                        different_file_counts[dirpath] = missing_file_count


                elif any(filename.startswith('testo') for filename in filenames):
                    if file_count != 1:
                        missing_file_count = 1
                        different_file_counts[dirpath] = missing_file_count
                else:
                    if any(filename.startswith('jeti') for filename in filenames):
                        if file_count != 8:
                            missing_file_count = 8 - file_count
                            different_file_counts[dirpath] = missing_file_count

                    elif any(filename.startswith('giga') for filename in filenames):
                        if file_count != 6:
                            missing_file_count = 6 - file_count
                            different_file_counts[dirpath] = missing_file_count

        if different_file_counts:
            print('WARNING: The following subdirectories do not have correct files numbers:', file=f_out)

            for dirpath, count in different_file_counts.items():
                print(f'{dirpath} has {count} missing files', file=f_out)



# ## Create the `measurement device` data frame 

# In[9]:


# Define a function to generate a dataframe for each divice names, paths and coresponding timestamps

#Example of header and two raws of the generated data frames

###########  timestamp       date       time   file_name                     file_paths
###########  20230302T0900   20230302   0900   jeti1511_20230302T0900.xlsx   \\kfs\tscn-dropbox\rewocap\data\pilot\Pythonte...
###########  20230302T0930   20230302   0930   jeti1511_20230302T0930.xlsx   \\kfs\tscn-dropbox\rewocap\data\pilot\Pythonte...

def generate_dataframe(dir_path, file_name_prefix, file_extension):
    # Create empty lists to store the file names, file paths and timestamps
    file_names = []
    file_paths = []
    dates = []
    times = []
    timestamps = []

    # Walk through the directory tree and search for the files
    for dirpath, dirnames, filenames in os.walk(dir_path):
        for filename in filenames:
            if filename.startswith(file_name_prefix) and filename.endswith(file_extension):
                    file_names.append(filename)
                    file_paths.append(os.path.join(dirpath, filename))
                    extension_len = len(file_extension)
                    timestamp_str = filename[-(extension_len+13):-extension_len]
                    timestamps.append(timestamp_str)
                    date_str = timestamp_str[0:8]
                    time_str = timestamp_str[9:]
                    dates.append(date_str)
                    times.append(time_str)

    # Create a dictionary with the data
    data_dict = {'timestamp': timestamps, 'date': dates, 'time': times, 'file_name': file_names, 'file_paths': file_paths}


    # Create a dataframe from the dictionary
    return pd.DataFrame(data_dict)



# ## WP- Amplitude spectra

# In[10]:


new_key_names = ["L cones", "M cones", "S cones", "Rods", "Melanopsin"]


# In[11]:


# Function to compute the amplitude spectrum
# input: 2D NumPy array

def compute_amplitude_spectrum(image):
    # Get dimensions of the input image
    height, width = image.shape
    # Determine the shorter dimension
    min_dim = min(height, width)

    # Crop the image to a centered square patch
    start_x = (width - min_dim) // 2
    start_y = (height - min_dim) // 2
    cropped_image = image[start_y:start_y + min_dim, start_x:start_x + min_dim]

    # Compute the median of valid values (ignoring NaN and Inf)
    valid_median = np.nanmedian(cropped_image)
    # Compute the maximum value (ignoring NaN and Inf)
    valid_max = np.nanmax(cropped_image[np.isfinite(cropped_image)])
    # Replace NaN with the computed median
    cropped_image = np.where(np.isnan(cropped_image), valid_median, cropped_image)
    # Replace Inf with the computed maximum value
    cropped_image = np.where(np.isinf(cropped_image), valid_max, cropped_image)

    # Perform 2D FFT on the valid part of the image (ignores NaN and Inf values)
    fft_result = fft2(cropped_image)
    fft_result = fftshift(fft_result)  # Shift the zero frequency component to the center
    amplitude_spectrum = np.abs(fft_result)
    return amplitude_spectrum


# In[12]:


# input:amplitude_spectrum , output: radial_frequencies (bin centers) and radial_amplitude (average amplitude per bin)

def radial_frequencies_logarithmically_spaced(amplitude_spectrum, center=None, num_log_bins=100):


    # Create coordinate grids
    y, x = np.indices(amplitude_spectrum.shape)
    if center is None:
        center = (amplitude_spectrum.shape[1] // 2, amplitude_spectrum.shape[0] // 2)

    # Calculate radial distances from the center
    radial_distances = np.sqrt((x - center[0])**2 + (y - center[1])**2)

# Determine logarithmically spaced bins for radial distances
    min_distance = np.min(radial_distances[radial_distances > 0])  # Exclude zero
    max_distance = np.max(radial_distances)
    log_bins = np.logspace(np.log10(min_distance), np.log10(max_distance), num=num_log_bins + 1)

    # Compute radial bins and their average values (exclude zero frequency)
    radial_amplitude, _ = np.histogram(radial_distances,
                                       bins=log_bins,
                                       weights=amplitude_spectrum)

    # Normalize by the number of points in each bin
    counts, _ = np.histogram(radial_distances, bins=log_bins)
    radial_amplitude = radial_amplitude / (counts + 1e-10)  # Avoid division by zero

    # Radial frequencies correspond to bin centers
    radial_frequencies = np.sqrt(log_bins[:-1] * log_bins[1:])

    # Filter out zero or near-zero amplitudes and frequencies above 10^2
    valid_indices = (radial_amplitude > 1e-10) & (radial_frequencies <= 10**2)
    radial_frequencies = radial_frequencies[valid_indices]
    radial_amplitude = radial_amplitude[valid_indices]

    return radial_frequencies, radial_amplitude

