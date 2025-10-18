import pytest
from optimizer.data_parse import extract_A, extract_ED, extract_EE


def test_extract_A_simple_dict():
    sample = {'emp1': {'2025-10-01': {'morning': 'O', 'evening': 'X'}}}
    res = extract_A(sample)
    assert isinstance(res, list)
    # expect one or two rows depending on parsing; availability converted to 1/0
    assert any(r[0] == 'emp1' for r in res)


def test_extract_ED_simple():
    ed_sample = {0: {'emp1': [{'shift': 0, 'willingness': 0.5}], 'emp2': [{'shift': 1, 'willingness': -0.2}]}}
    res = extract_ED(ed_sample)
    assert isinstance(res, list)
    assert any(r[0] == 'emp1' for r in res)


def test_extract_EE_simple():
    ee_sample = {'EMP1': {'EMP2': 0.1}, 'EMP2': {'EMP1': 0.1}}
    res = extract_EE(ee_sample)
    assert isinstance(res, list)
    assert ['EMP1', 'EMP2', 0.1] in res or ['EMP2', 'EMP1', 0.1] in res
