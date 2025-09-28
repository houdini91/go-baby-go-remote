# RX7 - TX1

| Item                  | Value                                                                 |
|-----------------------|-----------------------------------------------------------------------|
| Remote/Receiver       | **TX1 (remote)** → **RX7 (car)**                                   |
| FCC ID                | -                     |
| Band / Modulation     | **2.4 GHz**, suspected **GFSK** or **2FSK**                          |
| Probable RF SoC       | Panchip [XN297L](https://www.panchip.com/static/upload/file/20190916/1568621331607821.pdf) |
| Tools Used            | HackRF, GNU Radio, Universal Radio Hacker (URH)                       |

## ⚡️ RF Protocol Specification & Verified Command

| Parameter                    | Value                                | Notes                                                                         |
| ---------------------------- | ------------------------------------ | ----------------------------------------------------------------------------- |
| Center Freq                  | `2.433 GHz`                          | Matches URH/HackRF capture                                                    |
| Sample Rate                  | `4.0 MS/s`                           | `SAMP_RATE = 4e6`                                                             |
| Bitrate                      | `1 Mbps`                             | `SAMP_RATE / SPS = 4e6 / 4`                                                   |
| SPS (samples/sym)            | `4`                                  | `SPS = 4`                                                                     |
| Modulation                   | 2-FSK                                | Narrow-band GFSK-like                                                         |
| FSK Tones                    | `F0 = 492,188 Hz`, `F1 = 984,375 Hz` | Matches URH deviations                                                        |
| HackRF Gains                 | TX: `40`, IF: `21`, BB: `20`         | Script default                                                                |
| **TX Script Repeat Pattern** | **Send one packet every ~12.35 ms**  | Mimic stock cadence (~81 Hz); short-press burst ≈ **1.15 s** (~90–95 packets) |
| **Stock Remote Cadence**     | **~81 packets/s**                    | Start-to-start ≈ **12.35 ms**; on-air ≈ **379 µs**; gap ≈ **11.95 ms**        |


### Raw Packets shifted

**FWD**:
* 710F552F7D8726491656B992AEC4C108500 (Speed 1)
* 710F552F7D8726491656B992AEC80084500 (Speed 2)
* 710F552F7D8726491656B992AEC0818C500 (Speed 3)

**BACK**:
* 710F552F7D8726491656B992AE041844500 (Speed 1)
* 710F552F7D8726491656B992AE08D9C8500 (Speed 2)
* 710F552F7D8726491656B992AE0058C0500 (Speed 3)

**RIGHT**:
* 710F552F7D8726491656B992AEA4ADAE500 (Speed 1)
  710F552F7D8726491656B992AEA86C22500 (Speed 2)
  710F552F7D8726491656B992AEA0ED2A500 (Speed 3)

**LEFT**:
* 710F552F7D8726491656B992AE949BFD500 (Speed 1)
* 710F552F7D8726491656B992AE985A71500 (Speed 2)
* 710F552F7D8726491656B992AE90DB79500 (Speed 3)

**LEFT+FWD**:
* 710F552F7D8726491656B992AED4D339500 (Speed 1)
* 710F552F7D8726491656B992AED812B5500 (Speed 2)
* 710F552F7D8726491656B992AED093BD500 (Speed 3)

**RIGHT+FWD**:
* 710F552F7D8726491656B992AEE4E56A500 (Speed 1)
* 710F552F7D8726491656B992AEE824E6500 (Speed 2)
* 710F552F7D8726491656B992AEE0A5EE500 (Speed 3)

**LEFT+BACK**:
* 710F552F7D8726491656B992AE140A75500 (Speed 1)
* 710F552F7D8726491656B992AE18CBF9500 (Speed 2)
* 710F552F7D8726491656B992AE104AF1500 (Speed 3)

**RIGHT+BACK**:
* 710F552F7D8726491656B992AE243C26500 (Speed 1)
* 710F552F7D8726491656B992AE28FDAA500 (Speed 2)
* 710F552F7D8726491656B992AE207CA2500 (Speed 3)

**SPEED**:
* 710F552F7D8726491656B992AE83F92B500 (Speed 1-2)
* 710F552F7D8726491656B992AE83F92B500 (Speed 2-3)
* 710F552F7D8726491656B992AE83F92B500 (Speed 3-2)

* **PARK**:
* 710f552f7d8726491656b992ae83f92b500


### 🔄 Pairing Process (Work in Progress)
TBD
  
## Frame layout assumption (sep 25) 

| Field             | Size    | Example | Notes                                                                          |
| ----------------- | ------- | --------------------------------------------------- | ------------------------------------------------------------------------------ |
| **PREAMBLE/SYNC** | 3 B     | `71 0F 55`                                          | Radio sync; not payload.                                                       |
| **CAR ID**     | **5 B** |`2F 7D 87 26 49`                        | - |
| **REMOTE ID**     | **4 B** | `16 56 B9 92`                        | - |
| **HEADER**        | 1 B     | `AE`                                                | Fixed header.                                                                  |
| **OP**            | 1 B     | `94`                                                | High nibble = direction; low nibble = speed code.                              |
| **CMD**           | 1 B     | `9B`                                                | Direction signature ⊕ speed mask.                                                                                |
| **TAIL**          | 2 B     | `FD 50`                                                | CRC


### 🧠 OP byte — bit layout & mapping

```
OP = [ d3 d2 d1 d0 | s3 s2 s1 s0 ]
       high nibble     low nibble
       (direction)     (speed)
```

* **d3 (bit 3)**: **domain bit** — `1` ⇒ forward/steer domain (LEFT/RIGHT/FWD combos), 
                                   `0` ⇒ back domain (LEFT/RIGHT with **BACK**).
* **d2 (bit 2)**: **FWD flag** — meaningful **only when `d3=1`**; in back domain (`d3=0`) this **must be 0**.
* **d1 (bit 1)**: **RIGHT flag**.
* **d0 (bit 0)**: **LEFT flag**.

| Direction Combo | OR expression (high nibble only) | Result |
| --------------- | -------------------------------- | ------ |
| LEFT            | `0x8 \| 0x1`                     | `0x9`  |
| RIGHT           | `0x8 \| 0x2`                     | `0xA`  |
| FORWARD         | `0x8 \| 0x4`                     | `0xC`  |
| BACK            | `0x0`                            | `0x0`  |
| LEFT + FORWARD  | `0x8 \| 0x1 \| 0x4`              | `0xD`  |
| RIGHT + FORWARD | `0x8 \| 0x2 \| 0x4`              | `0xE`  |
| LEFT + BACK     | `0x0 \| 0x1`                     | `0x1`  |
| RIGHT + BACK    | `0x0 \| 0x2`                     | `0x2`  |

| Low nibble | Speed tier  |
| ---------- | ----------- |
| `0x4`      | **Speed 1** |
| `0x8`      | **Speed 2** |
| `0x0`      | **Speed 3** |


#### 🧩 `CMD` Byte — Bit Layout and Meaning

```
CMD[7..0] =  b7  b6  b5  b4  b3  b2  b1  b0
             ^    ^  \____DIR_SIG_____/   ^
             |    |                       └─ toggled for S2 (bit0 = 0x01)
             |    └─ toggled for S1 (bit6 = 0x40)
             └──── toggled for S2 (bit7 = 0x80)
```

**Bit usage (b7..b0):**

* **b7** — flipped for **S2** (part of speed mask `0x81`)
* **b6** — flipped for **S1** (speed mask `0x40`)
* **b5..b1** — **direction signature** bits (stable across speeds)
* **b0** — flipped for **S2** (the `+0x01` in mask `0x81`)

* **Speed masks (constant across all directions):**

  * **S1** (low nibble = `0x4` in `OP`):  `SPEED_MASK = 0x40`
  * **S2** (low nibble = `0x8` in `OP`):  `SPEED_MASK = 0x81`
  * **S3** (low nibble = `0x0` in `OP`):  `SPEED_MASK = 0x00`

| Direction / Combo | CMD @ S1 | CMD @ S2 | CMD @ S3 (DIR_SIG) |
| ----------------- | -------- | -------- | -------- |
| LEFT              | `0x9B`   | `0x5A`   | `0xDB`   |
| RIGHT             | `0xAD`   | `0x6C`   | `0xED`   |
| FORWARD           | `0xC1`   | `0x00`   | `0x81`   |
| BACK              | `0x18`   | `0xD9`   | `0x58`   |
| LEFT + FORWARD    | `0xD3`   | `0x12`   | `0x93`   |
| RIGHT + FORWARD   | `0xE5`   | `0x24`   | `0xA5`   |
| LEFT + BACK       | `0x0A`   | `0xCB`   | `0x4A`   |
| RIGHT + BACK      | `0x3C`   | `0xFD`   | `0x7C`   |

### 📡 Packet (“burst”) cadence — TX1 → RX7

* **While the button is held:** the remote repeats the **drive command** at ~**81 packets/s** (≈ **12.35 ms** start-to-start).
* **On release:** it switches immediately to **`PARK/NEUTRAL`** (your special OP/CMD), **but keeps the same cadence** for a short **post-release dwell**—so a short press still shows a full burst.

What this means in practice:

* The car **starts moving** on the first valid *drive* packet.
* It **stops** shortly **after the last drive packet**, either because it receives *PARK* packets or its **watchdog** times out.
  The extra packets after release are **PARK**—they don’t propel the car; they ensure a reliable stop.

time ──▶ [drive][drive][drive]……(release)→[PARK][PARK]…[PARK]

**Measured from your captures**

* **One packet on-air:** ~**379 µs**.
* **Inter-packet gap (end→next start):** ~**11.95 ms**.
* **Start-to-start interval:** ~**12.35 ms** ⇒ **~81 Hz**.
* **Full burst (short press):** ~**1.15 s** ⇒ **≈ 90–95 packets** total.

**Timing sanity check**

* 379 µs (on-air) + 11.95 ms (gap) ≈ 12.33 ms ≈ 12.35 ms (start-to-start) ✅
* With **SPS = 4 @ 4 MS/s**, **symbol = 1 µs** ⇒ **~1 Mb/s** effective bit rate; a ~379 µs frame ≈ ~379 bits on-air (including preamble/overhead).

> **Long press:** packets continue at ~**81 Hz** until release.

--- 
### APPENDX A: ON air shifted Raw Packets capture

**FWD**:
* 3887aa97bec393248b2b5cc957626084280 (Speed 1)
* 3887aa97bec393248b2b5cc957640042280 (Speed 2)
* 3887aa97bec393248b2b5cc9576040c6280 (Speed 3)

**BACK**:
  * 3887aa97bec393248b2b5cc957020c22280 (Speed 1)
  * 3887aa97bec393248b2b5cc957046ce4280 (Speed 2)
  * 3887aa97bec393248b2b5cc957002c60280 (Speed 3)

**RIGHT**:
* 3887aa97bec393248b2b5cc9575256d7280 (Speed 1)
  3887aa97bec393248b2b5cc957543611280 (Speed 2)
  3887aa97bec393248b2b5cc957507695280 (Speed 3)

**LEFT**:
* 3887aa97bec393248b2b5cc9574a4dfea80 (Speed 1)
* 3887aa97bec393248b2b5cc9574c2d38a80 (Speed 2)
* 3887aa97bec393248b2b5cc957486dbca80 (Speed 3)
  
**LEFT+FWD**:
* 3887aa97bec393248b2b5cc9576a699ca80 (Speed 1)
* 3887aa97bec393248b2b5cc9576c095aa80 (Speed 2)
* 3887aa97bec393248b2b5cc9576849dea80 (Speed 3)

**RIGHT+FWD**:
* 3887aa97bec393248b2b5cc9577272b5280 (Speed 1)
* 3887aa97bec393248b2b5cc957741273280 (Speed 2)
* 3887aa97bec393248b2b5cc9577052f7280 (Speed 3)
  
**LEFT+BACK**:
* 3887aa97bec393248b2b5cc9570a053aa80 (Speed 1)
* 3887aa97bec393248b2b5cc9570c65fca80 (Speed 2)
* 3887aa97bec393248b2b5cc957082578a80 (Speed 3)

**RIGHT+BACK**
* 3887aa97bec393248b2b5cc957121e13280
* 3887aa97bec393248b2b5cc957147ed5280
* 3887aa97bec393248b2b5cc957103e51280

**PARK**
* 3887aa97bec393248b2b5cc95741fc95a80

**SPEED**:
3887aa97bec393248b2b5cc957442420280 (Speed 1 - 2)
3887aa97bec3a6491656b9935d019290a00 (Speed 2 - 3)
3887aa97bec393248b2b5cc9574244e6280 (SPeed 3 - 1)

**Pairing**:
On car wake uup Car sends repeated packets on sync channel 2.407G until remote responds with any packet.
* 3887aa97bec39324f4ab5cc9573f4993280  ->   710f552f7d872649e956b992ae7e9326500
  3887aa97bec39324f4ab5cc957462e3da81 ??
  
RemoteReplays on both 2.407G and Data 2.433G with speed packet
* 3887aa97bec393248b2b5cc9574244e6280 (SPeed 3 - 1)
  
  

