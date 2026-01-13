#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

def main():
    """Run administrative tasks."""
    # Attempt to load environment variables from .env
    try:
        from dotenv import load_dotenv
        import pathlib
        
        # 1. Try local .env
        load_dotenv()
        
        # 2. Try sibling backend .env (specific to this project structure)
        backend_env = pathlib.Path(__file__).resolve().parent.parent / 'backend_fastapi' / '.env'
        if backend_env.exists():
            print(f"Loading env from {backend_env}")
            load_dotenv(backend_env)
            
    except ImportError:
        pass

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chatbot_project.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
