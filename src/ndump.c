// ndump.c - tiny static ARM binary, raw syscalls, no libc
typedef unsigned long u64;

static inline long sc(long n, long a, long b, long c) {
    register long r7 asm("r7") = n;
    register long r0 asm("r0") = a;
    register long r1 asm("r1") = b;
    register long r2 asm("r2") = c;
    asm volatile("svc 0" : "+r"(r0) : "r"(r7), "r"(r1), "r"(r2) : "memory");
    return r0;
}
static long slen(const char *s){ long n=0; while(s[n]) n++; return n; }
static void puts_(const char *s){ sc(4, 1, (long)s, slen(s)); }

void _start(void) {
    long *sp;
    asm volatile("mov %0, sp" : "=r"(sp));
    long argc = sp[0];
    char **argv = (char **)&sp[1];
    if (argc < 3) { puts_("usage: ndump <dev> <out>\n"); sc(1, 1, 0, 0); }
    const char *dev = argv[1];
    const char *out = argv[2];
    long in = sc(5, (long)dev, 0, 0);
    if (in < 0) { puts_("open dev failed\n"); sc(1, 1, 0, 0); }
    long of = sc(5, (long)out, 0x241, 0644);
    if (of < 0) { puts_("open out failed\n"); sc(1, 1, 0, 0); }
    static unsigned char buf[65536];
    u64 total = 0;
    for (;;) {
        long n = sc(3, in, (long)buf, sizeof buf);
        if (n <= 0) break;
        long w = 0;
        while (w < n) {
            long k = sc(4, of, (long)(buf + w), n - w);
            if (k <= 0) break;
            w += k;
        }
        total += n;
    }
    puts_("done\n");
    sc(1, 0, 0, 0);
}
