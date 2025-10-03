import sys
from typing import List, Tuple

# --- CRC Protocol Constants (Provided by user) ---
# Note: This is an MSB-First (unreflected) CRC-16/CCITT variant
INIT   = 0xB5D2
POLY   = 0x1021
XOROUT = 0x247C

def crc16_ccitt(bytes_iter) -> int:
    """CRC-16/CCITT calculation using MSB-first (unreflected) logic."""
    crc = INIT & 0xFFFF
    for b in bytes_iter:
        crc ^= (b << 8) & 0xFFFF
        for _ in range(8):
            # CRC is MSB-first, left shift, check 0x8000
            crc = ((crc << 1) & 0xFFFF) ^ POLY if (crc & 0x8000) else (crc << 1) & 0xFFFF
    return crc & 0xFFFF

def calculate_expected_crc(payload_6b: List[int]) -> int:
    """Calculates the expected 16-bit CRC for a 6-byte payload using the specified parameters."""
    base = crc16_ccitt(payload_6b)
    pred = (base ^ XOROUT) & 0xFFFF
    return pred

def parse_full_frame(full_hex: str) -> Tuple[str, List[int], int]:
    """Parses a full frame (Preamble + 8-byte body) into payload and CRC."""
    
    # Standard preamble nibbles: c710f55 (7 nibbles)
    body_start_index = 0
    if full_hex.startswith("c710f55"):
        body_start_index = 7
    
    # Get the 8-byte body (16 hex chars)
    body_hex = full_hex[body_start_index : body_start_index + 16]
    
    if len(body_hex) < 16:
        # Check for the oddly shorter frame: "c710f5dfb46a5aa683d2850"
        if full_hex.startswith("c710f5df"):
             body_hex = full_hex[8 : 8 + 16]
        else:
             raise ValueError(f"Frame body too short: {full_hex}")

    # Bytes: [D0 D1 D2 D3 D4 D5 C0 C1]
    b = [int(body_hex[i:i+2], 16) for i in range(0, 16, 2)]
    payload_6b = b[0:6]
    observed_tail = (b[6] << 8) | b[7] # CRC is High-Byte first (Big Endian)
    
    return body_hex, payload_6b, observed_tail

def verify_frame(line_label: str, full_frame_hex: str) -> Tuple[int, str]:
    """Verifies a single frame and returns match status and output line."""
    
    try:
        body_hex, payload, observed_tail = parse_full_frame(full_frame_hex)
        
        # Calculate the expected CRC
        calc_crc = calculate_expected_crc(payload)
        
        # Verification check
        is_ok = (calc_crc == observed_tail)
        status = "✅ OK" if is_ok else "❌ FAIL"
        
        # Format for output
        payload_hex = body_hex[0:12]
        observed_hex = body_hex[12:]
        calc_hex = f"{calc_crc:04X}"
        
        output_line = f"| {line_label:<20} | {payload_hex} | {observed_hex} | {calc_hex} | {status:<5} |"
        return (1 if is_ok else 0), output_line
        
    except ValueError as e:
        # Handle malformed lines gracefully
        output_line = f"| {line_label:<20} | {'N/A':<12} | {'N/A':<4} | {'N/A':<4} | ⚠️ SKIP |"
        return 0, output_line

# --- Main Execution Block ---

if __name__ == "__main__":
    
    # Hardcoded list of all captured frames
    import sys
from typing import List, Tuple

# --- CRC Protocol Constants (Provided by user) ---
# Note: This is an MSB-First (unreflected) CRC-16/CCITT variant
INIT   = 0xB5D2
POLY   = 0x1021
XOROUT = 0x247C

def crc16_ccitt(bytes_iter) -> int:
    """CRC-16/CCITT calculation using MSB-first (unreflected) logic."""
    crc = INIT & 0xFFFF
    for b in bytes_iter:
        crc ^= (b << 8) & 0xFFFF
        for _ in range(8):
            crc = ((crc << 1) & 0xFFFF) ^ POLY if (crc & 0x8000) else (crc << 1) & 0xFFFF
    return crc & 0xFFFF

def calculate_expected_crc(payload_6b: List[int]) -> int:
    """Calculates the expected 16-bit CRC for a 6-byte payload using the specified parameters."""
    base = crc16_ccitt(payload_6b)
    pred = (base ^ XOROUT) & 0xFFFF
    return pred

def parse_full_frame(full_hex: str) -> Tuple[str, List[int], int]:
    """Parses a full frame (Preamble + 8-byte body) into payload and CRC."""
    # Standard preamble nibbles: c710f55 (7 nibbles)
    body_start_index = 0
    if full_hex.startswith("c710f55"):
        body_start_index = 7

    # Get the 8-byte body (16 hex chars)
    body_hex = full_hex[body_start_index : body_start_index + 16]

    if len(body_hex) < 16:
        # Handle the shorter variant that starts with c710f5df...
        if full_hex.startswith("c710f5df"):
            body_hex = full_hex[8 : 8 + 16]
        else:
            raise ValueError(f"Frame body too short: {full_hex}")

    # Bytes: [D0 D1 D2 D3 D4 D5 C0 C1]
    b = [int(body_hex[i:i+2], 16) for i in range(0, 16, 2)]
    payload_6b = b[0:6]
    observed_tail = (b[6] << 8) | b[7]  # CRC is High-Byte first (Big Endian)
    return body_hex, payload_6b, observed_tail

def verify_frame(line_label: str, full_frame_hex: str) -> Tuple[int, str]:
    """Verifies a single frame and returns match status and output line."""
    try:
        body_hex, payload, observed_tail = parse_full_frame(full_frame_hex)
        calc_crc = calculate_expected_crc(payload)
        is_ok = (calc_crc == observed_tail)
        status = "✅ OK" if is_ok else "❌ FAIL"

        payload_hex = body_hex[0:12]
        observed_hex = body_hex[12:]
        calc_hex = f"{calc_crc:04X}"

        output_line = f"| {line_label:<20} | {payload_hex} | {observed_hex} | {calc_hex} | {status:<5} |"
        return (1 if is_ok else 0), output_line

    except ValueError:
        output_line = f"| {line_label:<20} | {'N/A':<12} | {'N/A':<4} | {'N/A':<4} | ⚠️ SKIP |"
        return 0, output_line

# --- Main Execution Block ---
if __name__ == "__main__":
    # Hardcoded list of all captured frames
    FRAMES = {
        # --- RX23 Frames (ID: fb46a5) ---
        "RX23 LEFT S1": "c710f55fb46a5aa1843bf50",
        "RX23 LEFT S2": "c710f55fb46a5aa14823350",
        "RX23 LEFT S3": "c710f55fb46a5aa1c033b50",

        "RX23 RIGHT S1": "c710f55fb46a5aa2875ec50",
        "RX23 RIGHT S2": "c710f55fb46a5aa24b46050",
        "RX23 RIGHT S3": "c710f55fb46a5aa2c356850",

        "RX23 FWD S1": "c710f55fb46a5aa48194a50",
        "RX23 FWD S2": "c710f55fb46a5aa44d8c650",
        "RX23 FWD S3": "c710f55fb46a5aa4c59ce50",
        "RX23 FWD ODD": "c710f55fb46a5aa4098424",

        "RX23 BWD S1": "c710f55fb46a5aa88c00650",
        "RX23 BWD S2": "c710f55fb46a5aa84018a50",
        "RX23 BWD S3": "c710f55fb46a5aa8c808250",

        "RX23 PARK": "c710f55fb46a5aa03e0e550",

        "RX23 SPD 1->2": "c710f55fb46a5aa04900250",
        "RX23 SPD 2->3": "c710f55fb46a5aa0c110a50",
        "RX23 SPD 3->1": "c710f55fb46a5aa682d2850",

        "RX23 L+FWD S1": "c710f55fb46a5aa580b7b50",
        "RX23 L+FWD S3_A": "c710f55fb46a5aa54caf750",
        "RX23 L+FWD S3_B": "c710f55fb46a5aa5c4bff50",

        "RX23 R+FWD S1": "c710f5dfb46a5aa683d2850",
        "RX23 R+FWD S2": "c710f55fb46a5aa64fca450",
        "RX23 R+FWD S3": "c710f55fb46a5aa6c7dac50",

        "RX23 L+BWD S1": "c710f55fb46a5aa98d23750",
        "RX23 L+BWD S2": "c710f55fb46a5aa9413bb50",
        "RX23 L+BWD S3": "c710f55fb46a5aa9c92b350",

        "RX23 R+BWD S1": "c710f55fb46a5aaa8e46450",
        "RX23 R+BWD S2": "c710f55fb46a5aaa425e850",
        "RX23 R+BWD S3": "c710f55fb46a5aaaca4e050",

        # --- RX57 Frames (ID: bd0f67) ---
        "RX57 LEFT S1": "c710f55bd0f67aa184a2e50",
        "RX57 LEFT S2": "c710f55bd0f67aa148ba250",
        "RX57 LEFT S3": "c710f55bd0f67aa1c0aaa50",

        "RX57 RIGHT S1": "c710f55bd0f67aa287c7d50",
        "RX57 RIGHT S2": "c710f55bd0f67aa24bdf150",
        "RX57 RIGHT S3": "c710f55bd0f67aa2c3cf950",

        "RX57 FWD S1": "c710f55bd0f67aa08581f50",
        "RX57 FWD S2": "c710f55bd0f67aa44d15750",
        "RX57 FWD S3": "c710f55bd0f67aa4c505f50",

        "RX57 BWD S1": "c710f55bd0f67aa88c99750",
        "RX57 BWD S2": "c710f55bd0f67aa84081b50",
        "RX57 BWD S3": "c710f55bd0f67aa8c891350",

        "RX57 PARK": "c710f55bd0f67aa03e97450",

        "RX57 SPD 1->2": "c710f55bd0f67aa04999350",
        "RX57 SPD 2->3": "c710f55bd0f67aa0c189b50",
        "RX57 SPD 3->1": "c710f55bd0f67a208581f50",

        "RX57 L+FWD S1": "c710f55bd0f67aa5802ea50",
        "RX57 L+FWD S2": "c710f55bd0f67aa54c36650",
        "RX57 L+FWD S3": "c710f55bd0f67aa5c426e50",

        "RX57 R+FWD S1": "c710f55bd0f67aa6834b950",
        "RX57 R+FWD S2": "c710f55bd0f67aa64f53550",
        "RX57 R+FWD S3": "c710f55bd0f67aa6c743d50",

        "RX57 L+BWD S1": "c710f55bd0f67aa98dba650",
        "RX57 L+BWD S2": "c710f55bd0f67aa941a2a50",
        "RX57 L+BWD S3": "c710f55bd0f67aa9c9b2250",

        "RX57 R+BWD S1": "c710f55bd0f67aaa8edf550",
        "RX57 R+BWD S2": "c710f55bd0f67aaa42c7950",
        "RX57 R+BWD S3": "c710f55bd0f67aaacad7150",

        # --- RX75 Frames (ID: 34 75 ee) ---
        "RX75 LEFT S1":  "c710f553475eeaa184f9750",
        "RX75 LEFT S2":  "c710f553475eeaa148e1b50",
        "RX75 LEFT S3":  "c710f553475eeaa1c0f1350",

        "RX75 RIGHT S1": "c710f553475eeaa2879c450",
        "RX75 RIGHT S2": "c710f553475eeaa24b84850",
        "RX75 RIGHT S3": "c710f553475eeaa2c394050",

        "RX75 FWD S1":   "c710f553475eeaa48156250",
        "RX75 FWD S2":   "c710f553475eeaa44d4ee50",
        "RX75 FWD S3":   "c710f553475eeaa4c55e650",

        "RX75 BWD S1":   "c710f553475eeaa88cc2e50",
        "RX75 BWD S2":   "c710f553475eeaa840da250",
        "RX75 BWD S3":   "c710f553475eeaa8c8caa50",

        "RX75 PARK":     "c710f553475eeaa03eccd50",

        "RX75 SPD 1->2": "c710f553475eeaa049c2a50",
        "RX75 SPD 2->3": "c710f553475eeaa0c1d2250",
        "RX75 SPD 3->1": "c710f553475eeaa085da650",

        "RX75 L+FWD S1": "c710f553475eeaa58075350",
        "RX75 L+FWD S2": "c710f553475eeaa54c6df50",
        "RX75 L+FWD S3": "c710f553475eeaa5c47d750",

        "RX75 R+FWD S1": "c710f553475eeaa68310050",
        "RX75 R+FWD S2": "c710f553475eeaa64f08c50",
        "RX75 R+FWD S3": "c710f553475eeaa6c718450",

        "RX75 L+BWD S1": "c710f553475eeaa98de1f50",
        "RX75 L+BWD S2": "c710f553475eeaa941f9350",
        "RX75 L+BWD S3": "c710f553475eeaa9c9e9b50",

        # Note: This S1 frame equals the plain BACKWARD S1 you provided; keeping as-is per your list
        "RX75 R+BWD S1": "c710f553475eeaa88cc2e50",
        "RX75 R+BWD S2": "c710f553475eeaaa429c050",
        "RX75 R+BWD S3": "c710f553475eeaaaca8c850",
    }
    
    total_frames = 0
    ok_frames = 0
    
    print("\n" + "=" * 80)
    print("XN297L CRC-16 Verification (Testing: Init=0x{:04X}, XOROUT=0x{:04X}, Unreflected Data)".format(INIT, XOROUT))
    print("=" * 80)
    
    # Table Header
    print("| {:<20} | {:<12} | {:<4} | {:<4} | {:<5} |".format(
        "COMMAND", "PAYLOAD (6B)", "OBS CRC", "CALC", "STATUS"
    ))
    print("|" + "-" * 22 + "|" + "-" * 14 + "|" + "-" * 6 + "|" + "-" * 6 + "|" + "-" * 7 + "|")

    # Run verification on all frames
    for label, frame_hex in FRAMES.items():
        matched, output_line = verify_frame(label, frame_hex)
        ok_frames += matched
        total_frames += 1
        print(output_line)
        
    print("|" + "=" * 22 + "|" + "=" * 14 + "|" + "=" * 6 + "|" + "=" * 6 + "|" + "=" * 7 + "|")
    print(f"Summary: {ok_frames}/{total_frames} Frames Matched (excluding skipped/malformed).")
    print("==================================================================================")