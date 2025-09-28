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


### #################### Raw Packets capture ############################################################3

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
  
** LEFT + BACK **

** RIGHT + BACK **

**SPEED**:
3887aa97bec393248b2b5cc957626084280 (Speed 1 - 2) ?
3887aa97bec393248b2b5cc957442420280 (Speed 1 - 2) ?
3887aa97bec393248b2b5cc9574064a4280 (Speed 2 - 3)



