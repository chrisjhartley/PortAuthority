import socket


def decode_lldp_management_address(raw_address):
    """Decode an LLDP management address from either raw IPv4/IPv6 bytes or the
    LLDP structure used for those addresses.

    The LLDP management address encoding is:
    - 1 byte: address subtype
    - 1 byte: address length
    - N bytes: address bytes
    - 1 byte: interface subtype
    - 4 bytes: interface number
    - 1 byte: OID length

    For IPv4, that becomes a 12-byte structure with a 4-byte address payload.
    For IPv6, it becomes a 16-byte structure with a 16-byte address payload.
    """
    if raw_address is None:
        return None

    if isinstance(raw_address, memoryview):
        raw_address = raw_address.tobytes()

    if isinstance(raw_address, str):
        return raw_address

    if not isinstance(raw_address, (bytes, bytearray)):
        return None

    raw = bytes(raw_address)

    if len(raw) == 4:
        try:
            return socket.inet_ntoa(raw)
        except OSError:
            return None

    if len(raw) == 16:
        try:
            return socket.inet_ntop(socket.AF_INET6, raw)
        except OSError:
            return None

    if len(raw) >= 2:
        address_length = raw[1]
        if len(raw) >= 2 + address_length:
            address_bytes = raw[2:2 + address_length]
            if len(address_bytes) == 4:
                try:
                    return socket.inet_ntoa(address_bytes)
                except OSError:
                    pass
            if len(address_bytes) == 16:
                try:
                    return socket.inet_ntop(socket.AF_INET6, address_bytes)
                except OSError:
                    pass

    return None
