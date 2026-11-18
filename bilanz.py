#!/usr/bin/env python3
"""
Bilanz-Programm
===============

Erfasst Posten (Konten) mit Anfangsbeständen und Buchungssätzen
("Soll an Haben") nach dem Prinzip der doppelten Buchführung und
erstellt daraus eine Gewinn- und Verlustrechnung sowie eine Bilanz.

Kontenarten:
    aktiv   - Aktivkonto (Vermögen, z. B. Kasse, Bank, Maschinen)
    passiv  - Passivkonto (Kapital, z. B. Eigenkapital, Darlehen)
    aufwand - Aufwandskonto (z. B. Miete, Löhne)
    ertrag  - Ertragskonto (z. B. Umsatzerlöse)

Start:  python3 bilanz.py            (interaktives Menü)
        python3 bilanz.py datei.json (lädt vorher eine gespeicherte Datei)
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

KONTOARTEN = {
    "aktiv": "Aktivkonto",
    "passiv": "Passivkonto",
    "aufwand": "Aufwandskonto",
    "ertrag": "Ertragskonto",
}

CENT = Decimal("0.01")


# --------------------------------------------------------------------------
# Hilfsfunktionen
# --------------------------------------------------------------------------

def parse_betrag(text: str) -> Decimal:
    """Wandelt Eingaben wie '1.234,56', '1234.56' oder '1234' in Decimal um."""
    t = text.strip().replace("€", "").replace(" ", "")
    if not t:
        raise ValueError("Kein Betrag angegeben.")
    if "," in t:
        # deutsches Format: Punkte = Tausendertrennzeichen, Komma = Dezimal
        t = t.replace(".", "").replace(",", ".")
    try:
        wert = Decimal(t)
    except InvalidOperation:
        raise ValueError(f"Ungültiger Betrag: {text!r}") from None
    if not wert.is_finite():
        raise ValueError(f"Ungültiger Betrag: {text!r}")
    return wert.quantize(CENT, rounding=ROUND_HALF_UP)


def fmt(betrag: Decimal) -> str:
    """Formatiert einen Betrag im deutschen Format, z. B. 1.234,56 €."""
    s = f"{betrag:,.2f}"  # 1,234.56
    s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{s} €"


# --------------------------------------------------------------------------
# Datenmodell
# --------------------------------------------------------------------------

@dataclass
class Konto:
    name: str
    art: str
    anfangsbestand: Decimal = Decimal("0.00")

    @property
    def ist_bestandskonto(self) -> bool:
        return self.art in ("aktiv", "passiv")

    @property
    def soll_mehrung(self) -> bool:
        """Aktiv- und Aufwandskonten nehmen im Soll zu."""
        return self.art in ("aktiv", "aufwand")


@dataclass
class Buchung:
    soll: str
    haben: str
    betrag: Decimal
    text: str = ""


@dataclass
class Buchhaltung:
    konten: dict[str, Konto] = field(default_factory=dict)
    buchungen: list[Buchung] = field(default_factory=list)

    # ---- Konten ---------------------------------------------------------

    def _finde(self, name: str) -> Konto:
        key = name.strip().lower()
        for konto in self.konten.values():
            if konto.name.lower() == key:
                return konto
        raise KeyError(f"Konto {name!r} existiert nicht.")

    def konto_anlegen(self, name: str, art: str,
                      anfangsbestand: Decimal = Decimal("0.00")) -> Konto:
        name = name.strip()
        art = art.strip().lower()
        if not name:
            raise ValueError("Kontoname darf nicht leer sein.")
        if art not in KONTOARTEN:
            raise ValueError(f"Unbekannte Kontoart {art!r}. "
                             f"Erlaubt: {', '.join(KONTOARTEN)}")
        if any(k.name.lower() == name.lower() for k in self.konten.values()):
            raise ValueError(f"Konto {name!r} existiert bereits.")
        if anfangsbestand < 0:
            raise ValueError("Anfangsbestand darf nicht negativ sein.")
        if art in ("aufwand", "ertrag") and anfangsbestand != 0:
            raise ValueError("Erfolgskonten haben keinen Anfangsbestand.")
        konto = Konto(name, art, anfangsbestand)
        self.konten[name] = konto
        return konto

    def konto_loeschen(self, name: str) -> None:
        konto = self._finde(name)
        if any(konto.name in (b.soll, b.haben) for b in self.buchungen):
            raise ValueError("Konto wird in Buchungen verwendet und kann "
                             "nicht gelöscht werden.")
        del self.konten[konto.name]

    # ---- Buchungen ------------------------------------------------------

    def buchen(self, soll: str, haben: str, betrag: Decimal,
               text: str = "") -> Buchung:
        k_soll = self._finde(soll)
        k_haben = self._finde(haben)
        if k_soll is k_haben:
            raise ValueError("Soll- und Habenkonto müssen verschieden sein.")
        if betrag <= 0:
            raise ValueError("Betrag muss größer als 0 sein.")
        buchung = Buchung(k_soll.name, k_haben.name, betrag, text.strip())
        self.buchungen.append(buchung)
        return buchung

    def buchung_stornieren(self, index: int) -> Buchung:
        if not 0 <= index < len(self.buchungen):
            raise IndexError("Ungültige Buchungsnummer.")
        return self.buchungen.pop(index)

    # ---- Auswertung -----------------------------------------------------

    def umsaetze(self, konto: Konto) -> tuple[Decimal, Decimal]:
        """Summe der Soll- und Habenbuchungen eines Kontos."""
        soll = sum((b.betrag for b in self.buchungen if b.soll == konto.name),
                   Decimal("0.00"))
        haben = sum((b.betrag for b in self.buchungen if b.haben == konto.name),
                    Decimal("0.00"))
        return soll, haben

    def saldo(self, konto: Konto) -> Decimal:
        """Endbestand (Schlussbestand) eines Kontos."""
        soll, haben = self.umsaetze(konto)
        if konto.soll_mehrung:
            return konto.anfangsbestand + soll - haben
        return konto.anfangsbestand + haben - soll

    def konten_nach_art(self, art: str) -> list[Konto]:
        return [k for k in self.konten.values() if k.art == art]

    def summe(self, art: str, anfang: bool = False) -> Decimal:
        return sum(((k.anfangsbestand if anfang else self.saldo(k))
                    for k in self.konten_nach_art(art)), Decimal("0.00"))

    def jahresergebnis(self) -> Decimal:
        """Erträge minus Aufwendungen (positiv = Gewinn)."""
        return self.summe("ertrag") - self.summe("aufwand")

    def eroeffnung_ausgeglichen(self) -> bool:
        return self.summe("aktiv", True) == self.summe("passiv", True)

    def bilanz(self) -> dict:
        """Liefert die Bilanzposten als Datenstruktur."""
        aktiva = [(k.name, self.saldo(k)) for k in self.konten_nach_art("aktiv")]
        passiva = [(k.name, self.saldo(k)) for k in self.konten_nach_art("passiv")]
        ergebnis = self.jahresergebnis()
        if ergebnis != 0:
            bez = "Jahresüberschuss" if ergebnis > 0 else "Jahresfehlbetrag"
            passiva.append((bez, ergebnis))
        summe_a = sum((b for _, b in aktiva), Decimal("0.00"))
        summe_p = sum((b for _, b in passiva), Decimal("0.00"))
        return {
            "aktiva": aktiva,
            "passiva": passiva,
            "summe_aktiva": summe_a,
            "summe_passiva": summe_p,
            "ausgeglichen": summe_a == summe_p,
        }

    # ---- Speichern / Laden ---------------------------------------------

    def to_dict(self) -> dict:
        return {
            "konten": [{"name": k.name, "art": k.art,
                        "anfangsbestand": str(k.anfangsbestand)}
                       for k in self.konten.values()],
            "buchungen": [{"soll": b.soll, "haben": b.haben,
                           "betrag": str(b.betrag), "text": b.text}
                          for b in self.buchungen],
        }

    @classmethod
    def from_dict(cls, daten: dict) -> "Buchhaltung":
        bh = cls()
        for k in daten.get("konten", []):
            bh.konto_anlegen(k["name"], k["art"], Decimal(k["anfangsbestand"]))
        for b in daten.get("buchungen", []):
            bh.buchen(b["soll"], b["haben"], Decimal(b["betrag"]),
                      b.get("text", ""))
        return bh

    def speichern(self, pfad: str) -> None:
        with open(pfad, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)

    @classmethod
    def laden(cls, pfad: str) -> "Buchhaltung":
        with open(pfad, encoding="utf-8") as f:
            return cls.from_dict(json.load(f))


# --------------------------------------------------------------------------
# Textausgabe
# --------------------------------------------------------------------------

BREITE = 38  # Breite einer Bilanzseite


def bilanz_text(bh: Buchhaltung) -> str:
    """Erstellt die Bilanz in klassischer T-Konto-Form."""
    b = bh.bilanz()
    links = [f"{n[:BREITE - 16]:<{BREITE - 16}}{fmt(v):>16}" for n, v in b["aktiva"]]
    rechts = [f"{n[:BREITE - 16]:<{BREITE - 16}}{fmt(v):>16}" for n, v in b["passiva"]]
    zeilen = max(len(links), len(rechts))
    links += [" " * BREITE] * (zeilen - len(links))
    rechts += [" " * BREITE] * (zeilen - len(rechts))

    gesamt = BREITE * 2 + 3
    out = [
        "=" * gesamt,
        "BILANZ".center(gesamt),
        "=" * gesamt,
        f"{'AKTIVA':<{BREITE}} | {'PASSIVA':<{BREITE}}",
        "-" * gesamt,
    ]
    out += [f"{l} | {r}" for l, r in zip(links, rechts)]
    out.append("-" * gesamt)
    out.append(f"{'Summe':<{BREITE - 16}}{fmt(b['summe_aktiva']):>16} | "
               f"{'Summe':<{BREITE - 16}}{fmt(b['summe_passiva']):>16}")
    out.append("=" * gesamt)

    if b["ausgeglichen"]:
        out.append("✔ Die Bilanz ist ausgeglichen.")
    else:
        diff = b["summe_aktiva"] - b["summe_passiva"]
        out.append(f"✘ Die Bilanz ist NICHT ausgeglichen (Differenz {fmt(diff)}).")
        if not bh.eroeffnung_ausgeglichen():
            out.append("  Ursache: Die Anfangsbestände sind nicht ausgeglichen "
                       f"(Aktiva {fmt(bh.summe('aktiv', True))} / "
                       f"Passiva {fmt(bh.summe('passiv', True))}).")
    return "\n".join(out)


def guv_text(bh: Buchhaltung) -> str:
    """Gewinn- und Verlustrechnung."""
    out = ["=" * 50, "GEWINN- UND VERLUSTRECHNUNG".center(50), "=" * 50]
    out.append("Erträge:")
    for k in bh.konten_nach_art("ertrag"):
        out.append(f"  {k.name:<30}{fmt(bh.saldo(k)):>16}")
    out.append(f"  {'Summe Erträge':<30}{fmt(bh.summe('ertrag')):>16}")
    out.append("Aufwendungen:")
    for k in bh.konten_nach_art("aufwand"):
        out.append(f"  {k.name:<30}{fmt(bh.saldo(k)):>16}")
    out.append(f"  {'Summe Aufwendungen':<30}{fmt(bh.summe('aufwand')):>16}")
    out.append("-" * 50)
    erg = bh.jahresergebnis()
    bez = "Jahresüberschuss" if erg >= 0 else "Jahresfehlbetrag"
    out.append(f"  {bez:<30}{fmt(erg):>16}")
    return "\n".join(out)


def t_konto_text(bh: Buchhaltung, konto: Konto) -> str:
    """Stellt ein Konto als T-Konto mit allen Buchungen dar."""
    w = 30
    soll_zeilen, haben_zeilen = [], []
    if konto.ist_bestandskonto:
        ab = f"{'AB':<{w - 16}}{fmt(konto.anfangsbestand):>16}"
        (soll_zeilen if konto.art == "aktiv" else haben_zeilen).append(ab)
    for b in bh.buchungen:
        if b.soll == konto.name:
            soll_zeilen.append(f"{b.haben[:w - 17]:<{w - 16}}{fmt(b.betrag):>16}")
        if b.haben == konto.name:
            haben_zeilen.append(f"{b.soll[:w - 17]:<{w - 16}}{fmt(b.betrag):>16}")

    saldo = bh.saldo(konto)
    bez = "SB" if konto.ist_bestandskonto else "Saldo"
    zeile = f"{bez:<{w - 16}}{fmt(abs(saldo)):>16}"
    # Saldo steht auf der kleineren Seite
    if (saldo >= 0) == konto.soll_mehrung:
        haben_zeilen.append(zeile)
    else:
        soll_zeilen.append(zeile)

    n = max(len(soll_zeilen), len(haben_zeilen))
    soll_zeilen += [" " * w] * (n - len(soll_zeilen))
    haben_zeilen += [" " * w] * (n - len(haben_zeilen))
    titel = f"{konto.name} ({KONTOARTEN[konto.art]})"
    out = [titel.center(2 * w + 3), "-" * (2 * w + 3),
           f"{'Soll':<{w}} | {'Haben':>{w}}", "-" * (2 * w + 3)]
    out += [f"{s} | {h}" for s, h in zip(soll_zeilen, haben_zeilen)]
    return "\n".join(out)


def journal_text(bh: Buchhaltung) -> str:
    if not bh.buchungen:
        return "Noch keine Buchungen erfasst."
    out = [f"{'Nr':>3}  {'Soll':<20} an {'Haben':<20}{'Betrag':>16}  Text",
           "-" * 80]
    for i, b in enumerate(bh.buchungen, 1):
        out.append(f"{i:>3}  {b.soll[:20]:<20} an {b.haben[:20]:<20}"
                   f"{fmt(b.betrag):>16}  {b.text}")
    return "\n".join(out)


def konten_text(bh: Buchhaltung) -> str:
    if not bh.konten:
        return "Noch keine Konten angelegt."
    out = [f"{'Konto':<25}{'Art':<16}{'Anfang':>16}{'Ende':>16}", "-" * 73]
    for k in bh.konten.values():
        ab = fmt(k.anfangsbestand) if k.ist_bestandskonto else "-"
        out.append(f"{k.name[:24]:<25}{KONTOARTEN[k.art]:<16}{ab:>16}"
                   f"{fmt(bh.saldo(k)):>16}")
    return "\n".join(out)


# --------------------------------------------------------------------------
# Beispieldaten
# --------------------------------------------------------------------------

def beispiel() -> Buchhaltung:
    bh = Buchhaltung()
    D = Decimal
    bh.konto_anlegen("Maschinen", "aktiv", D("50000"))
    bh.konto_anlegen("Waren", "aktiv", D("12000"))
    bh.konto_anlegen("Forderungen", "aktiv", D("8000"))
    bh.konto_anlegen("Bank", "aktiv", D("25000"))
    bh.konto_anlegen("Kasse", "aktiv", D("3000"))
    bh.konto_anlegen("Eigenkapital", "passiv", D("60000"))
    bh.konto_anlegen("Darlehen", "passiv", D("30000"))
    bh.konto_anlegen("Verbindlichkeiten", "passiv", D("8000"))
    bh.konto_anlegen("Umsatzerlöse", "ertrag")
    bh.konto_anlegen("Mietaufwand", "aufwand")
    bh.konto_anlegen("Löhne", "aufwand")

    bh.buchen("Bank", "Forderungen", D("5000"), "Kunde zahlt Rechnung")
    bh.buchen("Verbindlichkeiten", "Bank", D("4000"), "Lieferantenrechnung bezahlt")
    bh.buchen("Bank", "Umsatzerlöse", D("15000"), "Warenverkauf")
    bh.buchen("Mietaufwand", "Bank", D("2000"), "Miete Büro")
    bh.buchen("Löhne", "Bank", D("6000"), "Lohnzahlung")
    bh.buchen("Darlehen", "Bank", D("3000"), "Tilgung Darlehen")
    bh.buchen("Kasse", "Bank", D("1000"), "Bargeldabhebung")
    return bh


# --------------------------------------------------------------------------
# Interaktives Menü
# --------------------------------------------------------------------------

def frage(prompt: str) -> str:
    try:
        return input(prompt)
    except EOFError:
        print()
        raise SystemExit(0)


def waehle_konto(bh: Buchhaltung, prompt: str) -> str:
    namen = list(bh.konten)
    for i, n in enumerate(namen, 1):
        print(f"  {i:>2}) {n} ({KONTOARTEN[bh.konten[n].art]})")
    eingabe = frage(prompt).strip()
    if eingabe.isdigit() and 1 <= int(eingabe) <= len(namen):
        return namen[int(eingabe) - 1]
    return eingabe


def menue_konto_anlegen(bh: Buchhaltung) -> None:
    name = frage("Name des Postens/Kontos: ")
    print("Kontoart: 1) aktiv  2) passiv  3) aufwand  4) ertrag")
    art = frage("Auswahl: ").strip().lower()
    art = {"1": "aktiv", "2": "passiv", "3": "aufwand", "4": "ertrag"}.get(art, art)
    ab = Decimal("0.00")
    if art in ("aktiv", "passiv"):
        eingabe = frage("Anfangsbestand (Enter = 0): ").strip()
        if eingabe:
            ab = parse_betrag(eingabe)
    konto = bh.konto_anlegen(name, art, ab)
    print(f"→ Konto '{konto.name}' ({KONTOARTEN[konto.art]}) angelegt.")


def menue_buchen(bh: Buchhaltung) -> None:
    if len(bh.konten) < 2:
        print("Bitte zuerst mindestens zwei Konten anlegen.")
        return
    print("Buchungssatz: SOLL an HABEN")
    soll = waehle_konto(bh, "Soll-Konto (Nummer oder Name): ")
    haben = waehle_konto(bh, "Haben-Konto (Nummer oder Name): ")
    betrag = parse_betrag(frage("Betrag: "))
    text = frage("Buchungstext (optional): ")
    b = bh.buchen(soll, haben, betrag, text)
    print(f"→ Gebucht: {b.soll} an {b.haben} {fmt(b.betrag)}")


def menue_stornieren(bh: Buchhaltung) -> None:
    print(journal_text(bh))
    if not bh.buchungen:
        return
    nr = frage("Nummer der zu löschenden Buchung: ").strip()
    if not nr.isdigit():
        raise ValueError("Bitte eine Nummer eingeben.")
    b = bh.buchung_stornieren(int(nr) - 1)
    print(f"→ Buchung '{b.soll} an {b.haben} {fmt(b.betrag)}' gelöscht.")


def menue_t_konten(bh: Buchhaltung) -> None:
    if not bh.konten:
        print("Noch keine Konten angelegt.")
        return
    for k in bh.konten.values():
        print(t_konto_text(bh, k))
        print()


MENUE = """
==================== BILANZ-PROGRAMM ====================
 1) Posten/Konto anlegen        6) Gewinn- und Verlustrechnung
 2) Buchung erfassen            7) BILANZ erstellen
 3) Buchung löschen             8) Speichern
 4) Kontenübersicht             9) Laden
 5) T-Konten anzeigen          10) Beispieldaten laden
 J) Journal (alle Buchungen)    0) Beenden
=========================================================="""


def main(argv: list[str]) -> None:
    bh = Buchhaltung()
    if len(argv) > 1:
        bh = Buchhaltung.laden(argv[1])
        print(f"Datei '{argv[1]}' geladen.")

    while True:
        print(MENUE)
        wahl = frage("Auswahl: ").strip().lower()
        try:
            if wahl == "1":
                menue_konto_anlegen(bh)
            elif wahl == "2":
                menue_buchen(bh)
            elif wahl == "3":
                menue_stornieren(bh)
            elif wahl == "4":
                print(konten_text(bh))
            elif wahl == "5":
                menue_t_konten(bh)
            elif wahl == "6":
                print(guv_text(bh))
            elif wahl == "7":
                print(bilanz_text(bh))
            elif wahl == "8":
                pfad = frage("Dateiname (Enter = buchhaltung.json): ").strip()
                bh.speichern(pfad or "buchhaltung.json")
                print("→ Gespeichert.")
            elif wahl == "9":
                pfad = frage("Dateiname (Enter = buchhaltung.json): ").strip()
                bh = Buchhaltung.laden(pfad or "buchhaltung.json")
                print("→ Geladen.")
            elif wahl == "10":
                bh = beispiel()
                print("→ Beispieldaten geladen. Wähle 7 für die Bilanz.")
            elif wahl == "j":
                print(journal_text(bh))
            elif wahl in ("0", "q", "exit"):
                print("Auf Wiedersehen!")
                return
            else:
                print("Unbekannte Auswahl.")
        except (ValueError, KeyError, IndexError, OSError,
                json.JSONDecodeError) as e:
            msg = e.args[0] if isinstance(e, KeyError) and e.args else e
            print(f"Fehler: {msg}")


if __name__ == "__main__":
    main(sys.argv)
