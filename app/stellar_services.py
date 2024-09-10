from decimal import Decimal
from stellar_sdk import Server, TransactionBuilder, Network, Keypair, Asset
import logging

from .models import decrypt_token

logger = logging.getLogger(__name__)

def create_transaction(wallet, destination, amount, asset_code):
    stellar_private_key = decrypt_token(wallet.stellar_private_key)
    keypair = Keypair.from_secret(stellar_private_key)

    server = Server("https://horizon-testnet.stellar.org")
    account = server.load_account(wallet.stellar_public_key)

    transaction = (
        TransactionBuilder(
            source_account=account,
            network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE,
            base_fee=100
        )
        .append_payment_op(destination=destination, amount=str(Decimal(amount)), asset_code=asset_code)
        .set_timeout(30)
        .build()
    )

    transaction.sign(keypair)
    return transaction, server

def submit_transaction(transaction, server):
    try:
        response = server.submit_transaction(transaction)
        return response
    except Exception as e:
        logger.error(f"Transaction submission failed: {str(e)}")
        raise

def stellar_deposit(wallet, amount):
    try:
        transaction, server = create_transaction(wallet, wallet.stellar_public_key, amount, "USDT")
        response = submit_transaction(transaction, server)
        return response
    except Exception as e:
        logger.error(f"Stellar deposit failed for wallet {wallet.id}: {str(e)}")
        raise

def stellar_withdraw(wallet, amount, destination_public_key):
    try:
        transaction, server = create_transaction(wallet, destination_public_key, amount, "USDT")
        response = submit_transaction(transaction, server)
        return response
    except Exception as e:
        logger.error(f"Stellar withdrawal failed for wallet {wallet.id}: {str(e)}")
        raise

def stellar_transfer(wallet, amount, destination_wallet):
    try:
        transaction, server = create_transaction(wallet, destination_wallet.stellar_public_key, amount, "USDT")
        response = submit_transaction(transaction, server)
        return response
    except Exception as e:
        logger.error(f"Stellar transfer failed for wallet {wallet.id} to wallet {destination_wallet.id}: {str(e)}")
        raise

def create_trustline(wallet, asset_code, asset_issuer):
    try:
        stellar_private_key = decrypt_token(wallet.stellar_private_key)
        keypair = Keypair.from_secret(stellar_private_key)

        server = Server("https://horizon-testnet.stellar.org")
        account = server.load_account(wallet.stellar_public_key)

        asset = Asset(asset_code, asset_issuer)

        transaction = (
            TransactionBuilder(
                source_account=account,
                network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE,
                base_fee=100
            )
            .append_change_trust_op(asset=asset)
            .set_timeout(30)
            .build()
        )

        transaction.sign(keypair)
        response = submit_transaction(transaction, server)
        return response
    except Exception as e:
        logger.error(f"Stellar trustline creation failed for wallet {wallet.id}: {str(e)}")
        raise