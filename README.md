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

## HTML-Version

`bilanz.html` einfach im Browser öffnen – gleiche Funktionen mit grafischer
Oberfläche, Daten bleiben im Browser gespeichert. JSON-Dateien des
Python-Programms können dort ebenfalls geladen werden.

## Neon Heat Arcade

Sammlung von Browser-Minispielen im Neon-Sonnenuntergangs-Look (Ordner
`neon-heat/`). Einfach `neon-heat/index.html` öffnen – keine Installation nötig.

| Spiel | Datei | Prinzip |
|---|---|---|
| Highway Rush | `highway.html` | Verkehr ausweichen, Geldsäcke sammeln |
| Safe Cracker | `safecracker.html` | Timing: Zeiger in der grünen Zone stoppen |
| Grid Hacker | `hacker.html` | Code-Sequenzen merken und nachtippen |
| Lucky Palms | `casino.html` | Spielautomat mit der gemeinsamen Bank |
| Neon Mines | `minesweeper.html` | Klassisches Minesweeper |
| Getaway | `getaway.html` | Labyrinth-Flucht vor der Streife |

Alle Gewinne landen in einer gemeinsamen Bank (im Browser gespeichert), die im
Hub einen Rang freischaltet.
