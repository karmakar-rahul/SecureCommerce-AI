"""
Validation helper functions.
"""
import ipaddress

def validate_ip(ip: str) -> bool:
    """
    Returns True if IP is valid.
    """
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

def validate_coordinates(latitude: float, longitude: float) -> bool:
    """
    Validate latitude and longitude.
    """
    return (
        -90 <= latitude <= 90
        and
        -180 <= longitude <= 180
    )

def validate_failed_attempts(value: int) -> bool:
    return value >= 0

def validate_response_time(value: float) -> bool:
    return value >= 0