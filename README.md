# Baby Radar

A wireless radar display using an **RD-03D sensor connected to a Heltec WiFi LoRa 32 V3/V3.2** and a **Wio Tracker L1 Pro with OLED** as the handheld controller. Both devices must be the EU868 versions. This firmware replaces Meshtastic.

**[Go to the flashing instructions](#flashing-instructions).**

This repository contains the ready-to-flash firmware, this guide, and the [MIT License](LICENSE).

| File | Purpose |
|---|---|
| `firmware/Heltec_Radarstation_merged.bin` | Heltec radar station, version 2.0 |
| `firmware/Wio_RadarRemote.uf2` | Wio display and controller, version 2.1 |
| `README.md` | Wiring, flashing, controls, and troubleshooting |
| `LICENSE` | MIT license for Baby Radar's original project content |

The supplied Heltec and Wio versions work together. Startup messages still use the original **RadarRemote** name. Working displays, radio communication, and target detection were confirmed on the physical setup. The target update rate is up to 20 Hz; actual rate, latency, and range have not been measured.

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

<a id="flashing-instructions"></a>

## 2. Flashing instructions

For the first setup, flash **both devices** using the files supplied in this repository. No compilation or Arduino IDE is required.

### Step 1: Download and extract the files

1. On the GitHub repository page, select **Code → Download ZIP**. If you already have `Baby-Radar-GitHub.zip`, use that archive.
2. Extract the ZIP completely before selecting firmware files.
3. Open the extracted project's `firmware` folder.
4. Match each file to its device:

| Device | Firmware file | Flashing method |
|---|---|---|
| Heltec WiFi LoRa 32 V3/V3.2 | [Heltec_Radarstation_merged.bin](firmware/Heltec_Radarstation_merged.bin) | Browser flasher, address **0x0** |
| Wio Tracker L1 Pro | [Wio_RadarRemote.uf2](firmware/Wio_RadarRemote.uf2) | Copy onto the Wio's USB boot drive |

You can also download either firmware file individually using GitHub's **Download raw file** button. Download the actual binary, not the HTML page. These are the same binaries used in the working hardware setup.

Use a **USB data cable**, not a charge-only cable. Connect one device at a time while flashing to make port selection easier. Connect the Heltec's antenna before powering it on. You may leave the radar disconnected until both firmware installations are complete; always unplug USB before changing radar wiring.

### Step 2: Flash the Heltec V3/V3.2

1. Connect the Heltec to the computer with its USB-C data cable.
2. Open the official [Espressif browser flasher](https://espressif.github.io/esptool-js/) in desktop **Chrome or Edge**.
3. Close any other serial monitor or flasher using the Heltec's port.
4. Click **Connect** in the flasher's programming section.
5. Select the Heltec's serial port. On Windows it usually appears as **Silicon Labs CP210x USB to UART Bridge (COM...)**. The COM number depends on your computer.
6. Check the connection log: the detected chip must be **ESP32-S3**.
7. In the file row, choose `Heltec_Radarstation_merged.bin` from the extracted `firmware` folder.
8. Set **Flash Address** to **`0x0`**. Use one file row for this merged image. It already includes the bootloader, partition table, and application.
9. Where the flasher offers these settings, use:

| Setting | Value |
|---|---|
| Flash Address | **`0x0`** |
| Flash Mode | **DIO** |
| Flash Frequency | **80 MHz** |
| Flash Size | **8 MB** |

10. Click **Program** and wait until writing and verification finish successfully. Keep USB connected throughout the operation.
11. Click **Disconnect**, unplug USB, and reconnect it. If necessary, briefly press **RST/RESET** once, without holding BOOT/USER.
12. Check the Heltec display: it should show **`RADARSTATION 2.0`**. This is the correct Heltec version for the package; version 2.1 changed only the Wio display driver.

**The merged BIN must be flashed at `0x0`, not `0x10000`.** Flashing this image replaces the previous application and partition layout. A separate full-chip erase is not part of the normal procedure.

If the flasher cannot connect: hold **BOOT/USER**, briefly press **RESET**, release **BOOT/USER**, then try **Connect** again. After successful programming, start normally with RESET or a USB power cycle.

If no Heltec serial port appears, try another data cable or USB port. On Windows, check whether the [official Silicon Labs CP210x VCP driver](https://www.silabs.com/software-and-tools/usb-to-uart-bridge-vcp-drivers) is installed.

### Step 3: Flash the Wio Tracker L1 Pro

1. Connect the Wio to the computer with a USB data cable and switch it on.
2. Press **RESET twice quickly** to enter the UF2 bootloader.
3. Open the newly appearing USB drive in File Explorer or your operating system's file manager. The drive name and letter may vary. It normally contains files such as `INFO_UF2.TXT` and `CURRENT.UF2`.
4. Open `INFO_UF2.TXT` and check the board and SoftDevice. The unit used for this project reports **TRACKER L1** and **S140 7.3.0**. This application expects that SoftDevice version. If the reported board or SoftDevice differs, check compatibility before flashing.
5. Copy **`Wio_RadarRemote.uf2`** from the extracted `firmware` folder directly into the root of this USB drive.
6. Wait for copying to finish. The boot drive normally disappears as the Wio restarts. Do not unplug it during the copy.
7. Check the display: it should briefly show **`RadarRemote 2.1` / `Display OK`**, then the radar view. **`SUCHE STATION`** means “searching for station” and is expected until the Heltec is running.

**Do not delete the files on the boot drive and do not format it.** No flash address needs to be entered for the Wio: the UF2 already contains the application addresses. Use the UF2 file, not the Heltec BIN or the repository ZIP.

This UF2 writes only the application starting at **0x27000**; it does not overwrite the SoftDevice or bootloader. It is intended for the **Wio Tracker L1 Pro with OLED**, not the L1 E-Ink, T1000, or T114. See [Seeed's Wio L1 flashing guide](https://wiki.seeedstudio.com/get_started_with_meshtastic_wio_tracker_l1/) for the board's USB/DFU procedure; for Baby Radar, copy the UF2 supplied here.

If the boot drive does not appear, confirm that the Wio is switched on, try another USB data cable or USB port, and double-press RESET again.

### Step 4: Connect the radar and check the link

1. Unplug the Heltec's USB cable.
2. Connect RD-03D **5V → 5V**, **GND → GND**, **TX → GPIO 4**, and **RX → GPIO 5** on the Heltec. GPIO numbers are not physical header positions.
3. Reconnect Heltec USB and power on the Wio.
4. Check the displays:

| Device | Expected message | Meaning |
|---|---|---|
| Heltec | `Funk bereit` | Radio initialized |
| Heltec | `RD03D: Daten OK` | Valid radar measurements received |
| Heltec | `Wio: verbunden` | Wio requests received |
| Wio | `LIVE ... Hz` | Fresh radar data received over the radio |

The supplied files use the same radio settings and pair identifier, so no manual pairing is required. Move 1–3 m in front of the radar to check target detection.

### Flashing troubleshooting

| Symptom | What to check |
|---|---|
| Heltec display stays black after programming | Disconnect in the flasher, unplug and reconnect USB, then press RESET without holding BOOT. If it stays black, unplug USB and temporarily disconnect the radar, then test the Heltec alone. It should show a status screen even without radar data. |
| Heltec flasher reports a busy port or access denied | Disconnect other browser flashers and close serial monitors, then reconnect. |
| Wio stays black after copying the file | Double-press RESET again and copy this repository's version 2.1 `Wio_RadarRemote.uf2`. Version 2.0 used the wrong Wio display driver. |
| Wio displays `SUCHE STATION` | Confirm that the Heltec has started and that both devices use this package's firmware. Check the Heltec antenna and test the devices a few metres apart. |
| Heltec displays `RD03D: KEINE DATEN`, or Wio displays `RADAR OHNE DATEN` | Check radar power, common GND, and crossed TX/RX wiring while USB is unplugged. Radar TX must connect to Heltec GPIO 4. |
| Wio shows `LIVE` but no targets | Move 1–3 m in front of the radar; stationary people may disappear. Check the selected zoom range. |

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

## 5. Technical notes

- Direct GFSK radio at **869.525 MHz**, 100 kbit/s and 14 dBm. No phone, Wi-Fi, or Meshtastic connection is needed.
- The Wio polls every **50 ms**. Fresh positions are limited by the radar's measurement rate; movement is not extrapolated.
- The RD-03D primarily tracks moving targets. Stationary people can disappear; fans and reflections may produce false targets. This is not a lidar map or a 360° scanner.
- The display supports up to three sensor target slots. Slots do not permanently identify people.
- Radio range, battery life, spectral behavior, and end-to-end latency have not been measured.
- The shared pair identifier filters packets but provides no encryption or cryptographic authentication.

## License

Baby Radar's original application code and documentation are licensed under the [MIT License](LICENSE), copyright 2026 Baby Radar contributors.

The firmware includes third-party components that retain their own licenses. These include [RadioLib 7.1.2](https://github.com/jgromes/RadioLib/tree/7.1.2), Adafruit display and support libraries, [Arduino-ESP32 2.0.17](https://github.com/espressif/arduino-esp32/tree/2.0.17), and [Adafruit nRF52 Arduino Core 1.7.0](https://github.com/adafruit/Adafruit_nRF52_Arduino/tree/1.7.0). The MIT license for Baby Radar does not replace their licenses.

<details>
<summary>Radio and display library copyright notices</summary>

### RadioLib 7.1.2

```text
MIT License

Copyright (c) 2018 Jan Gromeš

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### Adafruit SH110X

```text
Software License Agreement (BSD License)

Copyright (c) 2012, Adafruit Industries
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
1. Redistributions of source code must retain the above copyright
notice, this list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright
notice, this list of conditions and the following disclaimer in the
documentation and/or other materials provided with the distribution.
3. Neither the name of the copyright holders nor the
names of its contributors may be used to endorse or promote products
derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS ''AS IS'' AND ANY
EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
```

### Adafruit SSD1306

```text
Software License Agreement (BSD License)

Copyright (c) 2012, Adafruit Industries
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
1. Redistributions of source code must retain the above copyright
notice, this list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright
notice, this list of conditions and the following disclaimer in the
documentation and/or other materials provided with the distribution.
3. Neither the name of the copyright holders nor the
names of its contributors may be used to endorse or promote products
derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS ''AS IS'' AND ANY
EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
```

### Adafruit GFX Library

```text
Software License Agreement (BSD License)

Copyright (c) 2012 Adafruit Industries.  All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

- Redistributions of source code must retain the above copyright notice,
  this list of conditions and the following disclaimer.
- Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
```

### Adafruit BusIO

```text
The MIT License (MIT)

Copyright (c) 2017 Adafruit Industries

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

</details>
