// tpzl.c v5 - 4KB segment compressor (matches Sony TPZL layout)
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#define BLOCK (1 << 16)
#define SEG   4096
#define WINDOW 4095
#define MAXMATCH 64
#define HSIZE 4096

static const int lengths[18] = {3,4,5,6,7,8,9,10,11,12,13,14,15,16,32,64,0,0};
typedef struct { uint8_t *p; size_t len, cap; } Buf;
static void bput(Buf *b, uint8_t v) { if (b->len == b->cap) { b->cap = b->cap ? b->cap*2 : 4096; b->p = realloc(b->p, b->cap); } b->p[b->len++] = v; }
static void bwrite(Buf *b, const uint8_t *d, size_t n) { if (b->len+n > b->cap) { while (b->len+n > b->cap) b->cap = b->cap ? b->cap*2 : 4096; b->p = realloc(b->p, b->cap); } memcpy(b->p+b->len, d, n); b->len += n; }
static uint32_t hash3(const uint8_t *d, size_t i) { uint32_t v = (uint32_t)d[i] | ((uint32_t)d[i+1]<<8) | ((uint32_t)d[i+2]<<16); return (v*2654435761u)>>20; } // 12 bits

// compress one segment (n <= SEG) into a 0xF0 stream
static void lz_segment(const uint8_t *d, size_t n, Buf *out) {
    int32_t *head = malloc(HSIZE*sizeof(int32_t));
    int32_t *prev = malloc(n*sizeof(int32_t));
    for (int i = 0; i < HSIZE; i++) head[i] = -1;
    bput(out, 0xF0);
    size_t i = 0; int done = 0;
    while (i < n && !done) {
        size_t flagpos = out->len; bput(out, 0); uint8_t flags = 0;
        for (int bit = 0; bit < 8; bit++) {
            if (i >= n) { flags |= (uint8_t)(1<<bit); bput(out,0); bput(out,0); done = 1; break; }
            int best_len = 0, best_dist = 0;
            if (i + 3 <= n) {
                int cand = head[hash3(d,i)]; int tries = 0;
                while (cand >= 0 && tries < 128) {
                    int dist = (int)i - cand;
                    if (dist > WINDOW) break;
                    int l = 0;
                    while (l < MAXMATCH && i+l < n && d[cand+l] == d[i+l]) l++;
                    if (l > best_len) { best_len = l; best_dist = dist; if (l == MAXMATCH) break; }
                    cand = prev[cand]; tries++;
                }
            }
            int idx = 0;
            for (int k = 17; k >= 0; k--) { if (lengths[k] && lengths[k] <= best_len) { idx = k; break; } }
            if (best_len >= 3) {
                int L = lengths[idx];
                flags |= (uint8_t)(1<<bit);
                bput(out, (uint8_t)((idx<<4)|((best_dist>>8)&0xf)));
                bput(out, (uint8_t)(best_dist & 0xff));
                for (int k = 0; k < L; k++) if (i+k+2 < n) { uint32_t h = hash3(d,i+k); prev[i+k] = head[h]; head[h] = (int32_t)(i+k); }
                i += L;
            } else {
                bput(out, d[i]);
                if (i+2 < n) { uint32_t h = hash3(d,i); prev[i] = head[h]; head[h] = (int32_t)i; }
                i++;
            }
        }
        out->p[flagpos] = flags;
    }
    if (!done) { bput(out, 0x01); bput(out, 0x00); bput(out, 0x00); }
    free(head); free(prev);
}

static void w32(FILE *f, uint32_t v) { fputc(v&0xff,f); fputc((v>>8)&0xff,f); fputc((v>>16)&0xff,f); fputc((v>>24)&0xff,f); }

int main(int argc, char **argv) {
    if (argc < 3) { fprintf(stderr, "usage: tpzl in.bin out.bin\n"); return 1; }
    FILE *f = fopen(argv[1], "rb"); if (!f) { perror("open in"); return 1; }
    fseek(f,0,SEEK_END); long sz = ftell(f); fseek(f,0,SEEK_SET);
    uint8_t *data = malloc(sz);
    if (fread(data,1,sz,f) != (size_t)sz) { fprintf(stderr,"read error\n"); return 1; }
    fclose(f);
    int nblocks = (int)((sz+BLOCK-1)/BLOCK);
    Buf *blocks = calloc(nblocks, sizeof(Buf));
    int nstore = 0;
    for (int b = 0; b < nblocks; b++) {
        size_t off = (size_t)b*BLOCK, blk = (off+BLOCK <= (size_t)sz) ? BLOCK : (size_t)sz-off;
        for (size_t s = 0; s < blk; s += SEG) {
            size_t sn = (s + SEG <= blk) ? SEG : blk - s;
            Buf lz = {0}; lz_segment(data+off+s, sn, &lz);
            if (lz.len > sn + 4) {
                nstore++;
                bput(&blocks[b], 0x0F); bput(&blocks[b], 0x00);
                bput(&blocks[b], (uint8_t)(sn & 0xff)); bput(&blocks[b], (uint8_t)((sn>>8)&0xff));
                bwrite(&blocks[b], data+off+s, sn);
                free(lz.p);
            } else {
                bwrite(&blocks[b], lz.p, lz.len);
                free(lz.p);
            }
        }
    }
    uint32_t tocOffset=24, tocSize=nblocks*8, dataOffset=tocOffset+tocSize;
    FILE *o = fopen(argv[2],"wb");
    fwrite("TPZL",1,4,o); w32(o,16); w32(o,tocOffset); w32(o,tocSize);
    for (int i=0;i<8;i++) fputc(0,o);
    uint32_t off = dataOffset;
    for (int b=0;b<nblocks;b++) { w32(o,off); w32(o,(uint32_t)blocks[b].len); off += blocks[b].len; }
    for (int b=0;b<nblocks;b++) fwrite(blocks[b].p,1,blocks[b].len,o);
    fclose(o);
    printf("blocks %d (store segs %d), in %ld, out %u\n", nblocks, nstore, sz, off);
    return 0;
}
