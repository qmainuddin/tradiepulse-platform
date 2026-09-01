import unittest
from src.rag.pii_redactor import PIIRedactor

class TestPIIRedactor(unittest.TestCase):

    def test_redact_nz_phone_numbers(self):
        sample = "Hi, my mobile number is 021 123 4567 or you can reach me at 03 355 9876."
        redacted = PIIRedactor.redact(sample)
        self.assertNotIn("021 123 4567", redacted)
        self.assertNotIn("03 355 9876", redacted)
        self.assertIn("[REDACTED_PHONE]", redacted)

    def test_redact_emails(self):
        sample = "Contact me at customer.test@gmail.com for the quote."
        redacted = PIIRedactor.redact(sample)
        self.assertNotIn("customer.test@gmail.com", redacted)
        self.assertIn("[REDACTED_EMAIL]", redacted)

    def test_redact_nz_ird_numbers(self):
        sample = "My NZ IRD number is 123-456-789."
        redacted = PIIRedactor.redact(sample)
        self.assertNotIn("123-456-789", redacted)
        self.assertIn("[REDACTED_IRD]", redacted)

    def test_redact_credit_cards(self):
        sample = "Card number: 4520 1234 5678 9012."
        redacted = PIIRedactor.redact(sample)
        self.assertNotIn("4520 1234 5678 9012", redacted)
        self.assertIn("[REDACTED_CREDIT_CARD]", redacted)


if __name__ == "__main__":
    unittest.main()
