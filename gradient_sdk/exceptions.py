class ConfigError(Exception):
    def __init__(self, component, message):
        self.component = component
        self.message = message

    def __str__(self):
        return f"""
        Component: {self.component}
        Error message: {self.message}
        """
