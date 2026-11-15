import re
import requests
import random
import string
import logging
from typing import Dict, Any, Optional, Tuple
from fake_useragent import UserAgent

logger = logging.getLogger(__name__)

class SwiggyAccountCreator:
    """
    Automatically creates Swiggy accounts using virtual numbers.
    """
    
    def __init__(self, sms_provider):
        self.sms = sms_provider
        self.session = requests.Session()
        self.ua = UserAgent()
        
        # Endpoints (may need updating)
        self.base_url = "https://www.swiggy.com"
        self.csrf_pattern = r"window._csrfToken = \"(.+?)\";"
        
        # Sign-up endpoints
        self.signup_otp_url = f"{self.base_url}/dapi/auth/signup-otp"
        self.signup_verify_url = f"{self.base_url}/dapi/auth/signup-verify"
        self.complete_signup_url = f"{self.base_url}/dapi/auth/complete-signup"
        
    def _get_csrf_token(self) -> Optional[str]:
        """Extract CSRF token from Swiggy homepage"""
        headers = {
            'User-Agent': self.ua.random
        }
        
        try:
            response = self.session.get(self.base_url, headers=headers, timeout=30)
            match = re.search(self.csrf_pattern, response.text)
            if match:
                return match.group(1)
            else:
                logger.error("CSRF token not found in response")
                return None
        except Exception as e:
            logger.error(f"Error getting CSRF token: {e}")
            return None
    
    def _generate_email(self, phone: str) -> str:
        """Generate random email based on phone"""
        random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return f"swiggy{phone}@{random_str}.com"
    
    def _generate_name(self) -> str:
        """Generate random Indian name"""
        first_names = ["Aarav", "Vihaan", "Aditya", "Vivaan", "Arjun", "Sai", "Reyansh", "Anaya", "Diya", "Aarohi"]
        last_names = ["Sharma", "Verma", "Patel", "Kumar", "Singh", "Reddy", "Nair", "Menon", "Pillai", "Mehta"]
        return f"{random.choice(first_names)} {random.choice(last_names)}"
    
    def _generate_password(self) -> str:
        """Generate random password"""
        chars = string.ascii_letters + string.digits + "!@#$%"
        return ''.join(random.choices(chars, k=12))
    
    def _make_request(self, url: str, payload: Dict[str, Any], use_csrf: bool = True) -> Optional[Dict[str, Any]]:
        """Make API request with proper headers"""
        headers = {
            'User-Agent': self.ua.random,
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/plain, */*',
            'Origin': self.base_url,
            'Referer': f'{self.base_url}/'
        }
        
        if use_csrf:
            csrf = self._get_csrf_token()
            if not csrf:
                return None
            payload['_csrf'] = csrf
        
        try:
            response = self.session.post(url, json=payload, headers=headers, timeout=30)
            logger.debug(f"Response status: {response.status_code}")
            logger.debug(f"Response text: {response.text[:200]}")
            
            if response.status_code == 200:
                try:
                    return response.json()
                except:
                    return {"raw": response.text}
            else:
                logger.error(f"Request failed with status {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Request error: {e}")
            return None
    
    def create_account(self) -> Optional[Dict[str, str]]:
        """
        Create a new Swiggy account.
        Returns: dict with account details or None
        """
        logger.info("Starting account creation process...")
        
        # Step 1: Get virtual number
        logger.info("Requesting virtual number...")
        number_info = self.sms.get_number(service="sw", country=6)  # India
        if not number_info:
            logger.error("Failed to get virtual number")
            return None
            
        activation_id, phone_number = number_info
        logger.info(f"Got number: {phone_number}")
        
        # Step 2: Request OTP for sign-up
        logger.info("Requesting OTP for sign-up...")
        otp_payload = {
            "mobile": phone_number
        }
        
        otp_response = self._make_request(self.signup_otp_url, otp_payload)
        if not otp_response:
            logger.error("Failed to request OTP")
            self.sms.cancel_number(activation_id)
            return None
        
        # Step 3: Wait for and get OTP
        logger.info("Waiting for OTP...")
        otp_code = self.sms.wait_for_code(activation_id, timeout=120)
        if not otp_code:
            logger.error("Failed to get OTP")
            self.sms.cancel_number(activation_id)
            return None
            
        logger.info(f"Got OTP: {otp_code}")
        
        # Step 4: Verify OTP
        logger.info("Verifying OTP...")
        verify_payload = {
            "otp": otp_code
        }
        
        verify_response = self._make_request(self.signup_verify_url, verify_payload)
        if not verify_response:
            logger.error("Failed to verify OTP")
            return None
            
        # Step 5: Generate account details
        name = self._generate_name()
        email = self._generate_email(phone_number)
        password = self._generate_password()
        
        # Step 6: Complete sign-up
        logger.info("Completing sign-up...")
        complete_payload = {
            "name": name,
            "email": email,
            "password": password
        }
        
        complete_response = self._make_request(self.complete_signup_url, complete_payload)
        if not complete_response:
            logger.error("Failed to complete sign-up")
            return None
        
        # Check if sign-up was successful
        if complete_response.get("statusCode") == 0:
            logger.info("Account created successfully!")
            
            account_details = {
                "phone": phone_number,
                "email": email,
                "password": password,
                "name": name,
                "activation_id": activation_id,
                "status": "active"
            }
            
            return account_details
        else:
            error_msg = complete_response.get("statusMessage", "Unknown error")
            logger.error(f"Sign-up failed: {error_msg}")
            return None
    
    def create_multiple_accounts(self, count: int = 1) -> list:
        """Create multiple accounts"""
        accounts = []
        
        for i in range(count):
            logger.info(f"Creating account {i+1}/{count}...")
            account = self.create_account()
            if account:
                accounts.append(account)
                logger.info(f"Account {i+1} created successfully")
            else:
                logger.error(f"Failed to create account {i+1}")
            
            # Small delay between creations
            if i < count - 1:
                import time
                time.sleep(5)
        
        return accounts