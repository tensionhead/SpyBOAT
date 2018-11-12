# Small pipeline to Wavelet transform Image Intensity Stacks

## Getting Started

To run locally: 

1. create a conda environment:
    
    ``conda env create -f environment.yml``
    
2. Run the example from `src`:

    ```bash
    cd src
    bash run_local.sh
    ```

## Available scripts:

- example configuration in ```/src/slurm_bash_template.sh```, this runs both from the shell and via slurm
- the script in ```/src/ana_movie.py``` accepts command line parameters managing I/O and the analysis parameters
- actual algorithms are in ```/src/wavelet_ana_lib.py```
