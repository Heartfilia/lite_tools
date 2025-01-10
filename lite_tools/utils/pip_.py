import sys
import subprocess


def install(
        package_name: str, update: bool = False, user: bool = False, quiet: bool = False,
        source: str = "", extra_source: str = "", trust_host: str = "", target: str = "", proxy: str = ""):
    """
    替换 pip.main([])
    update        >>> --upgrade
    user          >>> --user
    quiet         >>> --quiet
    source        >>> --index-url xxxx
    extra_source  >>> --extra-index-url xxxx
    trust_host    >>> --trusted-host xxx
    target        >>> --target xxx
    proxy         >>> --proxy xxx
    """
    exec_args = [sys.executable, '-m', 'pip', 'install', package_name]
    if update:
        exec_args.insert(4, '--upgrade')
    if user:
        exec_args.append("--user")
    if quiet:
        exec_args.append("--quiet")

    if source:
        exec_args.extend(["--index-url", source])
    if extra_source:
        exec_args.extend(["--extra-index-url", extra_source])
    if trust_host:
        exec_args.extend(["--trusted-host", trust_host])
    if target:
        exec_args.extend(["--target", target])
    if proxy:
        exec_args.extend(["--proxy", proxy])

    subprocess.run(exec_args)
