// nandump.c - dump Sony NEX-7 NAND partitions from updater mode
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <sys/stat.h>
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

static int dump_one(const char *dev, const char *out) {
    int fd = open(dev, O_RDONLY);
    if (fd < 0) return -1;
    unsigned long long size = 0;
    if (ioctl(fd, BLKGETSIZE64, &size) != 0 || size == 0) {
        size = lseek(fd, 0, SEEK_END);
        lseek(fd, 0, SEEK_SET);
    }
    FILE *o = fopen(out, "wb");
    if (!o) { close(fd); return -1; }
    static uint8_t buf[65536];
    ssize_t n; unsigned long long total = 0; uint32_t crc = 0xffffffffu;
    while ((n = read(fd, buf, sizeof buf)) > 0) {
        if (fwrite(buf, 1, (size_t)n, o) != (size_t)n) break;
        crc = crc32(buf, (size_t)n, crc);
        total += (unsigned long long)n;
    }
    fclose(o); close(fd);
    printf("%s,%llu,%08x\n", out, total, crc ^ 0xffffffffu);
    fflush(stdout);
    return 0;
}

int main(int argc, char **argv) {
    const char *dir = (argc > 1) ? argv[1] : "/tmp/dump";
    mkdir(dir, 0777);
    crc_init();
    char dev[64], out[160];
    for (int i = 1; i <= 8; i++) {
        snprintf(dev, sizeof dev, "/dev/nflasha%d", i);
        snprintf(out, sizeof out, "%s/nflasha%d.bin", dir, i);
        if (access(dev, R_OK) == 0) dump_one(dev, out);
    }
    return 0;
}
