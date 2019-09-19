# Makefile for reproducible (?) analysis and easier cron scheduling

SHELL=/bin/bash
CONDAROOT = /home/tushar/miniconda3

collect:
	source $(CONDAROOT)/bin/activate scooter && python collect.py

test:
	echo 'uh oh this has no tests yet'
