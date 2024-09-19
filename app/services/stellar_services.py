import logging

from stellar_sdk import Server, TransactionBuilder, Network, Keypair, Asset

logger = logging.getLogger(__name__)

STELLAR_SERVER = Server("https://horizon-testnet.stellar.org/")
NETWORK_PASSPHRASE = Network.TESTNET_NETWORK_PASSPHRASE
USDC_ISSUER = "GANCKFGWXAEMJ53GP6VIEHIHRCFO3CIG5ID54WEO7YDR32Y6OG4N2PTU"


def create_transaction(wallet, destination, amount, asset):
    account = STELLAR_SERVER.load_account(wallet.stellar_public_key)
    transaction = (
        TransactionBuilder(
            source_account=account,
            network_passphrase=NETWORK_PASSPHRASE,
            base_fee=STELLAR_SERVER.fetch_base_fee()
        )
        .append_payment_op(destination=destination, amount=str(amount), asset=asset)
        .set_timeout(30)
        .build()
    )
    return transaction


def submit_transaction(transaction, wallet):
    private_key = wallet.decrypt_key(wallet.stellar_private_key)
    keypair = Keypair.from_secret(private_key)
    transaction.sign(keypair)
    response = STELLAR_SERVER.submit_transaction(transaction)
    return response


def stellar_deposit(wallet, amount):
    usdc = Asset("USDC", USDC_ISSUER)
    transaction = create_transaction(wallet, wallet.stellar_public_key, amount, usdc)
    response = submit_transaction(transaction, wallet)
    logger.info(f"Deposit of {amount} USDC completed. Hash: {response['hash']}")
    return response


def stellar_withdraw(wallet, amount, destination):
    usdc = Asset("USDC", USDC_ISSUER)
    transaction = create_transaction(wallet, destination, amount, usdc)
    response = submit_transaction(transaction, wallet)
    logger.info(f"Withdrawal of {amount} USDC to {destination} completed. Hash: {response['hash']}")
    return response


def stellar_transfer(wallet, amount, destination_wallet):
    usdc = Asset("USDC", USDC_ISSUER)
    transaction = create_transaction(wallet, destination_wallet.stellar_public_key, amount, usdc)
    response = submit_transaction(transaction, wallet)
    logger.info(
        f"Transfer of {amount} USDC to {destination_wallet.stellar_public_key} completed. Hash: {response['hash']}")
    return response


def ensure_trustline(wallet):
    account = STELLAR_SERVER.load_account(wallet.stellar_public_key)
    usdc = Asset("USDC", USDC_ISSUER)
    transaction = (
        TransactionBuilder(
            source_account=account,
            network_passphrase=NETWORK_PASSPHRASE,
            base_fee=STELLAR_SERVER.fetch_base_fee()
        )
        .append_change_trust_op(asset=usdc)
        .set_timeout(30)
        .build()
    )
    response = submit_transaction(transaction, wallet)
    logger.info(f"Trustline for USDC established. Hash: {response['hash']}")
    return response
