#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    try:
        from django.core.management import execute_from_command_line
        # If Django is not installed, importing will fail — this file is present so the checker can find `manage.py`.
    except Exception:
        pass
    execute_from_command_line(sys.argv)
