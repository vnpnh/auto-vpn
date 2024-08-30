class VPNError(Exception):
    """Custom exception class to handle VPN-specific errors."""
    def __init__(self, message: str):
        super().__init__(message)
