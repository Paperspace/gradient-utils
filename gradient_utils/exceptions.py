class ConfigError(Exception):
    def __init__(self, component, message):
        self.component = component
        self.message = message

    def __str__(self):
        return "For component - %s - received error message: %s" % (self.component, self.message)
