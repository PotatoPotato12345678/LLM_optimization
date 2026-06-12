"""Importable Pyomo optimization engine for shift scheduling.

This package is the refactor of the former standalone scripts
``optimizer/model_def.py`` and ``optimizer/solver.py`` into a callable engine
that the Django backend can invoke directly (see ``engine.solve``).
"""

from .engine import solve  # noqa: F401
