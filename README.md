# CIPRS Reader

Setup:

```bash
pyenv virtualenv 3.7.2 pdf-template
pyenv shell pdf-template
pip install -r requirements.txt
pip install -e .
```

Read CIPRS PDF:

```
python ciprs_reader.py ignore/cypress-example.PDF
```

Run Jupyter:

```bash
jupyter-lab
```

Run tests:

```bash
pytest --pylint
```

Code for Durham
