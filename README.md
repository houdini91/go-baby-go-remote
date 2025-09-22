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

# RX23 - TX20
Remote Analysis paired with RX23 protcol.

> Note TX20 Remote seems to support the new RX75 Model as well depending on who it pairs with.

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

### Raw Packets capture

* **LEFT**:
  * 1fffffffffffffffffffffffffffffe3887aafda352d50c21dfa8 (speed 1)
  * 1fffffffffffffffffffffffffffffe3887aafda352d50a4119a8 (speed 2)
  * 1fffffffffffffffffffffffffffffe3887aafda352d50e019da8 (speed 3)
 
* **RIGHT**:
  * 1fffffffffffffffffffffffffffffe3887aafda352d5143af628 (speed 1)
  * 1fffffffffffffffffffffffffffffe3887aafda352d5125a3028 (speed 2)
  * 1fffffffffffffffffffffffffffffe3887aafda352d5161ab428 (speed 3)

* **FOWARD**: 
  * 1fffffffffffffffffffffffffffffe3887aafda352d5240ca528 (speed 1)
  * 1fffffffffffffffffffffffffffffe3887aafda352d5226c6328 (speed 2)
  * 1fffffffffffffffffffffffffffffe3887aafda352d5262ce728 (speed 3)
    
  > ODD BALL CAPTURE - 07ffffffffffffffffffffffffffffe3887aafda352d5204c212 ?? NOT SURE WHERE THIS CAME FROM BUT I RECORDED IT (maybe different error tollerance)

* **BACKWARD**: the
    * 1fffffffffffffffffffffffffffffe3887aafda352d544600328 (speed 1)
    * 1fffffffffffffffffffffffffffffe3887aafda352d54200c528 (speed 2)
    * 1fffffffffffffffffffffffffffffe3887aafda352d546404128 (speed 3)

* **PARK**:
  * 1fffffffffffffffffffffffffffffe3887aafda352d501f072a8

* **SPEED**:
  * 1fffffffffffffffffffffffffffffe3887aafda352d502480128 (change speed from 1 - 2)
  * 1fffffffffffffffffffffffffffffe3887aafda352d506088528 (change speed from 2 - 3)
  * 1fffffffffffffffffffffffffffffe3887aafda352d50428c728 (change speed from 3 - 1)

* **LEFT + FOWARD**:
  * 0fffffffffffffffffffffffffffffe3887aafda352d52c05bda8 (speed 1)
  * 0fffffffffffffffffffffffffffffe3887aafda352d52a657ba8 (speed 3)
  * 0fffffffffffffffffffffffffffffe3887aafda352d52e25ffa8 (speed 3)

* **RIGHT + FOWARD**:
  * 1fffffffffffffffffffffffffffffe3887aefda352d5341e9428 (speed 1)
  * 1fffffffffffffffffffffffffffffe3887aafda352d5327e5228 (speed 2) ?? CMD=57 should b3..
  * 0fffffffffffffffffffffffffffffe3887aafda352d5363ed628 (speed 3)

* **LEFT + BACKWARD**:
  * 0fffffffffffffffffffffffffffffe3887aafda352d54c691ba8 (speed 1)
  * 0fffffffffffffffffffffffffffffe3887aafda352d54a09dda8 (speed 2)
  * 0fffffffffffffffffffffffffffffe3887aafda352d54e4959a8 (speed 3)

* **RIGHT + BACKWARD**:
  * 0fffffffffffffffffffffffffffffe3887aafda352d554723228 (speed 1)2
  * 1fffffffffffffffffffffffffffffe3887aafda352d55212f428 (speed 2)
  * 1fffffffffffffffffffffffffffffe3887aafda352d556527028 (speed 3)
  
* **PAIR**: TBD still under investigation
  * Remote pairing mode - Sends signal on a slightly different channel 2.439,
    also seems burst is slower rate.

    `ffffffffffffffffffffffffffffffe3887aae66666528c65da5428`

  * CAR SEND TDB????

  * Remote Led show pair is complete.
    At the end of the pairing the remote sends burst at "speed" packet on the normal data channel 2.444

    `ffffffffffffffffffffffffffffffe3887aafda352d702480128`

## Frame layout assumption (sep 20) 

| Field        | Size     | Example (Hex) | Notes                                                               |
| ------------ | -------- | ------------- | ------------------------------------------------------------------- |
| PREAMBLE/PAD | variable | `…`           | Run of 1s (or 0s) for synchronization; not part of logical payload. |
| SYNC / MAGIC | 4 bytes  | `e3 88 7a af` | Fixed protocol sync header.                                         |
| DEVICE ID    | 3 bytes  | `da 35 2d`    | Constant per remote/car pair (your car’s ID).                       |
| OPCODE       | 1 byte   | `50`          | `0x50=LEFT / PARK / SPEED`, `0x51=RIGHT`, `0x52=FWD,LEFT+FWD`, `0x54=BACK,LEFT+BACK` `0x55=RIGHT+BACK` `0x53=RIGHT+FWD` |
| CMD          | 1 bytes  | `a4`       | Direction + speed bits. Some mirrored.                              |
| TAIL         | 2 byte   | `11 9a`          | Likely checksum or CRC over previous 

### Single‑button

| Action   | Speed | OP | CMD | TAIL  | Steer flags (`b7`,`b0`) |
| -------- | ----- | -- | --- | ----- | ----------------------- |
| LEFT     | 1     | 50 | c2  | 1d fa | `1,0`                   |
| LEFT     | 2     | 50 | a4  | 11 9a | `1,0`                   |
| LEFT     | 3     | 50 | e0  | 19 da | `1,0`                   |
| RIGHT    | 1     | 51 | 43  | af 62 | `0,1`                   |
| RIGHT    | 2     | 51 | 25  | a3 02 | `0,1`                   |
| RIGHT    | 3     | 51 | 61  | ab 42 | `0,1`                   |
| FORWARD  | 1     | 52 | 40  | ca 52 | `0,0`                   |
| FORWARD  | 2     | 52 | 22  | 6c 63 | `0,0`                   |
| FORWARD  | 3     | 52 | 62  | ce 72 | `0,0`                   |
| BACKWARD | 1     | 54 | 46  | 00 32 | `0,0`                   |
| BACKWARD | 2     | 54 | 20  | 0c 52 | `0,0`                   |
| BACKWARD | 3     | 54 | 64  | 04 12 | `0,0`                   |

### Dual‑button packets

Absolutely—here’s the completed, cleaned-up table with your latest captures, including **RIGHT+FORWARD**. I’ve kept the same columns and added the new rows. (Reminder: **CMD** here is the first byte after OP—i.e., `CMD_hi`. The two bytes in **TAIL** are the checksum/CRC right before the common trailer `0x28`.)

### Dual‑button packets

| Action           | Speed | OP | CMD      | TAIL  | Steer flags (`b7`,`b0`) | Relation to straight drive                                 |
| ---------------- | ----- | -- | -------- | ----- | ----------------------- | ---------------------------------------------------------- |
| LEFT + FORWARD   | 1     | 52 | **c0**   | 5b da | `b7=1, b0=0`            | `0x40 (FWD s1)` \| `0x80` = **0xC0**                       |
| LEFT + FORWARD   | 2     | 52 | **a6**\* | 57 ba | `b7=1, b0=0`            | expected `0x22 \| 0x80 = 0xA2`; seen **0xA6** (+`b2`) (\*) |
| LEFT + FORWARD   | 3     | 52 | **e2**   | 5f fa | `b7=1, b0=0`            | `0x62 (FWD s3)` \| `0x80` = **0xE2**                       |
| LEFT + BACKWARD  | 1     | 54 | **c6**   | 91 ba | `b7=1, b0=0`            | `0x46 (BACK s1)` \| `0x80` = **0xC6**                      |
| LEFT + BACKWARD  | 2     | 54 | **a0**   | 9d da | `b7=1, b0=0`            | `0x20 (BACK s2)` \| `0x80` = **0xA0**                      |
| LEFT + BACKWARD  | 3     | 54 | **e4**   | 95 9a | `b7=1, b0=0`            | `0x64 (BACK s3)` \| `0x80` = **0xE4**                      |
| RIGHT + BACKWARD | 1     | 55 | **47**   | 23 22 | `b7=0, b0=1`            | `0x46 (BACK s1)` \| `0x01` = **0x47**                      |
| RIGHT + BACKWARD | 2     | 55 | **21**   | 2f 42 | `b7=0, b0=1`            | `0x20 (BACK s2)` \| `0x01` = **0x21**                      |
| RIGHT + BACKWARD | 3     | 55 | **65**   | 27 02 | `b7=0, b0=1`            | `0x64 (BACK s3)` \| `0x01` = **0x65**                      |
| RIGHT + FORWARD  | 1     | 53 | **41**   | e9 42 | `b7=0, b0=1`            | `0x40 (FWD s1)` \| `0x01` = **0x41**                       |
| RIGHT + FORWARD  | 2     | 53 | **27**\* | e5 22 | `b7=0, b0=1`            | expected `0x22 \| 0x01 = 0x23`; seen **0x27** (+`b2`) (\*) |
| RIGHT + FORWARD  | 3     | 53 | **63**   | ed 62 | `b7=0, b0=1`            | `0x62 (FWD s3)` \| `0x01` = **0x63**                       |

> The **`+b2`** anomaly (extra bit 2 set) shows up in some **speed‑2 diagonal with FWD** packets (e.g., `0xA6` vs. expected `0xA2`, and `0x27` vs. `0x23`). Everything else matches the rule:

#### 🧩 `CMD` Byte — Bit Layout and Meaning

The **`CMD` field** is 1 byte wide (`8 bits`) and encodes **speed** and **steering** information:

```
CMD[7..0] = L  S1  S0  X  X  X  X  R
            ↑   ↑  ↑               ↑
           Left  Speed            Right
          Steer   Bits            Steer
```

* **Bit 7 (`L`)**: Left steering flag
  Set to `1` when **left** is part of the direction (e.g., `LEFT`, `LEFT+FORWARD`).

* **Bits 6–5 (`S1`, `S0`)**: **Speed bits**

  | Speed | Bits (S1 S0) | Binary | Decimal |
  | ----- | ------------ | ------ | ------- |
  | 1     | `1 0`        | `10`   | 2       |
  | 2     | `0 1`        | `01`   | 1       |
  | 3     | `1 1`        | `11`   | 3       |

* **Bits 4–1**:
  These 4 bits appear to encode a base pattern for each direction (e.g., FWD, BACK, LEFT, RIGHT), and vary consistently with speed and direction—but not with steering.
  | Direction | Speed | CMD base         | Bits 4–1 (binary) | Bits 4–1 (hex) |
  | --------- | ----- | ---------------- | ----------------- | -------------- |
  | FWD       | 1     | `0x40`           | `0000`            | `0x0`          |
  | FWD       | 2     | `0x22`           | `0110`            | `0x6`          |
  | FWD       | 3     | `0x62`           | `1110`            | `0xE`          |
  | BACK      | 1     | `0x46`           | `0110`            | `0x6`          |
  | BACK      | 2     | `0x20`           | `0000`            | `0x0`          |
  | BACK      | 3     | `0x64`           | `0100`            | `0x4`          |
  | SPEED UP  | n/a   | `0x24/0x60/0x42` | varies            | unclear        |

* **Bit 0 (`R`)**: Right steering flag
  Set to `1` when **right** is part of the direction (e.g., `RIGHT`, `RIGHT+BACKWARD`).
  
### PAIR
Pressing process press pair button until remote flases repeatedly, then turn on the car.
Remote starts by sending a pair packet but when remote starts to flasg there is no comminication from remote (probably waiting for ack from car or something) 

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

# RX75 WORK IN PROGRESS
Seems like it uses some other form of modulation possibly freq hopping.
  * 1fffffffffffffffffffffffffffffe3887aa9a3af755029c2a50
  * 1fffffffffffffffffffffffffffffe3887aa9a3af755024e1528
  * 1fffffffffffffffffffffffffffffe3887aa9a3af755024e1528
  * 1fffffffffffffffffffffffffffffe3887aa9a3af755024e1528
  * 1fffffffffffffffffffffffffffffe3887aa9a3af755226a7728
  * ffffffffffffffffffffffffffffffc3887aa9a3af7f40e470de8


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

