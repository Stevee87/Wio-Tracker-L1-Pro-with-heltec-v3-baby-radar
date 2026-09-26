# RadarRemote 2.1 – schnelle Live-Version mit Wio-Displaykorrektur

Eigene Radarstation: **RD-03D am Heltec WiFi LoRa 32 V3/V3.2**, Anzeige und Bedienung auf dem **Wio Tracker L1 Pro mit OLED**. Beide Funkmodule sind die EU868-Ausführung. Diese Firmware ersetzt Meshtastic.

**Stand vom 25.09.2026:** Beide Geräte wurden vom Nutzer geflasht; die Displays, die Funkverbindung und die Anzeige von Radar-Zielen funktionieren nach seiner Rückmeldung. Die Datenverarbeitung wurde zusätzlich automatisiert geprüft. Die tatsächlich erreichte Aktualisierungsrate, Latenz und Funkreichweite sind noch nicht gemessen.

In Version 2.1 verwendet der Wio den passenden **SH1106**-Displaytreiber; die Displayadresse wird zuerst an **0x3D**, ersatzweise an 0x3C geprüft. Bootloader und das fehlerfreie Aufspielen der ursprünglichen Datei wurden am angeschlossenen Wio überprüft.

**Update von 2.0: Nur den Wio neu flashen.** Die Heltec-Datei bleibt unverändert und ist kompatibel. Nach dem Aufspielen sollte zunächst „RadarRemote 2.1 / Display OK“ erscheinen, danach die Radaransicht oder „SUCHE STATION“. Auf dem Wio-Bootlaufwerk vorher **nichts löschen und nichts formatieren**; nur die neue UF2 darauf kopieren.

Version 2 nutzt **GFSK mit 100 kbit/s** auf denselben Funkchips. Der Wio fragt die Zielpositionen im 50-ms-Takt ab: **bis zu 20 Funkaktualisierungen und 20 Displaybilder pro Sekunde**. Die bisherige Wartezeit von über einer Sekunde entfällt. Die echten neuen Positionen bleiben durch die Messrate des Radars begrenzt; Reichweite und tatsächliche Bildrate sind noch nicht am Gerät gemessen. Gegenüber dem langsameren LoRa-Modus ist mit geringerer Funkreichweite zu rechnen.

**Beide Geräte auf Version 2 aktualisieren.** Version 1 und Version 2 können wegen des anderen Funkmodus nicht miteinander kommunizieren. Die Verdrahtung bleibt gleich.

## 1. Anschließen

Heltec ausschließlich über USB-C mit Strom versorgen. Wio nutzt seine eigene Versorgung.

| RD-03D, nach Beschriftung | Heltec V3/V3.2 |
|---|---|
| 5V | 5V |
| GND | GND |
| TX | GPIO 4 |
| RX | GPIO 5 |

Die Nummern 4 und 5 sind **GPIO-Nummern**, keine abgezählten Steckplätze. RX/TX sind gekreuzt. Beim RD-03D sind die UART-Signale 3,3 V; die Versorgung ist 5 V. Nicht mit 3V3 oder Vext versorgen. Das USB-Netzteil muss neben dem Heltec mindestens 200 mA für das Radar bereitstellen; ein stabiles 5-V-/1-A-Netzteil bietet Reserve. Zum Verdrahten USB abziehen. Vor dem Einschalten eine passende LoRa-Antenne am Heltec anschließen.

Der Original-RD-03D nutzt 256000 Baud, 8N1. Nach dem Start wird einmal der Mehrzielmodus angefordert. Die Radarstation zeigt „RD03D: Daten OK“, sobald gültige Messrahmen eingehen.

## 2. Fertige Dateien aufspielen

Die fertigen Dateien liegen im Ordner [firmware](firmware):

- [Heltec_Radarstation_merged.bin](firmware/Heltec_Radarstation_merged.bin) für den Heltec V3/V3.2, Flash-Adresse **0x0**.
- [Wio_RadarRemote.uf2](firmware/Wio_RadarRemote.uf2) für den Wio Tracker L1 Pro.
- [SHA256SUMS.txt](firmware/SHA256SUMS.txt) enthält die Prüfsummen beider Dateien.

Bei GitHub die jeweilige Datei herunterladen ("Download raw file"), nicht die HTML-Seite speichern. Die hier enthaltenen Binärdateien entsprechen dem vom Nutzer erfolgreich in Betrieb genommenen Stand.

### Wio L1 Pro

1. Wio per USB-Datenkabel anschließen.
2. Reset zweimal kurz drücken, um das UF2-Bootlaufwerk zu öffnen.
3. In `INFO_UF2.TXT` prüfen, dass das Board tatsächlich ein Wio Tracker L1 ist. Dieses Paket erwartet den üblichen L1-Bootloader mit **S140 7.3.0**. Bei abweichendem Board/SoftDevice zuerst den passenden Seeed-Bootloaderstand klären; keine fremden Bootloaderdateien aufspielen.
4. `firmware/Wio_RadarRemote.uf2` auf das Bootlaufwerk kopieren. Das Gerät startet neu.

Die UF2 enthält nur die Anwendung ab Adresse **0x27000**; SoftDevice und Bootloader werden nicht überschrieben. Sie ist nicht für den L1 E-Ink, T1000 oder T114 vorgesehen.

### Heltec V3/V3.2

`firmware/Heltec_Radarstation_merged.bin` ist ein **zusammengefasstes Image** und gehört an Adresse **0x0**. Es enthält Bootloader, Partitionstabelle und Anwendung. Es ersetzt die bisherige Anwendung und deren Partitionierung.

Mit dem offiziellen [Espressif-Browserflasher](https://espressif.github.io/esptool-js/) in Chrome/Edge verbinden, den Port des Heltec auswählen, Datei hinzufügen und als Flash-Adresse `0x0` angeben. Nach dem Schreiben den Heltec zurücksetzen. Falls keine Verbindung entsteht: BOOT/USER halten, RESET kurz drücken, BOOT/USER loslassen und erneut verbinden.

Bleibt das Heltec-Display nach dem Flashen schwarz: Im Flasher die Verbindung trennen, USB abziehen und wieder einstecken, dann einmal RESET drücken, ohne BOOT/USER gedrückt zu halten. Zur Eingrenzung kann das Radar bei abgezogenem USB vorübergehend abgeklemmt werden. Auch ohne Radar muss der Heltec seine Statusanzeige zeigen.

Alternativ mit installiertem PlatformIO im Projektordner:

```powershell
pio run -e heltec_station -t upload --upload-port COM7
```

`COM7` durch den tatsächlichen Heltec-Port ersetzen. Dieser Weg baut und lädt die Einzelbestandteile selbst.

## 3. Bedienung am Wio

| Taste | Funktion |
|---|---|
| Joystick oben | Zoom näher: 8 → 4 → 2 m |
| Joystick unten | Zoom weiter: 2 → 4 → 8 m |
| Joystick links/rechts | Erkannten Zielslot auswählen |
| Joystick drücken | Zielübertragung pausieren / starten |
| Separate Menü-/Benutzertaste | Radaransicht → Zieldetails → Funk-/Messrate → Radaransicht |

Der größere Kreis markiert den ausgewählten Zielpunkt. Die vier Entfernungsringe teilen den angezeigten Maximalabstand gleichmäßig. Ursprung unten = Radarsensor; oben = vor dem Radar. Positive X-Werte liegen rechts vom Sensor. Der Wio-Standort und seine Blickrichtung verändern diesen Bezug nicht.

Die Detailansicht zeigt Entfernung, Winkel und vorzeichenbehaftete radiale Geschwindigkeit. Slots 1–3 kommen vom Sensor und sind **keine dauerhaft identifizierten Personen**. Ziele außerhalb des Zooms werden nicht gezeichnet, zählen aber weiter zur Zielzahl `Z`. `S` bezeichnet den ausgewählten Slot.

## 4. Status verstehen

| Anzeige | Bedeutung |
|---|---|
| SUCHE STATION | Noch keine gültige Antwort empfangen |
| LIVE … Hz | Frische Messwerte; Zahl ist die gemessene Funkpaketrate am Wio |
| frei / Z:0 | Radar antwortet, meldet aber aktuell kein gültiges Ziel |
| RADAR OHNE DATEN | Funk funktioniert, aber die Radar-Messwerte fehlen oder sind veraltet |
| PAUSE … / START … | Gewünschter Zustand wurde noch nicht von der Station bestätigt |
| PAUSE | Zielübertragung pausiert; Statusabfragen laufen weiter |
| VERBINDUNG WEG | Im Live-Modus seit mindestens 0,5 Sekunden keine gültige Funkantwort; in Pause nach 2,5 Sekunden |
| FUNKFEHLER … | Initialisierung oder Übertragung fehlgeschlagen; automatischer Neuversuch |

Veraltete Zielpunkte werden nach spätestens 0,5 Sekunden ohne frische Messwerte ausgeblendet. `RX …ms` bzw. `RX …s` zeigt das Alter der letzten Funkantwort, nicht das Alter eines einzelnen Ziels. In Pause werden keine Positionsdaten übertragen; Radar und Heltec bleiben eingeschaltet. Beim Neustart des Wio ist die Übertragung wieder aktiv.

Die dritte Seite zeigt **Funk: Pak/s**, **Radar: Mess/s**, Empfangsstärke und das ungefähre Alter der Messwerte. Die Radarrate wird aus dem Messrahmenzähler der Station berechnet, nicht aus bewegten Bildpunkten. Beispiel: „Funk 20 / Radar 10“ bedeutet, dass die Funkverbindung schnell genug ist, aber der Sensor zehn neue Messrahmen pro Sekunde liefert. Nach Funkunterbrechungen oder beim Start ist diese kurze Durchschnittsmessung vorübergehend ungenau. Es werden keine zusätzlichen Positionen erfunden oder Bewegungen vorausberechnet.

## 5. Erster Funktionstest

1. Heltec einschalten: „Funk bereit“ und „RD03D: Daten OK“ prüfen. Ohne Wio steht „Warte auf Wio“.
2. Wio einschalten. Innerhalb weniger Sekunden sollte LIVE erscheinen.
3. In 1–3 m Entfernung vor dem fest montierten Radar seitlich bewegen. Einen Punkt erwarten; beim Wechsel nach links/rechts sollte er entsprechend wandern. Auf der dritten Wio-Seite die tatsächliche Funk- und Messrate prüfen. Zunächst mit wenigen Metern Abstand zwischen Wio und Heltec testen.
4. Zoom und Detailansicht ausprobieren. Mit Joystickdruck pausieren und wieder starten.
5. Zur Prüfung des Funkabbruchs Heltec-USB abziehen: Der Wio muss „VERBINDUNG WEG“ zeigen und die Punkte entfernen. Danach wieder anschließen.
6. Zur Prüfung eines Sensorfehlers zuerst ausschalten, Radar-TX trennen und erneut starten: Der Heltec und dann der Wio müssen fehlende Radardaten anzeigen. Anschließend ausgeschaltet wieder verbinden.

Der RD-03D verfolgt vor allem bewegte Ziele. Stationäre Personen können verschwinden. Spiegelflächen, Lüfter und Bewegung hinter dem Radar können Fehlziele verursachen. Das ist keine Lidar-Umgebungskarte und keine 360°-Messung.

## 6. Funk und technische Grenzen

- Direkte **GFSK-Verbindung**, kein Meshtastic, kein WLAN, kein Smartphone nötig. SX1262 unterstützt diesen Modus zusätzlich zu LoRa.
- **869,525 MHz**, 100 kbit/s, ±25 kHz Frequenzhub, Gaussian BT=0,5, 156,2 kHz Empfangsfilter, 14 dBm, 32-Bit-Präambel, vier Sync-Bytes, Whitening und 16-Bit-Hardware-CRC. Die als „868 MHz“ verkauften Geräte unterstützen diese EU-SRD-Frequenz.
- Wio fragt im **50-ms-Takt** an; das entspricht höchstens 20 Abfragen/s. Verpasste Zeitfenster lösen keine Sendebursts aus. In Pause erfolgt etwa jede Sekunde eine Statusabfrage.
- Ein Antwortpaket benötigt rechnerisch **3,76 ms** reine Sendezeit; inklusive angesetzter Anlaufreserve werden 4,16 ms verbucht. Bei 20 Antworten/s sind das **8,32 %**. Der Sender erzwingt zusätzlich mindestens 44 ms zwischen diesen Sendestarts. Die Rechnung umfasst Präambel, Synchronisation, Längenbyte und CRC.
- Die Frequenzplanung nutzt den 10-%-Bereich 869,4–869,65 MHz aus Band 54 der BNetzA-Verfügung 91/2025. Die elektrische/spektrale Umsetzung und reale Reichweite sind noch nicht vermessen. Die Firmware garantiert keine unterbrechungsfreie Echtzeitübertragung.
- Displayaktualisierungen werden am Wio erst nach einer Antwort ausgeführt, damit das OLED die kurze Empfangsphase nicht blockiert. Auf dem Heltec wird unmittelbar vor dem Antworten der neueste verfügbare Radarrahmen ausgewertet.
- Gemeinsame Paar-Kennung, Paketversion, Länge, Sequenz und Funk-CRC werden geprüft. **Keine Verschlüsselung oder kryptografische Authentifizierung.** Die Kennung verhindert zufällige Verwechslungen, ist kein Zugriffsschutz.
- Sensorwerte ohne Position, außerhalb 8 m, hinter der Sensorebene oder mit den Geschwindigkeits-Sentinelwerten 0/±248/±256 cm/s werden ausgefiltert, entsprechend dem dokumentierten ESPHome-Ansatz. Kein Personenklassifikator.
- GNSS, Bluetooth, Tiefschlaf und eine Akkuanzeige sind nicht implementiert. Die Akkulaufzeit des Wio im schnellen Modus ist noch nicht gemessen.

## 7. Selbst bauen

Voraussetzung: Python 3 und PlatformIO Core. Im Projektordner:

```powershell
pio run
python tools/package.py
```

Versionen sind in `platformio.ini` festgelegt. `include/Config.h` enthält Paar-Kennung, Funkparameter und Radar-GPIOs. Änderungen an gemeinsamen Funk-/Protokollwerten erfordern einen Neubau **beider** Geräte. Die eigene Wio-Boarddefinition nutzt eine eindeutige Nordic-Pinnummerierung: P0.n = n, P1.n = 32+n.

Die Tests in `tests/core_tests.cpp` verwenden denselben C++-Parser und dasselbe Funkprotokoll wie die Firmware. Details zu ausgeführten Prüfungen stehen in `VALIDIERUNG.md`.

### Aufbau des Repositorys

| Ordner / Datei | Inhalt |
|---|---|
| `src/station.cpp` | Heltec-Radarstation |
| `src/remote.cpp` | Wio-Anzeige und Bedienung |
| `include/` | Radarparser, Funkprotokoll und Zeitplanung |
| `boards/`, `variants/` | Wio-Boarddefinition und Pinbelegung |
| `firmware/` | Fertige Flash-Dateien und Prüfsummen |
| `tests/`, `tools/` | Kerntests und Firmware-Verpackung |
| `platformio.ini` | Board-Konfiguration und feste Abhängigkeitsversionen |

Build-Ausgaben und heruntergeladene Bibliotheken werden von Git ausgeschlossen. Die fertigen Dateien in `firmware/` werden mit versioniert, damit der funktionierende Stand direkt geflasht werden kann.

## Quellen

- [Heltec V3.2 Schaltplan](https://resource.heltec.cn/download/WiFi_LoRa_32_V3/WiFi_LoRa_32_V3.2_Schematic_Diagram.pdf): USB-5-V-Schiene, GPIOs, OLED und SX1262.
- [RD-03D Originaldatenblatt](https://en.ai-thinker.com/Uploads/file/20231016/20231016032622_13559.pdf): Seite 6 Versorgung/UART, Seite 15 3,3-V-IO.
- [ESPHome RD-03D](https://esphome.io/components/sensor/rd03d/) und [Parser-Quellcode](https://github.com/esphome/esphome/blob/dev/esphome/components/rd03d/rd03d.cpp): Datenformat, Vorzeichen, Einheiten und Sentinelwerte.
- [Seeed Wio L1](https://wiki.seeedstudio.com/wio_tracker_l1_node/) und [Meshtastic Boardbelegung](https://github.com/meshtastic/firmware/tree/develop/variants/nrf52840/seeed_wio_tracker_L1): OLED, Joystick, SX1262 und Empfangsverstärker.
- [CEPT ERC/REC 70-03](https://docdb.cept.org/document/845): SRD-Teilbänder und Sendezeitbedingungen.
- [BNetzA Vfg. 91/2025, Band 54](https://www.bundesnetzagentur.de/DE/Fachthemen/Telekommunikation/Frequenzen/Allgemeinzuteilungen/_DL/vfg91_2025.pdf?__blob=publicationFile&v=3): gewähltes Teilband und 10-%-Alternative.
- [Semtech SX1262](https://www.semtech.com/products/wireless-rf/lora-connect/sx1262): GFSK-Unterstützung des Funkchips.
- [Zephyr Wio-L1-Boarddefinition](https://github.com/zephyrproject-rtos/zephyr/blob/main/boards/seeed/wio_tracker_l1/wio_tracker_l1.dts): SH1106-OLED an I2C-Adresse 0x3D.
- [RadioLib](https://github.com/jgromes/RadioLib/tree/7.1.2), [Adafruit nRF52 Core](https://github.com/adafruit/Adafruit_nRF52_Arduino/tree/1.7.0), [UF2-Format](https://github.com/microsoft/uf2).
