import re

class PIIRedactor:
    """
    Sanitizes personally identifiable information (PII) before prompt transmission or logging.
    Enforces NZ Privacy Act 2020 compliance.
    """

    # NZ Landlines (03, 04, 06, 07, 09) and Mobiles (020-029) and International (+64)
    NZ_PHONE_REGEX = re.compile(
        r'(\+?64[-\s]?|0)(?:[234679]\d{0,2})[-\s]?\d{3,4}[-\s]?\d{3,4}\b'
    )
    # Email addresses
    EMAIL_REGEX = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    # NZ IRD number: 8 or 9 digits (e.g. 123-456-789 or 12-345-678 or 123456789)
    NZ_IRD_REGEX = re.compile(r'\b\d{2,3}[-\s]?\d{3}[-\s]?\d{3}\b')
    # Credit Card numbers
    CREDIT_CARD_REGEX = re.compile(r'\b(?:\d{4}[-\s]?){3}\d{4}\b')

    @classmethod
    def redact(cls, text: str) -> str:
        if not text:
            return text
        
        redacted = cls.EMAIL_REGEX.sub("[REDACTED_EMAIL]", text)
        redacted = cls.CREDIT_CARD_REGEX.sub("[REDACTED_CREDIT_CARD]", redacted)
        redacted = cls.NZ_IRD_REGEX.sub("[REDACTED_IRD]", redacted)
        redacted = cls.NZ_PHONE_REGEX.sub("[REDACTED_PHONE]", redacted)
        return redacted
