/* minimal preload test: write marker file */
static long sc(long n, long a, long b, long c) {
    register long r7 asm("r7") = n;
    register long r0 asm("r0") = a;
    register long r1 asm("r1") = b;
    register long r2 asm("r2") = c;
    asm volatile("svc 0" : "+r"(r0) : "r"(r7), "r"(r1), "r"(r2) : "memory");
    return r0;
}
static const char path[] = "/setting/ldtest.log";
static const char msg[]  = "ldtest loaded\n";
__attribute__((constructor)) static void ldtest_init(void) {
    long fd = sc(5, (long)path, 0x241, 0644); /* open O_WRONLY|O_CREAT|O_TRUNC */
    if (fd >= 0) {
        sc(4, fd, (long)msg, sizeof(msg) - 1);
        sc(6, fd, 0, 0);
    }
}
