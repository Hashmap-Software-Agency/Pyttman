from tests.module_helper import PyttmanInternalBaseTestCase
from pyttman.core.internals import Settings

from importlib import import_module
from . import mocksettings

class PyttmanInternalSettingsPyttmanApp(PyttmanInternalBaseTestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        settings_names = [i for i in dir(mocksettings)
                    if not i.startswith("_")]
        settings_config = {name: getattr(mocksettings, name)
                    for name in settings_names}
        self.settings = Settings(**settings_config)        

    def test_read_settings_with_dictionary(self):
        
        self.assertTrue(self.settings.d.k2.a == "a")
        self.assertTrue(self.settings.d["k2"].a == "a")
        self.assertTrue(self.settings.d["k2"]["a"] == "a")
        
        self.assertTrue(self.settings.d.k1 == "v1")
        self.assertTrue(self.settings.d["k1"] == "v1")

        self.assertTrue(self.settings.foo == "bar")
        
