import hashlib, json, struct, sys, zlib
out = sys.argv[1]
w = h = 16
raw = b"".join(b"\x00" + bytes([(x * 16) % 256, (y * 16) % 256, 128] * 1) * 1 for y in range(h) for x in range(w)) if False else b"".join(b"\x00" + b"".join(bytes([(x*16)%256,(y*16)%256,128]) for x in range(w)) for y in range(h))
def chunk(t, d): return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xffffffff)
png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b"")
open(out, "wb").write(png)
print(json.dumps({"program": "writes-binary", "out_file": out, "bytes": len(png), "sha256": hashlib.sha256(png).hexdigest()}))
