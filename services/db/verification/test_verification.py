import unittest
import asyncio
from services.db.verification.providers import (
    MockIRDProvider,
    EWRBLicenseProvider,
    PGDBLicenseProvider,
    ChristchurchRegionalComplianceProvider,
    VerificationStage
)

class TestVerificationProviders(unittest.TestCase):

    def test_ird_modulus11_checksum(self):
        # Valid NZ IRD numbers (8 and 9 digits)
        valid_irds = ["49-091-850", "49091850", "49-098-847", "49098847", "105-001-541", "105001541"]
        for ird in valid_irds:
            self.assertTrue(MockIRDProvider.validate_ird_checksum(ird), f"Expected valid: {ird}")

        # Invalid NZ IRD numbers
        invalid_irds = [
            "123-456-780",
            "111-111-111",
            "000-000-000",
            "49-091-859",
            "123",
            "abcdefghi",
            "999-999-999-999",
            ""
        ]
        for ird in invalid_irds:
            self.assertFalse(MockIRDProvider.validate_ird_checksum(ird), f"Expected invalid: {ird}")

    def test_ird_provider_verification_async(self):
        async def run():
            provider = MockIRDProvider()

            # Valid IRD
            res_valid = await provider.verify({"ird_number": "49-091-850"})
            self.assertTrue(res_valid.passed)
            self.assertEqual(res_valid.stage, VerificationStage.TAX_CHECKED)

            # Missing IRD
            res_missing = await provider.verify({})
            self.assertFalse(res_missing.passed)
            self.assertIn("Missing IRD", res_missing.message)

            # Invalid IRD
            res_invalid = await provider.verify({"ird_number": "123-456-780"})
            self.assertFalse(res_invalid.passed)
            self.assertIn("Invalid NZ IRD", res_invalid.message)

        asyncio.run(run())

    def test_ewrb_license_verification(self):
        async def run():
            provider = EWRBLicenseProvider()
            
            # Pass with prefix
            res_pass = await provider.verify({"licence_number": "EWRB-12345"})
            self.assertTrue(res_pass.passed)
            self.assertEqual(res_pass.stage, VerificationStage.LICENCE_CHECKED)

            # Pass with numeric
            res_numeric = await provider.verify({"licence_number": "998822"})
            self.assertTrue(res_numeric.passed)

            # Fail with empty
            res_fail = await provider.verify({"licence_number": ""})
            self.assertFalse(res_fail.passed)

            # Fail with unknown prefix
            res_unknown = await provider.verify({"licence_number": "UNKNOWN-999"})
            self.assertFalse(res_unknown.passed)

        asyncio.run(run())

    def test_pgdb_license_verification(self):
        async def run():
            provider = PGDBLicenseProvider()

            # Pass
            res_pass = await provider.verify({"licence_number": "PGDB-9921"})
            self.assertTrue(res_pass.passed)
            self.assertEqual(res_pass.stage, VerificationStage.LICENCE_CHECKED)

            # Fail with empty
            res_fail = await provider.verify({"licence_number": ""})
            self.assertFalse(res_fail.passed)

            # Fail with invalid
            res_invalid = await provider.verify({"licence_number": "FAKE-PLUMB"})
            self.assertFalse(res_invalid.passed)

        asyncio.run(run())

    def test_christchurch_regional_compliance(self):
        async def run():
            provider = ChristchurchRegionalComplianceProvider()
            
            # Pass with policy
            res_pass = await provider.verify({
                "insurance_policy": "NZ-INS-884920",
                "region": "Christchurch"
            })
            self.assertTrue(res_pass.passed)
            self.assertEqual(res_pass.stage, VerificationStage.APPROVED)

            # Fail without insurance
            res_fail = await provider.verify({"insurance_policy": ""})
            self.assertFalse(res_fail.passed)

        asyncio.run(run())

    def test_full_tradie_onboarding_verification_pipeline(self):
        async def run():
            tradie_data = {
                "name": "Sarah Spark",
                "trade": "electrician",
                "ird_number": "49-091-850",
                "licence_number": "EWRB-778899",
                "insurance_policy": "NZ-INS-CANTERBURY-2M",
                "region": "Christchurch"
            }

            ird_prov = MockIRDProvider()
            ewrb_prov = EWRBLicenseProvider()
            chch_prov = ChristchurchRegionalComplianceProvider()

            ird_res = await ird_prov.verify(tradie_data)
            self.assertTrue(ird_res.passed)

            lic_res = await ewrb_prov.verify(tradie_data)
            self.assertTrue(lic_res.passed)

            chch_res = await chch_prov.verify(tradie_data)
            self.assertTrue(chch_res.passed)
            self.assertEqual(chch_res.stage, VerificationStage.APPROVED)

        asyncio.run(run())


if __name__ == "__main__":
    unittest.main()
