from decimal import Decimal

from stellar_sdk import Server, TransactionBuilder, Network, Keypair, Asset

from .models import decrypt_token


def stellar_deposit(wallet, amount):
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
        .append_payment_op(destination=wallet.stellar_public_key, amount=str(Decimal(amount)), asset_code="USDT")
        .set_timeout(30)
        .build()
    )

    transaction.sign(keypair)
    response = server.submit_transaction(transaction)
    return response


def stellar_withdraw(wallet, amount, destination_public_key):
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
        .append_payment_op(destination=destination_public_key, amount=str(Decimal(amount)), asset_code="USDT")
        .set_timeout(30)
        .build()
    )

    transaction.sign(keypair)
    response = server.submit_transaction(transaction)
    return response


def stellar_transfer(wallet, amount, destination_wallet):
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
        .append_payment_op(destination=destination_wallet.stellar_public_key, amount=str(Decimal(amount)),
                           asset_code="USDT")
        .set_timeout(30)
        .build()
    )

    transaction.sign(keypair)
    response = server.submit_transaction(transaction)
    return response


def create_trustline(wallet, asset_code, asset_issuer):
    server = Server("https://horizon-testnet.stellar.org")
    stellar_private_key = decrypt_token(wallet.stellar_private_key)
    keypair = Keypair.from_secret(stellar_private_key)

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
    response = server.submit_transaction(transaction)
    return response
