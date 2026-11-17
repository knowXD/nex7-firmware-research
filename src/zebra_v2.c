// zebra_v2.c - weak symbol resolution, no libc, no maps parsing
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

extern void vdf_ctor(void *, unsigned short)
    __attribute__((weak)) __asm__("_ZN17OBJAVBBCBASECLASS5VdfChC1Et");
extern int vdf_set_zebra(void *, const void *)
    __attribute__((weak)) __asm__("_ZN17OBJAVBBCBASECLASS5VdfCh8setZebraERKN3VDF22VDF_PRM_SRVC_SET_ZEBRAE");

__attribute__((constructor)) static void init(void) {
    // only act in processes that actually loaded libBaseClass
    if (!vdf_ctor || !vdf_set_zebra) return;

    struct { long sec; long nsec; } ts = { 4, 0 };
    sc3(162, (long)&ts, 0, 0);   // nanosleep, let the app finish init

    static unsigned char obj[256];
    unsigned char prm[16];
    for (int i = 0; i < 16; i++) prm[i] = 0;
    prm[8] = 1;    // onoff
    prm[9] = 80;   // gray threshold
    prm[10] = 1;   // disp

    vdf_ctor(obj, 0);
    vdf_set_zebra(obj, prm);
    logmsg("zebra v2 done\n", 14);
}
