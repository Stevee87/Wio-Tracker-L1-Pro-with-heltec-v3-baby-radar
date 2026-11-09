import struct, sys
MAGIC0, MAGIC1, MAGIC_END = 0x0A324655, 0x9E5D5157, 0x0AB16F30
def uf2_to_bin(path):
    data = open(path,'rb').read()
    blocks = []
    for i in range(0, len(data), 512):
        b = data[i:i+512]
        m0,m1,flags,addr,sz,bno,nblk,fam = struct.unpack('<8I', b[:32])
        assert m0==MAGIC0 and m1==MAGIC1 and struct.unpack('<I',b[508:512])[0]==MAGIC_END, f'bad block {i//512}'
        blocks.append((addr, sz, b[32:32+sz], flags, fam))
    base = blocks[0][0]
    out = bytearray()
    for addr, sz, payload, flags, fam in blocks:
        assert addr == base+len(out), f'gap at {addr:#x}'
        out += payload
    return bytes(out), base, blocks[0][3], blocks[0][4], blocks[0][1]
def bin_to_uf2(bin_bytes, base, flags, fam, chunk=256):
    n = (len(bin_bytes)+chunk-1)//chunk
    out = bytearray()
    for i in range(n):
        payload = bin_bytes[i*chunk:(i+1)*chunk]
        hdr = struct.pack('<8I', MAGIC0, MAGIC1, flags, base+i*chunk, len(payload), i, n, fam)
        out += hdr + payload + b'\0'*(476-len(payload)) + struct.pack('<I', MAGIC_END)
    return bytes(out)
if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'tobin':
        b, base, flags, fam, sz = uf2_to_bin(sys.argv[2]); open(sys.argv[3],'wb').write(b)
        print(f'base={base:#x} flags={flags:#x} family={fam:#x} blocksize={sz} total={len(b)}')
    elif cmd == 'touf2':
        base=int(sys.argv[4],0); flags=int(sys.argv[5],0); fam=int(sys.argv[6],0)
        open(sys.argv[3],'wb').write(bin_to_uf2(open(sys.argv[2],'rb').read(), base, flags, fam))
