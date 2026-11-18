# Bilanz-Programm

Konsolenprogramm (Python 3, ohne externe Abhängigkeiten), das aus eingegebenen
Posten (Konten) und Buchungssätzen nach der doppelten Buchführung eine
**Bilanz** sowie eine **Gewinn- und Verlustrechnung** erstellt.

## Start

```bash
python3 bilanz.py              # interaktives Menü
python3 bilanz.py daten.json   # gespeicherte Buchhaltung laden
python3 -m unittest test_bilanz  # Tests
```

## Ablauf

1. **Posten anlegen** – Name, Kontoart und (bei Bestandskonten) Anfangsbestand
   - `aktiv`   – Vermögen (Maschinen, Waren, Forderungen, Bank, Kasse …)
   - `passiv`  – Kapital (Eigenkapital, Darlehen, Verbindlichkeiten …)
   - `aufwand` – Aufwendungen (Miete, Löhne …)
   - `ertrag`  – Erträge (Umsatzerlöse …)
2. **Buchungen erfassen** – Buchungssatz *Soll an Haben* mit Betrag,
   z. B. `Bank an Umsatzerlöse 15.000,00`
3. **Bilanz erstellen** – Schlussbestände aller Aktiv-/Passivkonten; der
   Saldo der Erfolgskonten (Jahresüberschuss/-fehlbetrag) wird auf der
   Passivseite ausgewiesen. Das Programm prüft, ob die Bilanz ausgeglichen ist.

Weitere Funktionen: T-Konten, Journal, Kontenübersicht, Buchungen löschen,
Speichern/Laden als JSON, Beispieldaten (Menüpunkt 10).
