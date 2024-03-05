import launch
import platform

if not launch.is_installed("sqlalchemy"):
    launch.run_pip("install sqlalchemy", "requirements for SearchMyPNG")
