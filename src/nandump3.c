// nandump3.c - dump a device to a file: usage: nandump3 <device> <outfile>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/fs.h>
#include <stdint.h>

static uint32_t table[256];
static void crc_init(void) {
    for (uint32_t i = 0; i < 256; i++) {
        uint32_t c = i;
        for (int k = 0; k < 8; k++) c = (c & 1) ? 0xEDB88320u ^ (c >> 1) : c >> 1;
        table[i] = c;
    }
}
static uint32_t crc32(const void *buf, size_t n, uint32_t crc) {
    const uint8_t *p = buf;
    for (size_t i = 0; i < n; i++) crc = table[(crc ^ p[i]) & 0xff] ^ (crc >> 8);
    return crc;
}

int main(int argc, char **argv) {
    if (argc < 3) { fprintf(stderr, "usage: nandump3 <device> <outfile>\n"); return 1; }
    int fd = open(argv[1], O_RDONLY);
    if (fd < 0) { perror(argv[1]); return 1; }
    unsigned long long size = 0;
    if (ioctl(fd, BLKGETSIZE64, &size) != 0 || size == 0) {
        size = lseek(fd, 0, SEEK_END);
        lseek(fd, 0, SEEK_SET);
    }
    printf("%s size=%llu\n", argv[1], size);
    FILE *o = fopen(argv[2], "wb");
    if (!o) { perror(argv[2]); close(fd); return 1; }
    static uint8_t buf[65536];
    ssize_t r; unsigned long long total = 0; uint32_t crc = 0xffffffffu;
    crc_init();
    while ((r = read(fd, buf, sizeof buf)) > 0) {
        if (fwrite(buf, 1, (size_t)r, o) != (size_t)r) break;
        crc = crc32(buf, (size_t)r, crc);
        total += (uint64_t)r;
    }
    fclose(o); close(fd);
    printf("done %s %llu crc=%08x\n", argv[2], total, crc ^ 0xffffffffu);
    return 0;
}
