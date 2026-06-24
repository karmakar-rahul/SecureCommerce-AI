from enum import Enum


class LoginStatus(str, Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class AttackType(str, Enum):
    NORMAL = "NORMAL"
    BRUTE_FORCE = "BRUTE_FORCE"
    CREDENTIAL_STUFFING = "CREDENTIAL_STUFFING"


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class DeviceType(str, Enum):
    WINDOWS = "Windows"
    LINUX = "Linux"
    MACOS = "macOS"
    ANDROID = "Android"
    IOS = "iOS"


class BrowserType(str, Enum):
    CHROME = "Chrome"
    FIREFOX = "Firefox"
    EDGE = "Edge"
    SAFARI = "Safari"


class UserRole(str, Enum):
    CUSTOMER = "Customer"
    ADMIN = "Admin"