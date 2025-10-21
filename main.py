# %%
# %%
"""
================================================================================
Master Thesis Code
--------------------------------------------------------------------------------
Title:  Elastic Net–based indicator selection for nowcasting German GDP:
        Evidence from Unrestricted MIDAS models
Author: Johannes Schäfer
================================================================================

Setup
-----
1) Install/Update the Conda environment from 'conda_env.yml' (env name: DataAnalysis):
       conda env create -f conda_env.yml
   or, if it already exists:
       conda env update -n DataAnalysis -f conda_env.yml --prune
   then:
       conda activate DataAnalysis

Quick start
-----------
2) Set the path to your /Code folder:
       FILE_PATH = "/Code/"

3) Go into the 'scripts' directory.

4) In the scripts folder, run the files in this order,
   RESTARTING THE KERNEL AFTER EACH RUN:

       01_compute_cache.py
       02_run_nps.py
       all files starting with 03_
       04_run_results              --> creates baseline outputs

5) Find baseline results (tables & plots) in:
       output/results/MA/

6) For the simulation in the indicator selection chapter, run:
       simulations/simpaths.py     --> runs the full simulation study
       (for both l1_ratio = 0.2 and 0.8)

Further results (optional; very time-consuming)
-----------------------------------------------
Run all scripts starting with 05_, then:
       06_run_results_nl_c         --> uses monthly indicator block lags
                                       in the selection matrix

Explore / custom specs
----------------------
• Use `main_mlu` to run your own specifications.
• Outputs are written to:
      output/mlumidas/
"""
# Path to the /Code folder
FILE_PATH = ""

