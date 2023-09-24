from tests.module_helper import PyttmanInternalBaseTestCase
from pyttman.core.internals import Settings

from importlib import import_module
from . import mocksettings

import pytest

@pytest.fixture
def mockSettings():
    settings_names = [i for i in dir(mocksettings)
                if not i.startswith("_")]
    settings_config = {name: getattr(mocksettings, name)
                for name in settings_names}

    return Settings(**settings_config)

def test_read_settings_with_dictionary(mockSettings):
    settings = mockSettings
    
    assert settings.d.k2.a == "a"
    assert settings.d["k2"].a == "a"
    assert settings.d["k2"]["a"] == "a"

    assert settings.d.k1 == "v1"
    assert settings.d["k1"] == "v1"

    assert settings.foo == "bar"
        
