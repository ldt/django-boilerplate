from decouple import config

environment = config("ENVIRONMENT", default="development")

if environment == "production":
    from .production import *  # noqa: F403
elif environment == "development":
    from .development import *  # noqa: F403
else:
    from .development import *  # noqa: F403
