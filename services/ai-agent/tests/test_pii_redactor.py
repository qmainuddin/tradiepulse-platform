import unittest
from src.rag.pii_redactor import PIIRedactor

class TestPIIRedactor(unittest.TestCase):

    def test_redact_nz_phone_numbers(self):
        sample = "Hi, my mobile number is 021 123 4567 or you can reach me at 03 355 9876."
        redacted = PIIRedactor.redact(sample)
        self.assertNotIn("021 123 4567", redacted)
        self.assertNotIn("03 355 9876", redacted)
        self.assertIn("[REDACTED_PHONE]", redacted)

    def test_redact_nz_international_phone(self):
        sample = "You can call my Christchurch mobile at +64 21 987 6543 or +64-3-366-0000."
        redacted = PIIRedactor.redact(sample)
        self.assertNotIn("+64 21 987 6543", redacted)
        self.assertNotIn("+64-3-366-0000", redacted)
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

    def test_redact_multiple_pii_in_single_message(self):
        sample = (
            "Hi, I'm John (john.doe@example.co.nz, ph 027 456 7890). "
            "My IRD is 49-091-850 and deposit card is 4111 2222 3333 4444."
        )
        redacted = PIIRedactor.redact(sample)
        self.assertNotIn("john.doe@example.co.nz", redacted)
        self.assertNotIn("027 456 7890", redacted)
        self.assertNotIn("49-091-850", redacted)
        self.assertNotIn("4111 2222 3333 4444", redacted)
        self.assertIn("[REDACTED_EMAIL]", redacted)
        self.assertIn("[REDACTED_PHONE]", redacted)
        self.assertIn("[REDACTED_IRD]", redacted)
        self.assertIn("[REDACTED_CREDIT_CARD]", redacted)

    def test_no_pii_passthrough(self):
        clean_text = "The hot water cylinder in my basement is making a loud banging noise."
        redacted = PIIRedactor.redact(clean_text)
        self.assertEqual(redacted, clean_text)

    def test_empty_and_none_handling(self):
        self.assertEqual(PIIRedactor.redact(""), "")
        self.assertIsNone(PIIRedactor.redact(None))


if __name__ == "__main__":
    unittest.main()
