// zebra_v1.c - LD_PRELOAD marker, no libc
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

__attribute__((constructor)) static void init(void) {
    long fd = sc3(5, (long)"/setting/zebra.txt", O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (fd >= 0) {
        sc3(4, fd, (long)"preload ok\n", 11);
        sc3(6, fd, 0, 0);
    }
}
