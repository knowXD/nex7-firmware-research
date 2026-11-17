// zebra_v3.c - maps-based, no weak symbols
#define O_RDONLY 0
#define O_WRONLY 1
#define O_CREAT 64
#define O_TRUNC 512

static long sc3(long n, long a, long b, long c) {
    register long r7 __asm__("r7") = n;
    register long r0 __asm__("r0") = a;
    register long r1 __asm__("r1") = b;
    register long r2 __asm__("r2") = c;
    __asm__ volatile("svc 0" : "+r"(r0) : "r"(r1), "r"(r2), "r"(r7) : "memory");
    return r0;
}

static void logmsg(const char *s, int len) {
    long fd = sc3(5, (long)"/setting/zebra.txt", O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (fd >= 0) { sc3(4, fd, (long)s, len); sc3(6, fd, 0, 0); }
}

static int has_name(const char *p, const char *e, const char *name, int nlen) {
    for (const char *q = p; q + nlen <= e; q++) {
        int ok = 1;
        for (int i = 0; i < nlen; i++) if (q[i] != name[i]) { ok = 0; break; }
        if (ok) return 1;
    }
    return 0;
}

static unsigned long find_base(void) {
    static char buf[65536];
    long fd = sc3(5, (long)"/proc/self/maps", O_RDONLY, 0);
    if (fd < 0) return 0;
    long n = sc3(3, fd, (long)buf, 65535);
    sc3(6, fd, 0, 0);
    if (n <= 0) return 0;
    buf[n] = 0;

    const char *name = "libBaseClass.so";
    int nlen = 14;
    unsigned long best = 0;
    char *p = buf;
    while (*p) {
        char *e = p;
        while (*e && *e != '\n') e++;
        if (has_name(p, e, name, nlen)) {
            unsigned long v = 0;
            for (char *q = p; *q && *q != '-'; q++) {
                int c = *q, d;
                if (c >= '0' && c <= '9') d = c - '0';
                else if (c >= 'a' && c <= 'f') d = c - 'a' + 10;
                else if (c >= 'A' && c <= 'F') d = c - 'A' + 10;
                else break;
                v = (v << 4) | (unsigned)d;
            }
            if (v && (best == 0 || v < best)) best = v;
        }
        p = (*e) ? e + 1 : e;
    }
    return best;
}

__attribute__((constructor)) static void init(void) {
    unsigned long base = find_base();
    if (!base) return;

    struct { long sec; long nsec; } ts = { 4, 0 };
    sc3(162, (long)&ts, 0, 0);

    typedef void (*ctor_t)(void *, unsigned short);
    typedef int  (*set_t)(void *, const void *);
    ctor_t ctor = (ctor_t)(base + 0x199b5);
    set_t  setz = (set_t)(base + 0x1bbc5);

    static unsigned char obj[256];
    unsigned char prm[16];
    for (int i = 0; i < 16; i++) prm[i] = 0;
    prm[8] = 1;
    prm[9] = 80;
    prm[10] = 1;

    ctor(obj, 0);
    setz(obj, prm);
    logmsg("zebra v3 done\n", 14);
}
