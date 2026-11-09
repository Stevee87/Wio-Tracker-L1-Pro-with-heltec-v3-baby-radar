#!/usr/bin/env python3
"""Build the US 915 MHz / English firmware variants from the upstream EU868 German binaries.

Usage (from the repository root):
    python3 tools/patch_us915_english.py

Reads  firmware/Heltec_Radarstation_merged.bin and firmware/Wio_RadarRemote.uf2
Writes firmware/us915_english/Heltec_Radarstation_EN_915.bin
       firmware/us915_english/Heltec_Radarstation_EN_915_RX5TX4.bin  (sensor TX->GPIO5, RX->GPIO4)
       firmware/us915_english/Wio_RadarRemote_EN_915.uf2

What it changes
  * Every German display string is replaced in place by an English string of equal or
    shorter length (null padded), so no code or layout moves.
  * The RadioLib FSK carrier frequency constant 869.525f is replaced by 915.0f
    (once in the Heltec image, twice in the Wio image).
  * The ESP32-S3 app image checksum and appended SHA-256 are recomputed so the
    bootloader accepts the modified image. The UF2 is rebuilt block for block.
  * The RX5TX4 variant additionally swaps the two pin immediates in the
    HardwareSerial::begin(256000, SERIAL_8N1, rx=4, tx=5) call.
"""
import hashlib, os, struct, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from uf2tool import uf2_to_bin, bin_to_uf2

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FW = os.path.join(ROOT, 'firmware')
OUT = os.path.join(FW, 'us915_english')
OLD_F, NEW_F = struct.pack('<f', 869.525), struct.pack('<f', 915.0)

HELTEC = [("Funk bereit", "Radio ready"), ("FUNKFEHLER ", "RADIO FAIL "), ("RD03D: Daten OK", "RD03D: Data OK"),
          ("RD03D: KEINE DATEN", "RD03D: NO DATA"), ("Warte auf Wio", "Wait for Wio"),
          ("Wio: verbunden", "Wio: connected"), ("Ziele: ", "Tgts: ")]
WIO = [("Funk startet ...", "Radio start ..."), ("SUCHE STATION", "SEARCHING..."), ("VERBINDUNG WEG", "LINK LOST"),
       ("RADAR OHNE DATEN", "RADAR: NO DATA"), ("Funk: ", "RF: "), (" Pak/s", " pkt/s"), (" Mess/s", " meas/s"),
       ("Messalter: ", "Data age: "), ("Zielslot ", "Slot "), ("Distanz ", "Dist "), ("Tempo ", "Speed "),
       ("Winkel ", "Angle "), (" Grad", " deg"), ("Keine aktuellen Ziele", "No current targets"), ("frei", "none"),
       ("Klick: Start", "Click: Start"), ("Klick: Pause", "Click: Pause"), ("FUNKFEHLER ", "RADIO FAIL ")]


def patch_strings(buf, table):
    for old, new in table:
        o, n = old.encode(), new.encode()
        assert len(n) <= len(o), f'too long: {new!r} > {old!r}'
        pat, idx, i = o + b'\0', [], buf.find(o + b'\0')
        while i != -1:
            if i == 0 or not (0x20 <= buf[i - 1] <= 0x7e):
                idx.append(i)
            i = buf.find(pat, i + 1)
        assert len(idx) == 1, f'{old!r}: found {len(idx)} times'
        buf[idx[0]:idx[0] + len(o)] = n + b'\0' * (len(o) - len(n))


def patch_freq(buf, expect):
    idx, i = [], buf.find(OLD_F)
    while i != -1:
        idx.append(i); i = buf.find(OLD_F, i + 1)
    assert len(idx) == expect, idx
    for i in idx:
        buf[i:i + 4] = NEW_F


def fix_esp_image(app):
    """Recompute the ESP32 image XOR checksum and appended SHA-256 in place."""
    assert app[0] == 0xE9
    nseg, pos, cs = app[1], 24, 0xEF
    for _ in range(nseg):
        _, ln = struct.unpack('<II', app[pos:pos + 8]); pos += 8
        for b in app[pos:pos + ln]:
            cs ^= b
        pos += ln
    cs_pos = ((pos + 16) // 16) * 16 - 1
    assert cs_pos + 1 + 32 == len(app), 'unexpected image footer layout'
    app[cs_pos] = cs
    app[cs_pos + 1:] = hashlib.sha256(app[:cs_pos + 1]).digest()


def build_heltec(swap_pins):
    merged = bytearray(open(os.path.join(FW, 'Heltec_Radarstation_merged.bin'), 'rb').read())
    APP = 0x10000
    app = bytearray(merged[APP:])
    patch_strings(app, HELTEC)
    patch_freq(app, 1)
    if swap_pins:
        IROM_VADDR, IROM_FILE = 0x42000020, 0x20018
        off = lambda va: va - IROM_VADDR + IROM_FILE
        # movi.n a14,5 -> movi.n a14,4 ; movi.n a13,4 -> movi.n a13,5  (args to HardwareSerial::begin)
        for va, old, new in [(0x42002174, b'\x0c\x5e', b'\x0c\x4e'), (0x42002178, b'\x0c\x4d', b'\x0c\x5d')]:
            o = off(va); assert app[o:o + 2] == old, hex(o); app[o:o + 2] = new
        assert app[off(0x4200216f):off(0x4200216f) + 3] == bytes.fromhex('b1e0f7')  # l32r of 256000 baud
        s = b'RD03D RX=4 TX=5'; i = app.find(s); assert i != -1 and app.find(s, i + 1) == -1
        app[i:i + len(s)] = b'RD03D RX=5 TX=4'
    fix_esp_image(app)
    merged[APP:] = app
    return bytes(merged)


def build_wio():
    src = os.path.join(FW, 'Wio_RadarRemote.uf2')
    b, base, flags, fam, _ = uf2_to_bin(src)
    assert bin_to_uf2(b, base, flags, fam) == open(src, 'rb').read(), 'UF2 round-trip mismatch'
    wio = bytearray(b)
    patch_strings(wio, WIO)
    patch_freq(wio, 2)
    return bin_to_uf2(bytes(wio), base, flags, fam)


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    for name, data in [('Heltec_Radarstation_EN_915.bin', build_heltec(False)),
                       ('Heltec_Radarstation_EN_915_RX5TX4.bin', build_heltec(True)),
                       ('Wio_RadarRemote_EN_915.uf2', build_wio())]:
        p = os.path.join(OUT, name)
        open(p, 'wb').write(data)
        print(f'wrote {p} ({len(data)} bytes, sha256 {hashlib.sha256(data).hexdigest()[:16]}...)')
