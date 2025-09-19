#!/usr/bin/env python3
# gfsk_precompute_tx20_rx23.py
#
# Make one call behave like a REAL button press:
# Builds one continuous IQ stream: [packet][gap] × N
# Defaults match your capture (~102 packets over ~1.22 s @ 2-FSK 250 kb/s).

import argparse, binascii, math, sys, time
from typing import List
import numpy as np
from gnuradio import gr, blocks
import osmosdr

# ---- Defaults (mirror your working capture) ----
DEF_CENTER_FREQ = 2.44388e9     # Hz
DEF_SAMP_RATE   = 2.0e6         # S/s
DEF_SPS         = 8             # samples/symbol -> 250 ksym/s
DEF_F0_HZ       = 28320.0       # “0” tone (Hz)
DEF_F1_HZ       = 56641.0       # “1” tone (Hz)
DEF_TX_GAIN     = 40
DEF_IF_GAIN     = 21
DEF_BB_GAIN     = 20
DEF_BW          = 2.0e6

# Remote-like press (~102 packets in ~1.22 s)
DEF_PACKETS     = 100
DEF_PERIOD_S    = 1.22 / 102.0  # ≈ 0.01196 s start-to-start
# ------------------------------------------------

def hex_to_bits(hexstr: str) -> np.ndarray:
    """MSB-first bit order per byte."""
    h = hexstr.strip().replace(" ", "").lower()
    if len(h) % 2:
        h = "0" + h
    b = binascii.unhexlify(h)
    bits = []
    for byte in b:
        for i in range(8):
            bits.append((byte >> (7 - i)) & 1)
    return np.asarray(bits, dtype=np.uint8)

def synth_packet_iq(bits: np.ndarray, fs: float, sps: int, f0: float, f1: float) -> np.ndarray:
    """Generate complex64 IQ for one 2-FSK packet (unit amplitude)."""
    sym  = np.repeat(bits, sps).astype(np.int8)
    freq = np.where(sym == 0, f0, f1).astype(np.float64)
    dphi = 2.0 * math.pi * freq / fs
    phi  = np.cumsum(dphi, dtype=np.float64)
    iq   = np.exp(1j * phi).astype(np.complex64)
    return iq

def build_press_iq(hexline: str, fs: float, sps: int, f0: float, f1: float,
                   packets: int, period_s: float) -> np.ndarray:
    """Build [packet][zeros gap] × packets as one continuous IQ array."""
    bits   = hex_to_bits(hexline)
    pkt    = synth_packet_iq(bits, fs, sps, f0, f1)
    pkt_n  = pkt.shape[0]
    start_to_start = int(round(period_s * fs))
    gap_n  = max(0, start_to_start - pkt_n)
    gap    = np.zeros(gap_n, dtype=np.complex64)

    one    = np.concatenate((pkt, gap))
    press  = np.tile(one, packets)

    total_s = press.shape[0] / fs
    print(f"[press] bits={len(bits)}  pkt={pkt_n} samp (~{pkt_n/fs*1e3:.2f} ms), "
          f"gap={gap_n} samp (~{gap_n/fs*1e3:.2f} ms), "
          f"packets={packets}, total≈{total_s:.2f} s")
    if gap_n == 0:
        print("[warn] period <= packet length; no silent gap inserted.")
    return press

class TXOnce(gr.top_block):
    def __init__(self, iq: np.ndarray, fc: float, fs: float, bw: float,
                 tx_gain: int, if_gain: int, bb_gain: int):
        gr.top_block.__init__(self, "press TX")
        src  = blocks.vector_source_c(iq, repeat=False)
        sink = osmosdr.sink(args="hackrf=0")
        sink.set_sample_rate(fs)
        sink.set_center_freq(fc)
        sink.set_bandwidth(bw)
        sink.set_gain(tx_gain)
        sink.set_if_gain(if_gain)
        sink.set_bb_gain(bb_gain)
        self.connect(src, sink)

def parse_args(argv: List[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Transmit a remote-like 2-FSK 'press' from HEX payload(s)")
    p.add_argument("hex", nargs="+", help="HEX payload(s) to send as separate presses (MSB-first)")
    p.add_argument("--fc", type=float, default=DEF_CENTER_FREQ, help="Center freq [Hz]")
    p.add_argument("--fs", type=float, default=DEF_SAMP_RATE,   help="Sample rate [S/s]")
    p.add_argument("--sps", type=int,   default=DEF_SPS,        help="Samples per symbol")
    p.add_argument("--f0",  type=float, default=DEF_F0_HZ,      help="FSK 0 tone [Hz]")
    p.add_argument("--f1",  type=float, default=DEF_F1_HZ,      help="FSK 1 tone [Hz]")
    p.add_argument("--tx-gain", type=int, default=DEF_TX_GAIN,  help="HackRF TX gain")
    p.add_argument("--if-gain", type=int, default=DEF_IF_GAIN,  help="HackRF IF gain")
    p.add_argument("--bb-gain", type=int, default=DEF_BB_GAIN,  help="HackRF BB gain")
    p.add_argument("--bw",       type=float, default=DEF_BW,    help="RF bandwidth [Hz]")

    grp = p.add_mutually_exclusive_group()
    grp.add_argument("--pps",    type=float, help="Packets per second (start-to-start). Overrides --period.")
    grp.add_argument("--period", type=float, help="Start-to-start period [s] (default: ~0.01196)")

    p.add_argument("--packets", type=int, default=DEF_PACKETS, help="Packets per press (default: 102)")
    p.add_argument("--repeat",  type=int, default=1, help="Repeat whole press N times (default: 1)")
    p.add_argument("--press-gap", dest="press_gap", type=float, default=0.3,
                   help="Gap between presses [s] (default: 0.3)")
    return p.parse_args(argv)

def main(argv: List[str]) -> int:
    args = parse_args(argv)
    period_s = (1.0 / args.pps) if (getattr(args, "pps", None) and args.pps > 0) \
               else (args.period if getattr(args, "period", None) else DEF_PERIOD_S)

    print(f"[cfg] Fc={args.fc/1e9:.6f} GHz  Fs={args.fs/1e6:.2f} MS/s  SPS={args.sps}  "
          f"F0={args.f0:.0f} Hz  F1={args.f1:.0f} Hz  BW={args.bw/1e6:.2f} MHz")
    print(f"[cadence] packets/press={args.packets}  period={period_s*1e3:.2f} ms  "
          f"(~{(1.0/period_s):.1f} pps)  repeats={args.repeat}  press-gap={args.press_gap:.2f} s")

    for rep in range(args.repeat):
        if args.repeat > 1:
            print(f"\n=== Press set {rep+1}/{args.repeat} ===")
        for idx, hexline in enumerate(args.hex, 1):
            shown = hexline if len(hexline) <= 24 else (hexline[:24] + "…")
            print(f"\n-- Press {idx}/{len(args.hex)}: {shown}")
            iq = build_press_iq(hexline, args.fs, args.sps, args.f0, args.f1,
                                args.packets, period_s)
            tb = TXOnce(iq, args.fc, args.fs, args.bw, args.tx_gain, args.if_gain, args.bb_gain)
            tb.start()
            tb.wait()   # ends when vector_source_c runs out
            time.sleep(args.press_gap)

    print("\n[done]")
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
