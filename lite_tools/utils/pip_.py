import sys
import subprocess


def install(package_name: str, update: bool = False, source: str = ""):
    """
    替换 pip.main([])
    """
    exec_args = [sys.executable, '-m', 'pip', 'install', package_name]
    if update:
        exec_args.insert(4, '--upgrade')

    if source:
        exec_args.extend(["-i", source])

    subprocess.check_call(exec_args)
