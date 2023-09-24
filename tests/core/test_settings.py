from tests.module_helper import PyttmanInternalBaseTestCase
from pyttman.core.internals import Settings

from importlib import import_module
import pytest

@pytest.fixture
def mockSettings():
    
    mock_settings = {
        "d":{
            "k1":"v1",
            "k2":{
                "a":"a",
                "b":"b"
            }
        },
        "foo":"bar"
    }

    return Settings(**mock_settings)

def test_read_settings_with_dictionary(mockSettings):
    assert mockSettings.d.k2.a == "a"
    assert mockSettings.d["k2"].a == "a"
    assert mockSettings.d["k2"]["a"] == "a"

    assert mockSettings.d.k1 == "v1"
    assert mockSettings.d["k1"] == "v1"

    assert mockSettings.foo == "bar"
        
