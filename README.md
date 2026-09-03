# Capsuli

[![Documentation](https://readthedocs.org/projects/capsuli/badge/?version=latest)](https://capsuli.readthedocs.io/en/latest/?badge=latest) [![CI](https://github.com/NaturalHPC/capsuli/actions/workflows/test.yml/badge.svg)](https://github.com/NaturalHPC/capsuli/actions/workflows/test.yml) [![CFF](https://github.com/NaturalHPC/capsuli/actions/workflows/cffconvert.yml/badge.svg)](https://github.com/NaturalHPC/capsuli/actions/workflows/cffconvert.yml)

Capsuli is the Cluster Allocation Process SUpervision LIbrary. It scans available
compute resources and returns a description of them, then lets you select a subset and
start a program on that subset. Programs can be single- or multithreaded, or MPI
parallel. Processes are monitored, output can be redirected, and exit status is
recorded. Works locally and inside a Slurm allocation

See the [Capsuli documentation](https://capsuli.readthedocs.io/en/latest) to get
started.

## Legal

Capsuli is Copyright 2018-2026 Netherlands eScience Center, University of Amsterdam,
Utrecht University.

Licensed under the Apache License 2.0. See LICENSE for the terms.

