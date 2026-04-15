# Photoreceptor-specific scene statistics analysis

## 1. Overview

This  Python code repository contains code, processed data, and output materials for the spatial analysis conducted in the SCENES project.

If you have any comments or queries, please reach out to us at [Niloufar Tabandeh](mailto:niloufar.tabandehsaravi@tum.de) and [Manuel Spitschan](mailto:manuel.spitschan@tum.de).

The repository is designed to be reproducible across systems. All internal paths are relative, while large external datasets stored in EDMOND general data repository [SCENES derivatives](https://doi.org/10.17617/3.NX2H2U). 


---

## 2. Repository Structure

```
SCENES/
├── code/
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── scenes_function.py
│   │   └── scenes_function.ipynb
│   ├── SCENES_spatial_analysis_paper.ipynb
│   └── WP_derivatives.ipynb
├── data/
│   ├── jeti_metadata_summary_tidy_scenes.csv
├── results/
│   ├── figures/
│   │   ├── Figure1.pdf
│   │   ├── Figure2.pdf
│   │   └── ...
│   ├── tables/
│   │   ├── overexposed_percentage_per_view.csv
│   │   ├── wp_statistics_per_view.csv
│   │   └── ...
├── .gitignore
├── LICENSE.md
├── README.md
└── environment.yml
```

### Description

- `code/`: Main analysis notebooks and utility functions  
- `code/utils/`: Reusable functions for analysis  
- `data/`: Small\local dataset to integrate metadata and spectral metrics
- `results/`: Output directory for figures and tables  
- `environment.yml`: Conda virtual environment specification  

---

## 3. Environment Setup

Create the environment using:

```
conda env create -f environment.yml
conda activate spatialstatistics_env
```

---

## 4. Data preparation

Due to the large size of the derivatives dataset, it is deposited in an open data repository [SCENES derivatives](https://doi.org/10.17617/3.NX2H2U). The following steps must be completed before running the code.

1. Navigate to the data repository and download all `wp_derivative..` archive parts. Extract all parts into a single folder so that the contents are reconstructed correctly.

2. Download the metadata file and place it in `metadata` folder.

3. Organize the files according to the following data tree structure:
```
dataset_dir/
├── derivatives/
│   └── wp_derivatives/
│       ├── wp690_YYYYMMDDTHHMM.npz
│       └── ...
└── data/
    └── jeti_metadata_summary_tidy_scenes.csv
```
4. Open `WP_derivatives.ipynb` and update the `dataset_dir` variable to point to the root directory of the organized dataset.

```
dataset_dir = "path/to/your/dataset"
```

Each `.npz` file contains multiple 2D NumPy arrays (lcone', 'mcone', 'scone', 'rhodopic', 'iprgc', 'luminance', 'trix', 'triz', 'stdred', 'stdgreen', 'stdblue').

---

## 5. Path Handling

- Internal paths use relative references (`../data`, `../results`)
- External dataset uses a user-defined absolute path

Example:

```
import os

data_dir = os.path.join("..", "data")
results_dir = os.path.join("..", "results")
```

---

## 6. Workflow

### 6.1 WP_derivatives.ipynb

- Input: External dataset (`wp_derivatives`)
- Processes `.npz` files
- calculate average radiance, average luminance, RMS contrast and ampilitude spectra for all α-opic radiance maps
- Generates intermediate aggrigated tabular data to use in the main notebook to generate figures and tables for the paper.

### 6.2 SCENES_spatial_analysis_paper.ipynb

- Main analysis notebook
- Produces figures and tables for the paper.
- Saves outputs in `results/`

---

## 7. Outputs

Generated outputs are saved in:

- `results/figures/`
    All final Figure1 to 7 in .png and .pdf formats stored here. In addition, the supplemantary `Figure_sup` is also stored here.

- `results/tables/`:
    central statistics for spectral data : `jeti_statistics_overall.csv`, `jeti_statistics_per_view.csv`
    central statistics for radiance maps: `wp_statistics_overall.csv`, `wp_statistics_per_view.csv`
    overexposed pixels of radiance maps: `overexposed_percentage_per_view.csv`
    derived metrics of radiance maps: `merged_wp_jeti_metadata_df.csv`
    amplitude spectra per view: `amplitude_spectra_regression_view_df.csv`

---

## 8. Reproducibility Notes

- Users must update `dataset_dir`
- Folder structure must remain unchanged
- Code uses OS-independent path handling (`os.path`)
- Jupyter outputs may change but do not affect results

---

## 9. License

This project is licensed under the MIT License. See the [LICENSE.md](LICENSE.md) file for details.

---


