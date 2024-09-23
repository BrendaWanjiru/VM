# a mock to create a payment client
import logging
import random
import string

logger = logging.getLogger(__name__)


class PaymentClient:
    """
    This will depend on the payment gateway you are using.
    """

    def __init__(self):
        """
        Initialize the payment client.
        """

    def make_payment(self) -> str:
        """
        Make a payment.
        We create random strings to simulate what a payment client would do.
        """
        vm_initials = "GATE"
        numbers = "".join(random.sample(string.digits, k=2))
        lowercase_letters = "".join(random.choices(string.ascii_lowercase, k=4))
        final_string = numbers + lowercase_letters
        shuffled_string = "".join(random.sample(final_string, len(final_string)))
        code = vm_initials + shuffled_string

        # create random strings for payment_method, transaction_no, receipt_no, payment_ref, status and description
        transaction_no = "".join(
            random.choices(string.ascii_uppercase + string.digits, k=10),
        )
        receipt_no = "".join(
            random.choices(string.ascii_uppercase + string.digits, k=10),
        )
        payment_ref = "".join(
            random.choices(string.ascii_uppercase + string.digits, k=10),
        )
        payment_method = random.choice(["card", "paypal", "stripe"])
        status = random.choice(["processing", "completed", "cancelled"])

        return {
            "transaction_no": transaction_no.upper(),
            "receipt_no": receipt_no.upper(),
            "payment_ref": payment_ref.upper(),
            "payment_method": payment_method.upper(),
            "status": status,
            "description": "Payment for subscription",
        }
