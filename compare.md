# 📊 Weelye 2.4 GHz Protocol Comparison (High-Level Differences)

| Aspect                         | `RX23` (2.444 GHz)             | `RX57` (2.446 GHz)             | `RX75` / Alt `RX23` (2.453 GHz)       |
| :-----------------------------|:-------------------------------|:-------------------------------|:--------------------------------------|
| **Normal Channel / CF**       | **2.444 GHz**                  | **2.446 GHz**                  | **2.453 GHz**                         |
| **Modulation / Bitrate**      | 2-FSK @ 250 kbps               | 2-FSK @ 250 kbps               | 2-FSK @ 250 kbps                      |
| **Device ID (3 B Example)**   | `fb 46 a5`                     | `bd 0f 67`                     | `34 75 ee`                            |
| **Stock Cadence (Held)**      | ~83 pkts/s                     | ~82.7 pkts/s                   | ~83.0 pkts/s                          |
| **Start-to-Start Interval**   | ~11.9 ms                       | 12.09 ms                       | ~12.05 ms                             |
| **On-Air Time per Packet**    | ~0.85–0.90 ms                  | ~0.864 ms                      | ~0.866 ms                             |
| **Short-Press Burst Duration**| ~1.22 s                        | ~1.15 s                        | ~1.11 s                               |
| **`OP` Byte Speed Mapping**   | S1=`0x8`<br>S2=`0x4`<br>S3=`0xC` (assumed) | Same                  | Same                                  |
| **`CMD` Direction Signature** | Differs per direction<br>Must match speed mask | Same         | e.g. `LEFT = 0x0E` (masked)           |
| **Pairing Frame (Example)**   | `c710f55fb46a5ae04900250`      | `c710f55bd0f67aa08581f50`      | `c710f553475eeaa085da650`            |



## Compare RX23/57/75 Pairing packets.

* **Remote pairing mode**
  When entering pairing mode, the remote transmits on a slightly different channel (\~2.44 GHz) at a noticeably slower burst rate.

  ```
  c710f55cccccca518cbb4a850
  ```

* **Car response** (confirmed via HackRF)
  The car appears to respond on \~2.405 GHz using a similar burst format:

  ```
  c710f55cccccc5aa562df3b2950 (RX23) Device ID fb46a5aa
  c710f55cccccc5ae6f0bd4db950 (RX57) Device ID bd0f67aa
  c710f55cccccc5a77ae2cbc9850 (RX75) Device ID 3475eeaa
  ```
    