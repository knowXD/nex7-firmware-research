/* delegate stub v2 —— 先记日志，再把调用转发给原始 scenario 模块
 *
 * 与 v1 的差别（v1 是 nex7/hack/scn_delegate.c）：
 *   原模块 /setting/orig_video.so 不存在时，返回 0 而不是 -1。
 *   理由：我们无法在上层状态机上验证 -1 会走到哪条分支；
 *   返回 0（"当作已处理"）至少不会把状态机推进错误分支，
 *   录像本来就是坏的，但日志会明确写 "dlopen FAILED"。
 *
 * 日志路径 /setting/scn_test.log，用 O_APPEND，多次触发不会互相覆盖。
 */
extern void *dlopen(const char *path, int mode);
extern void *dlsym(void *handle, const char *name);

static const char orig_path[] = "/setting/orig_video.so";
static const char log_path[]  = "/setting/scn_test.log";

static const char m_enter[]  = "delegate: scenario_run entered\n";
static const char m_noopen[] = "delegate: dlopen(/setting/orig_video.so) FAILED -> return 0\n";
static const char m_nosym[]  = "delegate: dlsym(scenario_run) FAILED -> return 0\n";
static const char m_ok[]     = "delegate: original scenario_run called\n";

unsigned int sid = 0x010A0000u;

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

static void logmsg(const char *s) {
    long len = slen(s);
    long fd = sc(5, (long)log_path, 0x441, 0644);  /* O_WRONLY|O_CREAT|O_APPEND */
    if (fd >= 0) {
        sc(4, fd, (long)s, len);
        sc(6, fd, 0, 0);
    }
}

int scenario_run(unsigned char *data, int size) {
    logmsg(m_enter);

    void *h = dlopen(orig_path, 1);   /* RTLD_LAZY */
    if (!h) {
        logmsg(m_noopen);
        return 0;
    }

    int (*fn)(unsigned char *, int) = (int (*)(unsigned char *, int))dlsym(h, "scenario_run");
    if (!fn) {
        logmsg(m_nosym);
        return 0;
    }

    logmsg(m_ok);
    return fn(data, size);
}
