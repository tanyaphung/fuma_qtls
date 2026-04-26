#!/bin/bash

snakemake -s process_gtexv10.smk -j1 --configfile config.json --rerun-incomplete --config chromosome="1"

# then repeat for all chromosomes.

