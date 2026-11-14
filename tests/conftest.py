"""
tests/conftest.py
Pytest session fixtures for Management Cards E2E test suite.
Enables seamless execution under `pytest tests/`.
"""
import pytest
try:
    from tests.test_utils import (
        load_cards_data,
        load_page_map,
        get_chapter2_cards,
        get_chapter2_card_map
    )
except ImportError:
    from test_utils import (
        load_cards_data,
        load_page_map,
        get_chapter2_cards,
        get_chapter2_card_map
    )

@pytest.fixture(scope="session")
def cards_data():
    """Provides cached cards-data.json dictionary."""
    return load_cards_data()

@pytest.fixture(scope="session")
def page_map():
    """Provides cached pdf-page-map.json dictionary."""
    return load_page_map()

@pytest.fixture(scope="session")
def ch2_cards(cards_data):
    """Provides the list of 231 Chapter 02 cards."""
    return get_chapter2_cards(cards_data)

@pytest.fixture(scope="session")
def ch2_card_map(cards_data):
    """Provides O(1) map of Chapter 02 card id -> card dict."""
    return get_chapter2_card_map(cards_data)
