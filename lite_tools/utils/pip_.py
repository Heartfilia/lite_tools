import sys
import subprocess


def install(package_name: str, update: bool = False, source: str = "", extra_source: str = "", trust_host: str = ""):
    """
    替换 pip.main([])
    update        >>> --upgrade
    source        >>> --index-url xxxx
    extra_source  >>> --extra-index-url xxxx
    trust_host    >>> --trusted-host xxx
    """
    exec_args = [sys.executable, '-m', 'pip', 'install', package_name]
    if update:
        exec_args.insert(4, '--upgrade')

    if source:
        exec_args.extend(["--index-url", source])
    if extra_source:
        exec_args.extend(["--extra-index-url", extra_source])
    if trust_host:
        exec_args.extend(["--trusted-host", trust_host])

    subprocess.run(exec_args)
