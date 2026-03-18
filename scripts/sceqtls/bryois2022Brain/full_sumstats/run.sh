#!/bin/bash

eval "$(conda shell.bash hook)"
conda activate base

snakemake -s format_full_sumstat.smk -j10 --configfile config.json --rerun-incomplete


