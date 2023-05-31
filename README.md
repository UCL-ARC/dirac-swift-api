# DiRAC-SWIFT API

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![Actions Status][actions-badge]][actions-link]
[![Licence][licence-badge]](./LICENCE.md)

<!--
[![PyPI version][pypi-version]][pypi-link]
[![Conda-Forge][conda-badge]][conda-link]
[![PyPI platforms][pypi-platforms]][pypi-link]
-->

<!-- prettier-ignore-start -->
[actions-badge]:            https://github.com/UCL-ARC/dirac-swift-api/workflows/CI/badge.svg
[actions-link]:             https://github.com/UCL-ARC/dirac-swift-api/actions
[licence-badge]:            https://img.shields.io/badge/License-BSD_3--Clause-blue.svg
<!-- prettier-ignore-end -->

Repository for the REST API side of the DiRAC-SWIFT project

This project is developed in collaboration with the [Centre for Advanced Research Computing](https://ucl.ac.uk/arc), University College London.

## About

### Project Team

Ilektra Christidi ([ilektra.christidi@ucl.ac.uk](mailto:ilektra.christidi@ucl.ac.uk))
Peter Andrews-Briscoe ([p.andrews-briscoe@ucl.ac.uk](mailto:p.andrews-briscoe@ucl.ac.uk))
Harry Moss ([h.moss@ucl.ac.uk](mailto:h.moss@ucl.ac.uk))

<!-- TODO: how do we have an array of collaborators ? -->

### Research Software Engineering Contact

Centre for Advanced Research Computing, University College London
([arc-collab@ucl.ac.uk](mailto:arc-collab@ucl.ac.uk))

## Getting Started

### Prerequisites

- Python 3.11

### Installation

- Clone the repository and `cd` into the repository directory

- Create a virtual environment

```bash
python -m venv env
```

- activate the environment

```bash
source ./env/bin/activate
```

- While in the top-level repository directory (containing this `README.md`)

```bash
pip install ".[dev]"
```

### Running Locally

_TODO_
How to run the application on your local system.

### Running Tests

Tests can be run either via `tox` or directly via `pytest`

```bash
tox run
```

or

```bash
python -m pytest -ra . --cov=src/
```

## Roadmap

- [x] Initial Research <-- You are Here
- [ ] Minimum viable product
- [ ] Alpha Release
- [ ] Feature-Complete Release
