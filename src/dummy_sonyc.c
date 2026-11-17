void *dlopen(const char *p, int m) { (void)p; (void)m; return 0; }
void *dlsym(void *h, const char *s) { (void)h; (void)s; return 0; }
char *dlerror(void) { return 0; }
