import pytest
from fact_checker import perform_fact_checking_task, classify_result
from typing import Any

def test_perform_fact_checking_task(text: str) -> None:
    result = perform_fact_checking_task('This is a true statement.')
    assert result == 'accurate'

    result = perform_fact_checking_task('This is a false statement.')
    assert result == 'false'

def test_classify_result(result: str) -> None:
    classification = classify_result('accurate')
    assert classification == 'accurate'

    classification = classify_result('inaccurate')
    assert classification == 'inaccurate'

    classification = classify_result('false')
    assert classification == 'false'

    classification = classify_result('unknown')
    assert classification == 'indeterminate'
