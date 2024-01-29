# The GlobalsVar class is used to store global variables.
class GlobalsVar:
    def __init__(self):
        self.gvar = {
            "program_finished": False,
            "sf_config_changed": True,
            'sf_real_time_running': False,
            'has_new_version': False,
        }

    def get(self, key):
        return self.gvar[key]

    def set(self, key, value):
        self.gvar[key] = value
        return True


gvar = GlobalsVar()
