# Baby Radar

Baby Radar is a dedicated radar system: **RD-03D connected to a Heltec WiFi LoRa 32 V3/V3.2**, with a **Wio Tracker L1 Pro with OLED** as the handheld display and controller. Both radio modules must be the EU868 versions. This firmware replaces Meshtastic.

Current firmware version: **2.1**. The firmware files and on-device startup messages use the original **RadarRemote** name.

**Status as of September 25, 2026:** The user flashed both devices and confirmed working displays, radio communication, and radar target display. Data processing was also checked with automated tests. Actual update rate, latency, and radio range have not been measured.

Version 2.1 uses the correct **SH1106** display driver on the Wio, probing address **0x3D** first and 0x3C as a fallback. The bootloader and successful transfer of the original application were verified on the connected Wio.

**Updating from 2.0: reflash the Wio only.** The Heltec image is unchanged and compatible. After flashing, the Wio should first show “RadarRemote 2.1 / Display OK”, followed by the radar view or “SUCHE STATION” (searching for station). **Do not delete files or format the Wio boot drive**; simply copy the new UF2 file onto it.

Version 2 uses **GFSK at 100 kbit/s** on the same radio chips. The Wio requests target positions every 50 ms: **up to 20 radio updates and 20 display frames per second**. This removes the previous delay of over one second. New position data is still limited by the radar's measurement rate; actual display frame rate and radio range have not been measured on the devices. Expect less radio range than with the slower LoRa mode.

**Upgrade both devices to version 2.** Versions 1 and 2 cannot communicate because they use different radio modes. Wiring is the same.

## 1. Wiring

Power the Heltec through USB-C only. The Wio uses its own power supply.

| RD-03D pin label | Heltec V3/V3.2 |
|---|---|
| 5V | 5V |
| GND | GND |
| TX | GPIO 4 |
| RX | GPIO 5 |

The numbers 4 and 5 are **GPIO numbers**, not physical header positions. RX and TX are crossed. RD-03D UART signals use 3.3 V logic; its power supply is 5 V. Do not power it from 3V3 or Vext. The USB supply must provide at least 200 mA for the radar in addition to the Heltec's requirements; a stable 5 V / 1 A supply provides headroom. Unplug USB before changing wiring. Connect a suitable LoRa antenna to the Heltec before powering it on.

The original RD-03D uses 256000 baud, 8N1. The firmware requests multi-target mode once after startup. The station displays “RD03D: Daten OK” (data OK) when it receives valid measurement frames.

## 2. Flashing the prebuilt firmware

Ready-to-flash files are in the [firmware](firmware) folder:

- [Heltec_Radarstation_merged.bin](firmware/Heltec_Radarstation_merged.bin) for Heltec V3/V3.2, flash address **0x0**.
- [Wio_RadarRemote.uf2](firmware/Wio_RadarRemote.uf2) for Wio Tracker L1 Pro.
- [SHA256SUMS.txt](firmware/SHA256SUMS.txt) contains checksums for both files.

On GitHub, download the actual file using “Download raw file”; do not save the HTML page. These binaries are the versions successfully used by the user on the working devices.

### Wio L1 Pro

1. Connect the Wio using a USB data cable.
2. Press Reset twice quickly to open the UF2 boot drive.
3. Check `INFO_UF2.TXT` to confirm that the board is a Wio Tracker L1. This package expects the standard L1 bootloader with **S140 7.3.0**. If the board or SoftDevice differs, first check the correct Seeed bootloader version; do not flash bootloaders intended for other boards.
4. Copy `firmware/Wio_RadarRemote.uf2` onto the boot drive. The device restarts.

The UF2 contains only the application starting at **0x27000**; it does not overwrite the SoftDevice or bootloader. It is not intended for the L1 E-Ink, T1000, or T114.

### Heltec V3/V3.2

`firmware/Heltec_Radarstation_merged.bin` is a **merged image** and must be written at **0x0**. It includes the bootloader, partition table, and application, replacing the previous application and partition layout.

Open the official [Espressif browser flasher](https://espressif.github.io/esptool-js/) in Chrome or Edge, connect to the Heltec's serial port, select the file, and enter `0x0` as the flash address. Reset the Heltec after writing. If connection fails, hold BOOT/USER, briefly press RESET, release BOOT/USER, and try connecting again.

If the Heltec display stays black after flashing, disconnect in the flasher, unplug and reconnect USB, then press RESET once without holding BOOT/USER. To isolate the problem, temporarily disconnect the radar while USB is unplugged. The Heltec should display its status even without the radar connected.

Alternatively, with PlatformIO installed, run this from the project folder:

```powershell
pio run -e heltec_station -t upload --upload-port COM7
```

Replace `COM7` with the Heltec's actual port. This method builds and uploads the individual components automatically.

## 3. Wio controls

| Control | Action |
|---|---|
| Joystick up | Zoom in: 8 → 4 → 2 m |
| Joystick down | Zoom out: 2 → 4 → 8 m |
| Joystick left/right | Select a detected target slot |
| Joystick press | Pause / resume target transmission |
| Separate menu/user button | Radar view → target details → radio/measurement rates → radar view |

The larger circle marks the selected target. The four range rings divide the displayed maximum distance into equal intervals. The origin at the bottom represents the radar sensor; the top represents the area in front of it. Positive X values are to the sensor's right. Moving or rotating the Wio does not change this frame of reference.

The details view shows distance, angle, and signed radial speed. Slots 1–3 come from the sensor and are **not persistent person identities**. Targets outside the selected zoom range are not drawn, but still count toward `Z`, the target count. `S` identifies the selected slot.

## 4. Understanding the status display

The current firmware displays German status messages. The table below gives their English meanings.

| Display message | Meaning |
|---|---|
| SUCHE STATION | Searching for station; no valid reply received yet |
| LIVE … Hz | Fresh measurements; the number is the radio packet rate measured by the Wio |
| frei / Z:0 | Clear: radar is responding but currently reports no valid targets |
| RADAR OHNE DATEN | Radio communication works, but radar measurements are missing or stale |
| PAUSE … / START … | The station has not yet confirmed the requested state |
| PAUSE | Target transmission is paused; status polling continues |
| VERBINDUNG WEG | Connection lost: no valid reply for at least 0.5 seconds in live mode or 2.5 seconds while paused |
| FUNKFEHLER … | Radio initialization or transmission failed; retrying automatically |

Stale target points disappear after at most 0.5 seconds without fresh measurements. `RX …ms` or `RX …s` shows the age of the last radio reply, not the age of an individual target. No positions are transmitted while paused; the radar and Heltec remain powered. Restarting the Wio resumes transmission.

The third page shows **Funk: Pak/s** (radio packets per second), **Radar: Mess/s** (radar measurement frames per second), received signal strength, and approximate measurement age. The radar rate is calculated from the station's measurement frame counter, not from moving pixels. For example, “Funk 20 / Radar 10” means that the radio link is fast enough, but the sensor supplies ten new measurement frames per second. This short averaging window can temporarily be inaccurate after startup or a radio interruption. No extra positions are generated and no movement is extrapolated.

## 5. First functional check

1. Power on the Heltec and look for “Funk bereit” (radio ready) and “RD03D: Daten OK” (radar data OK). Without the Wio, it displays “Warte auf Wio” (waiting for Wio).
2. Power on the Wio. LIVE should appear within a few seconds.
3. Move sideways 1–3 m in front of the securely mounted radar. A target point should appear and move left or right accordingly. Check the actual radio and measurement rates on the Wio's third page. Start with only a few metres between the Wio and Heltec.
4. Try zoom and the details view. Press the joystick to pause and resume.
5. Test radio loss by unplugging the Heltec's USB cable: the Wio should show “VERBINDUNG WEG” and remove the points. Reconnect afterward.
6. Test a sensor failure by powering off, disconnecting radar TX, and restarting: the Heltec, followed by the Wio, should report missing radar data. Power off again before reconnecting the wire.

The RD-03D mainly tracks moving targets. Stationary people may disappear. Reflective surfaces, fans, and movement behind the radar can produce false targets. This is not a lidar map or a 360° scan.

## 6. Radio and technical limits

- Direct **GFSK link**; no Meshtastic, Wi-Fi, or smartphone is required. The SX1262 supports this mode in addition to LoRa.
- **869.525 MHz**, 100 kbit/s, ±25 kHz frequency deviation, Gaussian BT=0.5, 156.2 kHz receive filter, 14 dBm, 32-bit preamble, four sync bytes, whitening, and 16-bit hardware CRC. The devices sold as “868 MHz” support this EU SRD frequency.
- The Wio polls every **50 ms**, up to 20 requests per second. Missed time slots do not cause catch-up bursts. While paused, it polls for status approximately once per second.
- A reply has a calculated transmission time of **3.76 ms**; with the startup allowance, the firmware accounts for 4.16 ms. At 20 replies per second, this is **8.32%**. The transmitter also enforces at least 44 ms between these transmission starts. The calculation includes preamble, synchronization, length byte, and CRC.
- The frequency plan uses the 10% duty-cycle option in the 869.4–869.65 MHz range, band 54 of BNetzA General Assignment 91/2025. Electrical and spectral behavior and actual range have not been measured. The firmware does not guarantee uninterrupted real-time delivery.
- The Wio updates its display after receiving a reply so OLED work does not block the short receive window. The Heltec processes the latest available radar frame immediately before replying.
- The pair identifier, packet version, length, sequence number, and radio CRC are checked. **There is no encryption or cryptographic authentication.** The identifier prevents accidental mix-ups; it does not provide access control.
- Readings without a position, beyond 8 m, behind the sensor plane, or with speed sentinel values of 0/±248/±256 cm/s are filtered out, following the documented ESPHome approach. There is no person classifier.
- GNSS, Bluetooth, deep sleep, and a battery indicator are not implemented. Wio battery life in this fast mode has not been measured.

## 7. Building from source

Requirements: Python 3 and PlatformIO Core. Run from the project folder:

```powershell
pio run
python tools/package.py
```

Dependency versions are pinned in `platformio.ini`. `include/Config.h` contains the pair identifier, radio parameters, and radar GPIO assignments. Changing shared radio or protocol settings requires rebuilding **both** devices. The custom Wio board definition uses direct Nordic pin numbering: P0.n = n, P1.n = 32+n.

The tests in `tests/core_tests.cpp` use the same C++ parser and radio protocol as the firmware. See [VALIDATION.md](VALIDATION.md) for details of the checks performed.

### Repository layout

| Folder / file | Contents |
|---|---|
| `src/station.cpp` | Heltec radar station |
| `src/remote.cpp` | Wio display and controls |
| `include/` | Radar parser, radio protocol, and timing |
| `boards/`, `variants/` | Wio board definition and pin assignments |
| `firmware/` | Prebuilt firmware and checksums |
| `tests/`, `tools/` | Core tests and firmware packaging |
| `platformio.ini` | Board configuration and pinned dependencies |

Build output and downloaded libraries are excluded from Git. The prebuilt files in `firmware/` are versioned so the working version can be flashed directly.

## Sources

- [Heltec V3.2 schematic](https://resource.heltec.cn/download/WiFi_LoRa_32_V3/WiFi_LoRa_32_V3.2_Schematic_Diagram.pdf): USB 5 V rail, GPIOs, OLED, and SX1262.
- [Original RD-03D datasheet](https://en.ai-thinker.com/Uploads/file/20231016/20231016032622_13559.pdf): page 6 for power/UART, page 15 for 3.3 V I/O.
- [ESPHome RD-03D](https://esphome.io/components/sensor/rd03d/) and [parser source](https://github.com/esphome/esphome/blob/dev/esphome/components/rd03d/rd03d.cpp): data format, signs, units, and sentinel values.
- [Seeed Wio L1](https://wiki.seeedstudio.com/wio_tracker_l1_node/) and [Meshtastic board definitions](https://github.com/meshtastic/firmware/tree/develop/variants/nrf52840/seeed_wio_tracker_L1): OLED, joystick, SX1262, and receive amplifier.
- [CEPT ERC/REC 70-03](https://docdb.cept.org/document/845): SRD sub-bands and airtime conditions.
- [BNetzA General Assignment 91/2025, band 54](https://www.bundesnetzagentur.de/DE/Fachthemen/Telekommunikation/Frequenzen/Allgemeinzuteilungen/_DL/vfg91_2025.pdf?__blob=publicationFile&v=3): selected sub-band and 10% duty-cycle option.
- [Semtech SX1262](https://www.semtech.com/products/wireless-rf/lora-connect/sx1262): radio chip GFSK support.
- [Zephyr Wio L1 board definition](https://github.com/zephyrproject-rtos/zephyr/blob/main/boards/seeed/wio_tracker_l1/wio_tracker_l1.dts): SH1106 OLED at I2C address 0x3D.
- [RadioLib](https://github.com/jgromes/RadioLib/tree/7.1.2), [Adafruit nRF52 Core](https://github.com/adafruit/Adafruit_nRF52_Arduino/tree/1.7.0), [UF2 format](https://github.com/microsoft/uf2).
