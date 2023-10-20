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

Harry Moss ([h.moss@ucl.ac.uk](mailto:h.moss@ucl.ac.uk))

Peter Andrews-Briscoe ([p.andrews-briscoe@ucl.ac.uk](mailto:p.andrews-briscoe@ucl.ac.uk))

### Research Software Engineering Contact

Centre for Advanced Research Computing, University College London
([arc-collab@ucl.ac.uk](mailto:arc-collab@ucl.ac.uk))

## Getting Started

### Prerequisites

- Python 3.10 or newer

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
pip install "./api[dev,test]"
```

## Running the API

### Getting authenticated

The API can be accessed after JWT authentication. After submitting your username and password, a token will be generated, which will be attached to a header in all your requests. The token will have a lifespan of an hour, after which you'll need to generate a new token by signing in again.

### Running locally

After installing the package, from the root directory (containing this README), run in development mode with

```bash
python src/api/main.py
```

which will launch a [uvicorn](https://www.uvicorn.org/) server on `127.0.0.1`/`localhost` on the default port `8000`.

Alternatively, in the same directory the app can be equivalently launched with

```bash
uvicorn api.main:app --reload
```

By default, the API will be served on `localhost:8000`, with OpenAPI documentation available at `localhost:8000/docs`

### Deploying the API

When deploying the API for use in production, it's recommended to use [Gunicorn](https://docs.gunicorn.org/en/stable/index.html) to serve the FastAPI application and act as a process manager. Gunicorn can start one or more uvicorn worker processes, listening on the port indicated on startup. Request and response handling is taken care of by individual workers.

Gunicorn will restart failing workers, but care should be taken to deal with cases where the Gunicorn process itself is killed.
It's important to note that Gunicorn does not provide load balancing capability, but relies on the operating system to perform that role.

The documentation recommends `(2 x $num_cores) + 1` workers, although depending on your deployment environment this may not be suitable.

As an example, to start this application under Gunicorn on a `localhost` port with your choice of workers:

```bash
gunicorn src.api.main:app --workers ${n_workers} --worker-class uvicorn.workers.UvicornWorker --bind localhost:${port}
```

## For developers

### Running Tests

Tests can be run either via `tox` or directly via `pytest` from the top level directory of the repository

```bash
tox run
```

or

```bash
python -m pytest -ra . --cov=src/api
```

either of which will run all tests and generate a coverage report.

## Contributing

To contribute to the project as a developer, use the following as a guide. These are based on ARC Collaborations [group practices](https://github.com/UCL-ARC/research-software-documentation/blob/main/processes/programming_projects/group_practices.md) and [code review documentation](https://github.com/UCL-ARC/research-software-documentation/blob/main/processes/programming_projects/review.md).

### Python standards we follow

To make explicit some of the potentially implicit:

- We will target Python versions `>= 3.10`
- We will use [ruff](https://beta.ruff.rs/docs/) for linting and [black](https://github.com/psf/black) for code formatting to standardise code, improve legibility and speed up code reviews
- Function arguments and return types will be annotated, with type checking via [mypy](https://mypy.readthedocs.io/en/stable/)
- We will use [docstrings](https://peps.python.org/pep-0257/) to annotate classes, class methods and functions
  - If you use Visual Studio Code, [autoDocstring](https://marketplace.visualstudio.com/items?itemName=njpwerner.autodocstring) is recommended to speed this along.

### General GitHub workflow

- Create a branch for each new piece of work with a suitable descriptive name, such as `feature-newgui` or `adding-scaffold`
- Do all work on this branch
- Open a new PR for that branch to contain discussion about your changes
  - Do this **early** and set as a 'Draft PR' (on GitHub) until you are ready to merge to make your work visible to other developers
- Make sure the repository has CI configured so tests (ideally both of the branch, and of the PR when merged) are run on every push.
- If you need advice, mention @reviewer and ask questions in a PR comment.
- When ready for merge, request a review from the "Reviewer" menu on the PR.
- All work must go through a pull-request review before reaching `main`
  - **Never** commit or push directly to `main`

The `main` branch is for ready-to-deploy release quality code

- Any team member can review (but not the PR author)
  - try to cycle this around so that everyone becomes familiar with the code
- Try to cycle reviewers around the project's team: so that all members get familiar with all work.
- Once a reviewer approves your PR, **you** can hit the merge button
- Default to a 'Squash Merge', adding your changes to the main branch as a single commit that can be easily rolled back if need be

### Reviewing code

[The Turing Way](https://the-turing-way.netlify.app/index.html) provides an overview of best practices - it comes as recommended reading and includes some [possible workflows for code review](https://the-turing-way.netlify.app/reproducible-research/reviewing/reviewing-checklist.html?highlight=code%20review) - great if you're unsure what you're typically looking for during a code review.

## Project Roadmap

- [x] Initial Research
- [x] Minimum viable product  <-- You are Here
- [ ] Alpha Release
- [ ] Feature-Complete Release
