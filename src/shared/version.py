"""Version management and consistency tracking."""

APP_VERSION = "1.0.0"
PROTOCOL_VERSION = "3.0.0"
SCHEMA_VERSION = "1.2"

def get_version_info():
    return {
        "app_version": APP_VERSION,
        "protocol_version": PROTOCOL_VERSION,
        "schema_version": SCHEMA_VERSION,
    }
