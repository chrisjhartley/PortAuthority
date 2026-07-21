from lldp_utils import decode_lldp_management_address


def test_ipv4_raw_bytes():
    assert decode_lldp_management_address(b'\xC0\xA8\x01\x01') == '192.168.1.1'


def test_lldp_12_byte_ipv4_structure():
    payload = b'\x00\x04\xC0\xA8\x01\x01\x00\x00\x00\x00\x00\x00'
    assert decode_lldp_management_address(payload) == '192.168.1.1'


def test_lldp_ipv6_structure():
    payload = b'\x00\x10' + bytes.fromhex('20010db8000000000000000000000001')
    assert decode_lldp_management_address(payload) == '2001:db8::1'
