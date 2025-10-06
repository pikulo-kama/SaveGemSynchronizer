from savegem.common.core.editable_json_config_holder import EditableJsonConfigHolder


class MockJsonConfigHolder(EditableJsonConfigHolder):
    """Mock for JsonConfigHolder to control config values."""

    def __init__(self, config_values):  # noqa
        self._config_values = config_values

    def get_value(self, property_name, default_value=None):
        return self._config_values.get(property_name, default_value)

    def set_value(self, property_name: str, value: any):
        self._config_values[property_name] = value
