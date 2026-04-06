import pytest

from src.base_api import BaseAPI
from src.base_storage import BaseStorage


def test_base_api_cannot_be_instantiated():
    with pytest.raises(TypeError):
        BaseAPI()


def test_base_storage_cannot_be_instantiated():
    with pytest.raises(TypeError):
        BaseStorage()
