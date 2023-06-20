from lite_tools.logs import logger

try:
    import tls_client
except ImportError:
    logger.warning("没有 tls-client 包,建议手动安装 pip install tls-client")
    exit(0)
else:
    requests = tls_client.Session(
        client_identifier="chrome112",
        random_tls_extension_order=True
    )
