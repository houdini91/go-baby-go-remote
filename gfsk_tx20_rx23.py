#!/usr/bin/env python3
# tx_fsk_hex.py
#
# Usage examples:
#   python tx_fsk_hex.py "07ffffffffffffffffffffffffffffe3887aafda352d50a4119a0"
#   python tx_fsk_hex.py HEX1 HEX2 ...
#
# Matches your URH TX that worked:
#   Fc = 2.444 GHz, Fs = 2.0 MS/s, sps = 8  ->  250 ksym/s
#   FSK tones: F0=28320 Hz, F1=56641 Hz
# LEFT TURN: python3 rx_gfsk_125Kbs.py "07ffffffffffffffffffffffffffffe3887aafda352d50a4119a0"

import sys, binascii, numpy as np, time
from gnuradio import gr, blocks, analog
import osmosdr
import math

# --------- CONFIG (mirror URH that worked) ----------
CENTER_FREQ = 2.444e9      # Hz
SAMP_RATE   = 2.0e6        # samples/s
SPS         = 8            # samples per symbol  -> 250 ksym/s
F0_HZ       = 28320.0      # “0” tone (Hz)  (URH pm[0])
F1_HZ       = 56641.0      # “1” tone (Hz)  (URH pm[1])
TX_GAIN     = 40           # HackRF VGA gain (adjust as needed)
IF_GAIN     = 21
BB_GAIN     = 20
BANDWIDTH   = 2.0e6        # matches URH “Bandwidth”
REPEAT_BURST= 5            # repeats per message
BURST_GAP_S = 0.05         # seconds between repeats
# ----------------------------------------------------

def hex_to_bits(hexstr: str) -> np.ndarray:
    # sanitize & pad to even length
    h = hexstr.strip().lower().replace(" ", "")
    if len(h) % 2 == 1:
        h = "0" + h
    try:
        b = binascii.unhexlify(h)
    except binascii.Error as e:
        raise ValueError(f"Bad HEX '{hexstr}': {e}")
    bits = []
    for byte in b:
        for i in range(8):
            bits.append((byte >> (7 - i)) & 1)  # MSB-first
    return np.array(bits, dtype=np.uint8)

class TX2FSK(gr.top_block):
    def __init__(self, bits: np.ndarray):
        gr.top_block.__init__(self, "TX 2-FSK from HEX")

        # 1) bit stream -> symbol timing (repeat each bit SPS times)
        src_bits = blocks.vector_source_b(bits.tolist(), repeat=False)
        upsample = blocks.repeat(gr.sizeof_char, SPS)

        # 2) map {0,1} -> instantaneous baseband frequency in Hz
        to_float = blocks.uchar_to_float()
        scale    = blocks.multiply_const_ff(F1_HZ - F0_HZ)
        bias     = blocks.add_const_ff(F0_HZ)

        # 3) FM at baseband: integrate 2*pi*Hz / Fs  -> complex exp(j*phase)
        fm = analog.frequency_modulator_fc(2.0 * math.pi / SAMP_RATE)

        # 4) HackRF sink
        sink = osmosdr.sink(args="hackrf=0")
        sink.set_sample_rate(SAMP_RATE)
        sink.set_center_freq(CENTER_FREQ)
        sink.set_bandwidth(BANDWIDTH)
        sink.set_gain(TX_GAIN)
        sink.set_if_gain(IF_GAIN)
        sink.set_bb_gain(BB_GAIN)
        # Optional helpers if needed:
        # sink.set_dc_offset_mode(0)
        # sink.set_iq_balance_mode(0)

        # wire it up
        self.connect(src_bits, upsample, to_float, scale, bias, fm, sink)

def send_hex_once(hexline: str):
    bits = hex_to_bits(hexline)
    symrate = SAMP_RATE / SPS
    dur_s   = len(bits) / symrate
    print(f"[i] HEX chars={len(hexline)} -> bits={len(bits)}, "
          f"symrate={symrate:.0f} sym/s, burst≈{dur_s*1000:.1f} ms")
    tb = TX2FSK(bits)
    tb.start()
    time.sleep(dur_s + 0.02)  # a tiny guard
    tb.stop(); tb.wait()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python tx_fsk_hex.py <HEX1> [HEX2 ...]")
        sys.exit(1)

    msgs = sys.argv[1:]
    print(f"[cfg] Fc={CENTER_FREQ/1e9:.6f} GHz  Fs={SAMP_RATE/1e6:.1f} MS/s  "
          f"SPS={SPS}  F0={F0_HZ:.0f} Hz  F1={F1_HZ:.0f} Hz  BW={BANDWIDTH/1e6:.1f} MHz")
    for line in msgs:
        shown = (line if len(line) <= 20 else line[:20] + "...")
        print(f"\n=== Sending {REPEAT_BURST}x: {shown} ({len(line)} hex chars) ===")
        for i in range(REPEAT_BURST):
            print(f"  burst {i+1}/{REPEAT_BURST}")
            send_hex_once(line)
            time.sleep(BURST_GAP_S)
