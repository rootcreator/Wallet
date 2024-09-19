from typing import Optional, List, Dict
from django.conf import settings
from pymono import Mono
import logging

logger = logging.getLogger(__name__)

# Initialize the Mono client with your secret key from settings
MONO_SEC_KEY = getattr(settings, 'MONO_SEC_KEY', None)

if not MONO_SEC_KEY:
    logger.error("The MONO_SEC_KEY setting is not defined or is empty")
    mono = None
else:
    try:
        mono = Mono(MONO_SEC_KEY)
    except Exception as e:
        logger.error(f"Error initializing Mono client: {e}")
        mono = None


def authenticate(mono_code):
    """
    Authenticate with Mono using the provided mono_code.
    """
    if not mono:
        logger.error("Mono client is not initialized")
        return None, None
    try:
        data, status = mono.Auth(mono_code)
        return data, status
    except Exception as e:
        logger.error(f"Error during authentication: {e}")
        return None, None


def set_user_id(user_id):
    """
    Set the user ID for the Mono client.
    """
    try:
        mono.SetUserId(user_id)
    except Exception as e:
        print(f"Error setting user ID: {e}")


def get_account():
    """
    Get the user account details.
    """
    try:
        account = mono.getAccount()
        return account
    except Exception as e:
        logger.error(f"Error fetching account details: {e}")
        return None


def get_transactions(start: str = '', end: str = '', narration: str = '', types: str = '', paginate: str = 'false') -> Optional[List[Dict]]:
    """
    Get transactions with optional filters.
    """
    try:
        transactions = mono.getTransactions(start=start, end=end, narration=narration, types=types, paginate=paginate)
        return transactions
    except Exception as e:
        print(f"Error fetching transactions: {e}")
        return None


def get_statement(month='', output='json'):
    """
    Get account statement.
    """
    try:
        statement = mono.getStatement(month, output)
        return statement
    except Exception as e:
        print(f"Error fetching statement: {e}")
        return None


def get_credits():
    """
    Get credits details.
    """
    try:
        credits = mono.getCredits()
        return credits
    except Exception as e:
        print(f"Error fetching credits: {e}")
        return None


def get_debits():
    """
    Get debits details.
    """
    try:
        debits = mono.getDebits()
        return debits
    except Exception as e:
        print(f"Error fetching debits: {e}")
        return None


def get_identity():
    """
    Get identity details.
    """
    try:
        identity = mono.getIdentity()
        return identity
    except Exception as e:
        print(f"Error fetching identity: {e}")
        return None


def bvn_lookup(bvn):
    """
    Perform BVN lookup.
    """
    try:
        result = mono.bvn_lookup(bvn)
        return result
    except Exception as e:
        print(f"Error during BVN lookup: {e}")
        return None
