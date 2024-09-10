from app.payment_methods import (
    initiate_flutterwave_deposit, initiate_flutterwave_withdrawal,
    initiate_circle_deposit, initiate_circle_withdrawal,
    initiate_tempo_deposit, initiate_tempo_withdrawal,
    initiate_settle_deposit, initiate_settle_withdrawal,
    initiate_virgocx_deposit, initiate_virgocx_withdrawal
)

ANCHORS = {
    'AF': {
        'name': 'Flutterwave',
        'currency': 'NGN',
        'deposit_url': 'https://api.flutterwave.com/v3/payments',
        'deposit_method': initiate_flutterwave_deposit,
        'withdraw_method': initiate_flutterwave_withdrawal,
    },
    'US': {
        'name': 'Circle',
        'currency': 'USD',
        'deposit_url': 'https://api.circle.com/v1/payments',
        'deposit_method': initiate_circle_deposit,
        'withdraw_method': initiate_circle_withdrawal,
    },
    'EU': {
        'name': 'Tempo',
        'currency': 'EUR',
        'deposit_url': 'https://api.tempo.eu.com/deposit',
        'deposit_method': initiate_tempo_deposit,
        'withdraw_method': initiate_tempo_withdrawal,
    },
    'UK': {
        'name': 'Settle Network',
        'currency': 'GBP',
        'deposit_url': 'https://api.settle.network/deposit',
        'deposit_method': initiate_settle_deposit,
        'withdraw_method': initiate_settle_withdrawal,
    },
    'CA': {
        'name': 'VirgoCX',
        'currency': 'CAD',
        'deposit_url': 'https://api.virgocx.ca/v1/payments',
        'deposit_method': initiate_virgocx_deposit,
        'withdraw_method': initiate_virgocx_withdrawal,
    },
}
