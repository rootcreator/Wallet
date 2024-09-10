import plaid
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.transactions_sync_request import TransactionsSyncRequest
from datetime import datetime

# Initialize the Plaid client
client_id = '66dbc120020d87001aba4e70',
secret = 'acd64823b2c80ca4ff48500b81f18d',

configuration = plaid.Configuration(
    host=plaid.Environment.Sandbox,  # or 'Development' or 'Production'
    api_key={
        'clientId': client_id,
        'secret': secret,
    }
)
api_client = plaid.ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)


def create_link_token():
    request = LinkTokenCreateRequest(
        user={'client_user_id': 'unique_user_id'},  # Replace with dynamic user ID if needed
        client_name='Your App',
        products=[plaid.model.Products('auth'), plaid.model.Products('transactions')],
        country_codes=[plaid.model.CountryCode('US')],
        language='en'
    )
    response = client.link_token_create(request)
    return response.to_dict()['link_token']


def exchange_public_token(public_token):
    request = ItemPublicTokenExchangeRequest(public_token=public_token)
    response = client.item_public_token_exchange(request)
    return response.to_dict()['access_token']


def retrieve_transactions(access_token, start_date, end_date):
    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

    request = TransactionsSyncRequest(access_token=access_token)
    response = client.transactions_sync(request)
    transactions = response.to_dict()['added']

    while response.to_dict()['has_more']:
        request = TransactionsSyncRequest(
            access_token=access_token,
            cursor=response.to_dict()['next_cursor']
        )
        response = client.transactions_sync(request)
        transactions += response.to_dict()['added']

    return transactions
