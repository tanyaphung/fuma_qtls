#!/bin/bash
eval "$(conda shell.bash hook)"
conda activate base

snakemake -s process.smk -j8 --configfile config.json --rerun-incomplete


