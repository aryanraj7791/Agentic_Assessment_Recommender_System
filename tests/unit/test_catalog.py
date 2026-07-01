import pytest

from app.catalog.loader import Catalog
from app.catalog.preprocessor import load_catalog_dataframe, load_catalog_from_dataframe


@pytest.fixture(scope="session")
def catalog():
    df = load_catalog_dataframe("data/shl_product_catalog.json")
    return load_catalog_from_dataframe(df)


def test_catalog_loads(catalog):
    assert len(catalog) > 100


def test_opq32r_exists(catalog):
    item = catalog.get_by_name("Occupational Personality Questionnaire OPQ32r")
    assert item is not None
    assert item.test_type == "P"
    assert item.url.startswith("https://www.shl.com/")


def test_dataframe_preprocessing_removes_invalid_rows():
    df = load_catalog_dataframe("data/shl_product_catalog.json")
    assert df["entity_id"].is_unique
    assert (df["name"].str.len() > 0).all()
