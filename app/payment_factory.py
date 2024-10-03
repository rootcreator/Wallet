from app.payment_services import (
    FlutterwaveAnchorBridge,
    TempoAnchorBridge,
    CircleAnchorBridge,
    SettleNetworkAnchorBridge,
    AlchemyPayAnchorBridge,
    MoneyGramAnchorBridge,
    StellarAnchorService,
)


def get_anchor_url_for_service(service_class) -> str:
    """Get the anchor URL for the specified payment service class."""
    anchor_urls = {
        FlutterwaveAnchorBridge: "https://flutterwave.com/api",
        TempoAnchorBridge: "https://tempo.com/api",
        CircleAnchorBridge: "https://circle.com/api",
        SettleNetworkAnchorBridge: "https://settlenetwork.com/api",
        AlchemyPayAnchorBridge: "https://alchemy.com/api",
        MoneyGramAnchorBridge: "https://moneygram.com/api",
    }

    return anchor_urls.get(service_class, "https://default.anchor.com/api")


class PaymentFactory:
    """Factory for creating payment service instances based on user region."""

    @staticmethod
    def get_payment_service(user_region: str):
        """Retrieve the appropriate payment service based on user region."""
        anchor_services = {
            "Africa": FlutterwaveAnchorBridge,
            "Europe": TempoAnchorBridge,
            "US": CircleAnchorBridge,
            "South America": SettleNetworkAnchorBridge,
            "Global": AlchemyPayAnchorBridge,
            "Global_MoneyGram": MoneyGramAnchorBridge,
        }

        # Get the service class based on user region, defaulting to Stellar
        service_class = anchor_services.get(user_region, StellarAnchorService)

        # Retrieve the anchor URL based on the selected service
        anchor_url = get_anchor_url_for_service(service_class)

        # Return an instance of the selected service with the anchor URL
        return service_class(anchor_url)
