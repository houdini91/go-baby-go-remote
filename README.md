# GoBabyGo Dual-Control Wireless Remote (R\&D)

**Objective**
Build a **dual-control** system for ride-on cars so a **child controller** (buttons/joystick) can drive while the **parent’s stock remote** retains full, immediate **override**—preserving all original safety behavior and requiring no changes to the car’s stock receiver.

---

## Current Status

**Phase:** Research in to reverse engenreing the RF protcol.
**Focus:** Decoding the stock RF protocol to enable safe emulation/mediation.

* Platform under test: **TX20 (remote) → RX23 (car)**, FCC ID **2AJ2H-TX10**
* Band/Modulation: **2.4 GHz**, suspected **GFSK** (bit rate **TBD**)
* RF modal with good probablity is panchip [XN297L](https://www.panchip.com/static/upload/file/20190916/1568621331607821.pdf)
* Tools: **HackRF**, **GNU Radio**, **Universal Radio Hacker (URH)**
* Progress:
  * ✅ Reliable captures of button-press bursts
  * 🔄 Tuning **samples-per-symbol (sps)** / bitrate to stabilize framing
  * 🔍 Identifying preamble/sync, payload layout, and CRC (in progress)

> Goal of this phase: confirm modulation/bitrate, extract a stable frame format, and map commands (FWD/REV/LEFT/RIGHT/STOP).

## ⚡️ RF Protocol Specification & Verified Command (as of 2025-09-19)
The following parameters have been confirmed via a successful transmission script `gfsk_tx20_rx23.py` that reliably controlled the car's receiver.

| Parameter                   | Value                                | Notes                          |
| --------------------------- | ------------------------------------ | ------------------------------ |
| Center Freq                 | `2.44388 GHz`                        | Matches URH/HackRF capture     |
| Sample Rate                 | `2.0 MS/s`                           | `SAMP_RATE = 2e6`              |
| Bitrate                     | `250 kbps`                           | `SAMP_RATE / SPS`              |
| SPS (samples/sym)           | `8`                                  | `SPS = 8`                      |
| Modulation                  | 2-FSK                                | Narrow-band GFSK-like          |
| FSK Tones                   | `F0 = 28320 Hz`, `F1 = 56641 Hz`     | Matches URH deviations         |
| HackRF Gains                | TX: `40`, IF: `21`, BB: `20`         | Script default                 |
| **TX Script Repeat Pattern**| **5 packets per group, 50 ms gap**   | How the script transmits       |
| **Stock Remote Cadence**    | **~83 packets/s (~12 ms start-to-start)** | While button held; each packet ~0.85–0.9 ms on-air |


> ℹ️ Note: While the stock remote likely uses GFSK (e.g., XN297L datasheet), our working GNU Radio transmission uses 2-FSK without shaping — and it successfully activates the car.

* **LEFT**: `gfsk_tx20_rx23.py "07ffffffffffffffffffffffffffffe3887aafda352d50a4119a"`
  **LEFT**: `gfsk_tx20_rx23.py "1fffffffffffffffffffffffffffffe3887aafda352d50c21dfa"` (second speed)


* **RIGHT** `gfsk_tx20_rx23.py "1fffffffffffffffffffffffffffffe3887aafda352d5125a302"`
  **RIGHT** `gfsk_tx20_rx23.py "1fffffffffffffffffffffffffffffe3887aafda352d5143af62"` (second speed)

* **FOWARD**: `gfsk_tx20_rx23.py "07ffffffffffffffffffffffffffffe3887aafda352d5262ce72"`
  **FOWARD**: `gfsk_tx20_rx23.py "07ffffffffffffffffffffffffffffe3887aafda352d5204c212"` (second speed)

* **BACKWARD**: `gfsk_tx20_rx23.py "1fffffffffffffffffffffffffffffe3887aafda352d54200c52"`

* **PARK**: `gfsk_tx20_rx23.py  "fffffffffffffffffffffffffffffe3887aafda352d501f072a"`

* **SPEED**: `gfsk_tx20_rx23.py "1fffffffffffffffffffffffffffffe3887aafda352d50428c72"`

## Proposed frame layout
[ PREAMBLE/PAD ]     variable  — runs of 0/1 (not part of logical payload)
[ SYNC / MAGIC ]     4 bytes   — constant per protocol (e3 88 7a af)
[ DEVICE ID ]        4 bytes   — constant for your car/remote (da 35 2d d5)
[ OPCODE ]           1 byte    — 0x50=LEFT, 0x51=RIGHT, 0x52=FWD, 0x54=BACK
[ CMD ]              2 bytes   — direction bits + SPEED (2 bits duplicated)
[ TAIL ]             2 bytes   — small check/CRC over the fields above

… e3 88 7a af | da 35 2d d5 | 50 | 0a 41 | 19 a0
  SYNC/MAGIC     DEVICE ID    OPC   CMD     TAIL

#### 🧩 `CMD` (2 bytes) — what we know so far
`CMD` is a 16-bit field immediately after the `OPCODE` (`0x5X`). Across all captures, changing **speed** flips the same four bits inside `CMD` while the rest stay direction-specific.

CMD[15..0] = b15 b14 b13 b12 b11 b10 b9 b8 b7 b6 b5 b4 b3 b2 b1 b0
- `S_hi = (CMD >> 9) & 0b11`
- `S_lo = (CMD >> 5) & 0b11`

**Observed invariant:** speed changes toggle both 2-bit fields together with the mask **`0x0660`**.  
That is, for the *same direction*:
CMD_speed_B = CMD_speed_A XOR 0x0660

### 📡 Packet (“burst”) cadence 
- **While the button is held:** the remote transmits the **drive command** packet repeatedly at ~**83 packets/s** (≈ **12 ms** start-to-start).
- **On release:** the payload **immediately switches to `PARK/NEUTRAL`**, but the remote **keeps transmitting at the same cadence** for a built-in **post-release dwell**, so a “short press” still shows ~**100 packets** in URH.

What that means in practice:

- The car **starts moving** as soon as it receives the first valid *drive* packet.
- The car **stops** shortly **after the last drive packet**, either because it receives *PARK* packets or because its internal **watchdog** (~0.1 s typical) expires.  
  The extra packets you see after release are mostly **PARK** and **don’t keep it moving**—they just ensure the stop command is delivered reliably.

time ──▶ [drive][drive][drive]........(release)→[PARK][PARK]...[PARK]

* **One line in URH = one packet (a.k.a. frame/burst).**
  A short press produced **\~102 packets over \~1.22 s** ⇒ **\~83 packets/s**.
* **Packet length (on-air):** \~**213 bits** ≈ **1700–1800 samples** at 2 MS/s, SPS = 8 → **\~0.85–0.90 ms**.
* **Symbol timing:** SPS = 8 @ 2 MS/s → **4 µs per symbol** (≈ 250 kb/s).
* **Start-to-start interval:** \~**11.9 ms**.
  **Inter-packet gap (silence):** \~**11.0–11.2 ms** (you see `Pause: ~22k samples` in URH).

> **Long press:** packets continue at \~**83 Hz** until release.


## How You Can Help

* Share short IQ captures of your **TX20/RX23** (or similar) with notes (frequency, sample rate, button pressed).
* Report hardware variants (photos/labels/PCBs).
* Open issues with any repeatable observations (idle beacons, pairing behavior, etc.).

![image 1](img/image1.jpg)
![image 2](img/image2.jpg)
![image 3](img/image3.jpg)
![image 4](img/image4.jpg)
![image 5](img/image5.jpg)
![image 6](img/image6.jpg)
![rec 1](img/rec1.png)
![rec 2](img/rec2.png)

---

## Links (repo)

* Google docs with some notes about the project -  https://docs.google.com/document/d/1At2ocUe9gaYEEyBYa_aoBxoMLpggaP__u1GeCZVrkBw/edit?usp=sharing

