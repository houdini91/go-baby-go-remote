# RX7 - TX1

| Item                  | Value                                                                 |
|-----------------------|-----------------------------------------------------------------------|
| Remote/Receiver       | **TX1 (remote)** → **RX7 (car)**                                   |
| FCC ID                | -                     |
| Band / Modulation     | **2.4 GHz**, suspected **GFSK** or **2FSK**                          |
| Probable RF SoC       | Panchip [XN297L](https://www.panchip.com/static/upload/file/20190916/1568621331607821.pdf) |
| Tools Used            | HackRF, GNU Radio, Universal Radio Hacker (URH)                       |

## ⚡️ RF Protocol Specification & Verified Command

| Parameter                   | Value                                | Notes                          |
| --------------------------- | ------------------------------------ | ------------------------------ |
| Center Freq                 | `2.433   GHz`                        | Matches URH/HackRF capture     |
| Sample Rate                 | `4.0 MS/s`                           | `SAMP_RATE = 4e6`              |
| Bitrate                     | `100 Mbps`                           | `SAMP_RATE / SPS`              |
| SPS (samples/sym)           | `4`                                  | `SPS = 4`                      |
| Modulation                  | 2-FSK                                | Narrow-band GFSK-like          |
| FSK Tones                   | `F0 = 492188 Hz`, `F1 = 984375 Hz`   | Matches URH deviations         |
| HackRF Gains                | TX: `40`, IF: `21`, BB: `20`         | Script default                 |
| **TX Script Repeat Pattern**|  - | - |
| **Stock Remote Cadence**    | -  | - |

### Raw Packets capture

**FWD**:
* 3887aa97bec393248b2b5cc957626084280 (Speed 1)

**BACK**:
* 3887aa97bec393248b2b5cc957020c22280 (Speed 1)

**RIGHT**:
* 3887aa97bec393248b2b5cc9575256d7280 (Speed 1)

**LEFT**:
* 3887aa97bec393248b2b5cc9574a4dfea80 (Speed 1)


###################### 
TMP RAW PACKETS

FWD
f002aafffffffffffffffffffffffffffffffffffffffffffbfffffff83887aa97bec393248b2b5cc957626084280
9e0055bffffffffffffffffffffffffffffffffffffffffffefffffffe0e21eaa5efb0e4c922cad73255d898210a00
9e00aab6ffffffffffffffffffffffffffffffffffffffffffbfffffff83887aa97bec393248b2b5cc957626084280

BACK
3c0002afffffffffffffffffffffffffffffffffffffffffffcfffffffc1c43d54bdf61c9924595ae64ab8106111400
9f0000aafffffffffffffffffffffffffffffffffffffffffff9fffffff83887aa97bec393248b2b5cc957020c22280
f00003afffffffffffffffffffffffffffffffffffffffffffcfffffff83887aa97bec393248b2b5cc957020c22280 (back)


RIGHT:
fc02aafffffffffffffffffffffffffffffffffffffffffffffffffffff83887aa97bec393248b2b5cc9575256d7280

LEFT
000000000000000000000000000000000000000000000000003887aa97bec393248b2b5cc9574a4dfea800




