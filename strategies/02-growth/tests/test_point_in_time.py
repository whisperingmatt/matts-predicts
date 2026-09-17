"""Spec section 10 — point-in-time join guard.

To be written in S3 before any feature is computed: for a known ticker and
decision date, assert the SF1 row used has datekey <= decision date.
Placeholder so the test directory exists; it is skipped, not passing.
"""
import pytest


@pytest.mark.skip(reason="S3 — written before features.py computes anything")
def test_feature_uses_filing_on_or_before_decision_date():
    raise AssertionError("not implemented")
