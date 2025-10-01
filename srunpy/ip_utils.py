import socket
from typing import List


def get_local_ipv4_addresses(include_loopback: bool = False) -> List[str]:
    """Return a sorted list of IPv4 addresses assigned to the local machine."""
    candidates = set()

    def _add(addr: str) -> None:
        if not addr:
            return
        if not include_loopback and addr.startswith("127."):
            return
        candidates.add(addr)

    try:
        hostname = socket.gethostname()
        host_info = socket.gethostbyname_ex(hostname)
        for addr in host_info[2]:
            _add(addr)
    except socket.gaierror:
        pass

    try:
        for info in socket.getaddrinfo(socket.gethostname(), None, family=socket.AF_INET):
            _add(info[4][0])
    except socket.gaierror:
        pass

    try:
        for info in socket.getaddrinfo(None, 0, family=socket.AF_INET, type=socket.SOCK_DGRAM):
            _add(info[4][0])
    except socket.gaierror:
        pass

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("198.51.100.1", 80))
            _add(s.getsockname()[0])
    except OSError:
        pass

    return sorted(candidates)
