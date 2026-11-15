import requests
import time
import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

class SMSActivateProvider:
    """
    SMS-Activate.org API wrapper for virtual numbers.
    Requires API key and balance.
    """
    
    BASE_URL = "https://api.sms-activate.org/stubs/handler_api.php"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        
    def get_number(self, service: str = "sw", country: int = 6) -> Optional[Tuple[str, str]]:
        """
        Get virtual number for service.
        country: 6 = India, 0 = Russia, etc.
        Returns: (activation_id, phone_number) or None
        """
        params = {
            'api_key': self.api_key,
            'action': 'getNumber',
            'service': service,
            'country': country
        }
        
        try:
            response = requests.get(self.BASE_URL, params=params, timeout=30)
            if 'ACCESS_NUMBER' in response.text:
                # Format: ACCESS_NUMBER:activation_id:number
                parts = response.text.split(':')
                if len(parts) >= 3:
                    activation_id = parts[1]
                    number = parts[2]
                    logger.info(f"Got number: {number}, activation_id: {activation_id}")
                    return activation_id, number
            elif 'NO_NUMBERS' in response.text:
                logger.error("No numbers available for this country/service")
            elif 'NO_BALANCE' in response.text:
                logger.error("Insufficient balance")
            else:
                logger.error(f"Unexpected response: {response.text}")
        except Exception as e:
            logger.error(f"Error getting number: {e}")
            
        return None
    
    def get_status(self, activation_id: str) -> Optional[str]:
        """
        Check for SMS code.
        Returns: code if received, None if not yet, "CANCEL" if cancelled
        """
        params = {
            'api_key': self.api_key,
            'action': 'getStatus',
            'id': activation_id
        }
        
        try:
            response = requests.get(self.BASE_URL, params=params, timeout=30)
            text = response.text.strip()
            
            if text.startswith('STATUS_OK:'):
                # Format: STATUS_OK:code
                code = text.split(':')[1]
                return code
            elif text == 'STATUS_WAIT_CODE':
                # Still waiting
                return None
            elif text == 'STATUS_CANCEL':
                return "CANCEL"
            else:
                logger.debug(f"Status response: {text}")
                return None
                
        except Exception as e:
            logger.error(f"Error checking status: {e}")
            return None
    
    def cancel_number(self, activation_id: str) -> bool:
        """Cancel number request"""
        params = {
            'api_key': self.api_key,
            'action': 'setStatus',
            'id': activation_id,
            'status': '8'  # Cancel
        }
        
        try:
            response = requests.get(self.BASE_URL, params=params, timeout=30)
            return 'ACCESS_CANCEL' in response.text
        except Exception as e:
            logger.error(f"Error cancelling number: {e}")
            return False
    
    def wait_for_code(self, activation_id: str, timeout: int = 120, interval: int = 5) -> Optional[str]:
        """
        Wait for SMS code with timeout.
        Returns: code or None
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            code = self.get_status(activation_id)
            if code:
                if code == "CANCEL":
                    logger.info("Number cancelled")
                    return None
                return code
            elif code is None:
                # Still waiting
                time.sleep(interval)
            else:
                # Some other status
                time.sleep(interval)
                
        logger.warning(f"Timeout waiting for code after {timeout} seconds")
        return None


class MockSMSProvider:
    """
    Mock provider for testing - generates fake OTP
    """
    
    def __init__(self):
        self.counter = 1000
    
    def get_number(self, service: str = "sw", country: int = 6) -> Optional[Tuple[str, str]]:
        self.counter += 1
        # Generate fake Indian number
        fake_number = f"98765{self.counter % 100000:05d}"
        activation_id = f"mock_{self.counter}"
        return activation_id, fake_number
    
    def get_status(self, activation_id: str) -> Optional[str]:
        # Always return fake OTP after "waiting"
        time.sleep(2)  # Simulate delay
        return "123456"
    
    def wait_for_code(self, activation_id: str, timeout: int = 120, interval: int = 5) -> Optional[str]:
        time.sleep(3)  # Simulate SMS delay
        return "123456"
    
    def cancel_number(self, activation_id: str) -> bool:
        return True