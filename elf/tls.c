extern __thread int ext_gd;
extern __thread int ext_ie __attribute__((tls_model("initial-exec")));
int get_gd(void) { return ext_gd; }
int get_ie(void) { return ext_ie; }
