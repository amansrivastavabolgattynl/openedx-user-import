from tutor import hooks

# Plugin configuration
config = {
    "defaults": {
        "BULK_USER_UPLOAD_MAX_FILE_SIZE": 10 * 1024 * 1024,  # 10MB
        "BULK_USER_UPLOAD_MAX_USERS": 1000,
    }
}

# Plugin hooks
hooks.Filters.CONFIG_DEFAULTS.add_items([
    ("BULK_USER_UPLOAD_MAX_FILE_SIZE", config["defaults"]["BULK_USER_UPLOAD_MAX_FILE_SIZE"]),
    ("BULK_USER_UPLOAD_MAX_USERS", config["defaults"]["BULK_USER_UPLOAD_MAX_USERS"]),
])

# Add the app to INSTALLED_APPS
hooks.Filters.ENV_PATCHES.add_items([
    ("openedx-lms-common-settings", "INSTALLED_APPS += ['bulk_user_upload']"),
])
