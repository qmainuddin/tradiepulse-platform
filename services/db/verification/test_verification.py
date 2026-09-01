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
        # Valid NZ IRD numbers
        valid_irds = ["49-091-850", "49091850", "49-098-847", "49098847"]
        for ird in valid_irds:
            self.assertTrue(MockIRDProvider.validate_ird_checksum(ird), f"Expected valid: {ird}")

        # Invalid NZ IRD numbers
        invalid_irds = ["123-456-780", "111-111-111", "000-000-000", "49-091-859", "123"]
        for ird in invalid_irds:
            self.assertFalse(MockIRDProvider.validate_ird_checksum(ird), f"Expected invalid: {ird}")

    def test_ewrb_license_verification(self):
        async def run():
            provider = EWRBLicenseProvider()
            
            # Pass
            res_pass = await provider.verify({"licence_number": "EWRB-12345"})
            self.assertTrue(res_pass.passed)
            self.assertEqual(res_pass.stage, VerificationStage.LICENCE_CHECKED)

            # Fail
            res_fail = await provider.verify({"licence_number": ""})
            self.assertFalse(res_fail.passed)

        asyncio.run(run())

    def test_pgdb_license_verification(self):
        async def run():
            provider = PGDBLicenseProvider()
            res_pass = await provider.verify({"licence_number": "PGDB-9921"})
            self.assertTrue(res_pass.passed)
            self.assertEqual(res_pass.stage, VerificationStage.LICENCE_CHECKED)

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


if __name__ == "__main__":
    unittest.main()
