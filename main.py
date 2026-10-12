"""Convenience runner for the KQMS Django project."""
import os
import sys

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
    try:
        from django.core.management import execute_from_command_line
        from django.core.management.commands.runserver import Command as runserver
        runserver.default_port = '9000'
        # Run development server on port 9000
        execute_from_command_line(['manage.py', 'runserver', '127.0.0.1:9000'])
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Make sure your virtual environment (.venv) is activated."
        ) from exc
