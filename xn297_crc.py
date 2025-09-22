#!/usr/bin/env python3
import argparse
import sys
from typing import Tuple, Optional

# ---------------------------
# XN297L / nRF24-family CRC16 (CCITT), MSB-first, poly 0x1021, init 0xB5D2
# ---------------------------

POLY = 0x1021
INIT = 0xB5D2

def crc16_ccitt(data: bytes, init: int = INIT) -> int:
    crc = init & 0xFFFF
    for b in data:
        crc ^= (b << 8) & 0xFFFF
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) & 0xFFFF) ^ POLY
            else:
                crc = (crc << 1) & 0xFFFF
    return crc & 0xFFFF

def parse_hex(s: str) -> bytes:
    s = s.strip().lower().replace(" ", "")
    if s.startswith("0x"):
        s = s[2:]
    if len(s) % 2 == 1:
        # Many of your working "short" strings had a trailing nibble, just drop it.
        s = s[:-1]
    try:
        return bytes.fromhex(s)
    except ValueError:
        raise SystemExit("Bad hex input.")

def strip_trailer(b: bytes) -> Tuple[bytes, Optional[int]]:
    """
    Your TX tool sometimes appends a tool trailer 0x28. If present, drop it and return the value.
    Return (payload_without_trailer, trailer_byte_or_None).
    """
    if len(b) >= 1 and b[-1] == 0x28:
        return b[:-1], 0x28
    return b, None

def split_data_crc(frame: bytes) -> Tuple[bytes, int]:
    """
    Split into (data_without_crc, observed_crc).
    Assumes the last 2 bytes are CRC (big-endian) AFTER we have removed any 0x28 trailer.
    """
    if len(frame) < 3:
        raise SystemExit("Frame too short.")
    data = frame[:-2]
    crc_obs = (frame[-2] << 8) | frame[-1]
    return data, crc_obs

def hex_be16(v: int) -> str:
    return f"{(v>>8)&0xFF:02x}{v&0xFF:02x}"

def autodetect_xorout(data: bytes, crc_obs: int) -> int:
    """
    Given one known-good frame (data + on-air CRC), compute XOROUT:
        XOROUT = crc_calc ^ crc_obs
    For your 4-byte payload frames, this returned 0xAD0D (consistent).
    """
    crc_calc = crc16_ccitt(data)
    return crc_calc ^ crc_obs

def rebuild_frame(data: bytes, xorout: int, add_trailer_28: bool) -> bytes:
    crc = crc16_ccitt(data) ^ (xorout & 0xFFFF)
    out = data + bytes([(crc >> 8) & 0xFF, crc & 0xFF])
    if add_trailer_28:
        out += b"\x28"
    return out

def pretty(b: bytes) -> str:
    return b.hex()

# ------------- CLI --------------

def main():
    p = argparse.ArgumentParser(
        description="XN297L CRC16 (CCITT) verifier/patcher (init=0xB5D2, big-endian on-air). "
                    "Calibrate XOROUT from a known-good frame, then verify or rebuild after edits."
    )
    p.add_argument("hex", nargs="+",
                   help="Hex frame(s). Accepts your short TX format (may end with ...28). "
                        "Each must include the 2-byte on-air CRC at the end (before any 0x28 trailer).")
    p.add_argument("--xorout", type=lambda x: int(x,16), default=None,
                   help="Force XOROUT (hex). If omitted, will be calibrated from the first given frame.")
    p.add_argument("--verify", action="store_true",
                   help="Verify provided frames against the calibrated/forced XOROUT.")
    p.add_argument("--edit", metavar="OFFSET:BYTE", action="append",
                   help="Edit one byte in the DATA (addr+payload) before CRC rebuild. "
                        "OFFSET is zero-based into DATA (i.e., not counting the CRC). Example: --edit 4:36 to change 0x35->0x36 at data[4].")
    p.add_argument("--print-data", action="store_true", help="Print parsed DATA and CRC for each input.")
    args = p.parse_args()

    # Parse first frame; calibrate XOROUT if needed
    first_raw = parse_hex(args.hex[0])
    first_core, trailer = strip_trailer(first_raw)
    data0, crc0 = split_data_crc(first_core)
    xorout = args.xorout if args.xorout is not None else autodetect_xorout(data0, crc0)

    print(f"[calibration] data_len={len(data0)} crc_obs=0x{crc0:04X}  crc_calc=0x{crc16_ccitt(data0):04X}  XOROUT=0x{xorout:04X}")

    if args.print_data:
        print(f"[frame0] DATA={data0.hex()}  CRC_BE={crc0:04x}  trailer={'28' if trailer==0x28 else 'none'}")

    # Verification / Rebuild for each provided frame
    for idx, hx in enumerate(args.hex):
        raw = parse_hex(hx)
        core, tr = strip_trailer(raw)
        data, crc_obs = split_data_crc(core)
        crc_calc = crc16_ccitt(data)
        crc_expected = crc_calc ^ (xorout & 0xFFFF)
        ok = (crc_expected == crc_obs)

        print(f"[frame{idx}] verify: CRC_calc^XOROUT=0x{crc_expected:04X}  vs  CRC_obs=0x{crc_obs:04X}  -> {'OK' if ok else 'MISMATCH'}")
        if args.print_data:
            print(f"          DATA={data.hex()}  trailer={'28' if tr==0x28 else 'none'}")

        # If edits requested, apply to THIS frame's data then rebuild with calibrated XOROUT
        if args.edit:
            db = bytearray(data)
            for e in args.edit:
                try:
                    off_s, byte_s = e.split(":")
                    off = int(off_s, 0)
                    val = int(byte_s, 16)
                except Exception:
                    raise SystemExit(f"Bad --edit format: '{e}'. Use OFFSET:HH (hex).")
                if not (0 <= off < len(db)):
                    raise SystemExit(f"Edit offset {off} out of range for data length {len(db)}.")
                db[off] = val & 0xFF

            rebuilt = rebuild_frame(bytes(db), xorout, add_trailer_28=(tr==0x28))
            print(f"[frame{idx}] rebuilt_hex={rebuilt.hex()}")
            print(f"[frame{idx}] rebuilt_crc=0x{((rebuilt[-3] if tr==0x28 else rebuilt[-2])<<8 | (rebuilt[-2] if tr==0x28 else rebuilt[-1])):04X}")

if __name__ == "__main__":
    main()
