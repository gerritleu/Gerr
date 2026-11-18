import os
import tempfile
import unittest
from decimal import Decimal as D

from bilanz import Buchhaltung, beispiel, bilanz_text, parse_betrag, fmt


class TestBilanz(unittest.TestCase):
    def test_parse_betrag(self):
        self.assertEqual(parse_betrag("1.234,56"), D("1234.56"))
        self.assertEqual(parse_betrag("1234.5"), D("1234.50"))
        self.assertEqual(parse_betrag("100 €"), D("100.00"))
        with self.assertRaises(ValueError):
            parse_betrag("abc")

    def test_fmt(self):
        self.assertEqual(fmt(D("1234567.8")), "1.234.567,80 €")

    def test_beispiel_ausgeglichen(self):
        bh = beispiel()
        b = bh.bilanz()
        self.assertTrue(b["ausgeglichen"])
        self.assertEqual(bh.jahresergebnis(), D("7000"))
        self.assertEqual(b["summe_aktiva"], D("98000"))
        self.assertIn(("Jahresüberschuss", D("7000")), b["passiva"])

    def test_saldo_passivkonto(self):
        bh = beispiel()
        self.assertEqual(bh.saldo(bh.konten["Darlehen"]), D("27000"))
        self.assertEqual(bh.saldo(bh.konten["Bank"]), D("29000"))

    def test_verlust(self):
        bh = Buchhaltung()
        bh.konto_anlegen("Bank", "aktiv", D("1000"))
        bh.konto_anlegen("EK", "passiv", D("1000"))
        bh.konto_anlegen("Miete", "aufwand")
        bh.buchen("miete", "BANK", D("300"))  # Groß-/Kleinschreibung egal
        b = bh.bilanz()
        self.assertTrue(b["ausgeglichen"])
        self.assertIn(("Jahresfehlbetrag", D("-300")), b["passiva"])

    def test_fehler(self):
        bh = Buchhaltung()
        bh.konto_anlegen("Bank", "aktiv")
        with self.assertRaises(ValueError):
            bh.konto_anlegen("bank", "passiv")
        with self.assertRaises(ValueError):
            bh.konto_anlegen("X", "unsinn")
        with self.assertRaises(KeyError):
            bh.buchen("Bank", "Gibtsnicht", D("1"))
        with self.assertRaises(ValueError):
            bh.buchen("Bank", "Bank", D("1"))

    def test_unausgeglichene_eroeffnung(self):
        bh = Buchhaltung()
        bh.konto_anlegen("Bank", "aktiv", D("100"))
        self.assertIn("NICHT ausgeglichen", bilanz_text(bh))

    def test_speichern_laden(self):
        bh = beispiel()
        with tempfile.TemporaryDirectory() as d:
            pfad = os.path.join(d, "x.json")
            bh.speichern(pfad)
            bh2 = Buchhaltung.laden(pfad)
        self.assertEqual(bh.bilanz(), bh2.bilanz())
        self.assertEqual(len(bh2.buchungen), len(bh.buchungen))


if __name__ == "__main__":
    unittest.main()
