"""Standalone entry point for the Windows desktop inspector.

Keep package imports inside multistomp_lab.desktop resolvable under PyInstaller.
"""
from multistomp_lab.desktop import main

if __name__ == "__main__":
    main()
