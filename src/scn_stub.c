/* minimal scenario stub —— 只写一行日志，然后返回 0。
 * 用途：验证"替换 scenario 模块后能被加载并调用"这一条链路，
 * 不依赖任何外部文件（没有 dlopen），也不用 libsony 的库。
 */
static const char log_path[] = "/setting/scn_test.log";
static const char msg[]      = "stub: scenario_run called (no delegate)\n";

unsigned int sid = 0x010A0000u;   /* 与原模块一致 */

static long sc(long n, long a, long b, long c) {
    register long r7 asm("r7") = n;
    register long r0 asm("r0") = a;
    register long r1 asm("r1") = b;
    register long r2 asm("r2") = c;
    asm volatile("svc 0" : "+r"(r0) : "r"(r7), "r"(r1), "r"(r2) : "memory");
    return r0;
}

static int slen(const char *s) {
    int n = 0;
    while (s[n]) n++;
    return n;
}

int scenario_run(unsigned char *data, int size) {
    (void)data; (void)size;
    long fd = sc(5, (long)log_path, 0x441, 0644);   /* O_WRONLY|O_CREAT|O_APPEND */
    if (fd >= 0) {
        sc(4, fd, (long)msg, slen(msg));
        sc(6, fd, 0, 0);
    }
    return 0;
}
