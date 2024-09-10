from walletconnect import WalletConnect

# Initialize WalletConnect
wc = WalletConnect(
    bridge="https://bridge.walletconnect.org",  # Use the default bridge URL or your own
    qrcode=True
)

# Example usage
# Connect to a Wallet
uri = wc.get_uri()
print("Please scan this QR code with your WalletConnect-compatible wallet:", uri)
