#ifdef __PYSPOS__
#include "../splibc.h"
#else
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <stdbool.h>
#include <stdint.h>
#include <errno.h>
#include <limits.h>
#include <spaceapi.h>
#include <fcntl.h>
#endif

#define ENV_INITIAL_SIZE 32
#define ENV_GROW_FACTOR 2

typedef struct {
    char *name;
    char *value;
} env_var_t;

static env_var_t *env_vars = NULL;
static size_t env_count = 0;
static size_t env_capacity = 0;
static bool env_initialized = false;

#ifdef __PYSPOS__
static void env_lock(void) {}
static void env_unlock(void) {}
#else
static int env_mutex = -1;
static void env_lock(void) {
    if (env_mutex >= 0) sp_mutex_lock(env_mutex);
}
static void env_unlock(void) {
    if (env_mutex >= 0) sp_mutex_unlock(env_mutex);
}
#endif

static void init_env_system(void)
{
    if (env_initialized) {
        return;
    }
#ifndef __PYSPOS__
    env_mutex = sp_mutex_create();
    if (env_mutex < 0) {
        env_mutex = -1;
    }
#endif
    env_capacity = ENV_INITIAL_SIZE;
    env_vars = (env_var_t *)malloc(sizeof(env_var_t) * env_capacity);
    if (env_vars) {
        memset(env_vars, 0, sizeof(env_var_t) * env_capacity);
    }
    env_initialized = true;
}

static int env_grow(void)
{
    size_t new_capacity = env_capacity * ENV_GROW_FACTOR;
    env_var_t *new_vars = (env_var_t *)realloc(env_vars, sizeof(env_var_t) * new_capacity);
    if (!new_vars) {
        return -1;
    }
    memset(&new_vars[env_capacity], 0, sizeof(env_var_t) * (new_capacity - env_capacity));
    env_vars = new_vars;
    env_capacity = new_capacity;
    return 0;
}

static int find_env_index(const char *name)
{
    if (!name || !env_vars) {
        return -1;
    }
    for (size_t i = 0; i < env_count; i++) {
        if (env_vars[i].name && strcmp(env_vars[i].name, name) == 0) {
            return (int)i;
        }
    }
    return -1;
}

void exit(int status)
{
#ifdef __PYSPOS__
    syscall1(SYS_exit, status);
#else
    sp_exit(status);
#endif
    while(1);
}

void abort(void)
{
    exit(EXIT_FAILURE);
}

int atoi(const char *nptr)
{
    return (int)strtol(nptr, NULL, 10);
}

long atol(const char *nptr)
{
    return strtol(nptr, NULL, 10);
}

long long atoll(const char *nptr)
{
    return strtoll(nptr, NULL, 10);
}

static double parse_fraction(const char **p)
{
    double result = 0.0;
    double divisor = 10.0;
    while (**p >= '0' && **p <= '9') {
        result += (**p - '0') / divisor;
        divisor *= 10.0;
        (*p)++;
    }
    return result;
}

static double parse_exponent(const char **p)
{
    int exp_sign = 1;
    int exp_val = 0;
    if (**p == '+' || **p == '-') {
        exp_sign = (**p == '-') ? -1 : 1;
        (*p)++;
    }
    while (**p >= '0' && **p <= '9') {
        exp_val = exp_val * 10 + (**p - '0');
        (*p)++;
    }
    double result = 1.0;
    double base = 10.0;
    int exp = exp_sign * exp_val;
    if (exp < 0) {
        exp = -exp;
        base = 0.1;
    }
    while (exp > 0) {
        if (exp & 1) {
            result *= base;
        }
        base *= base;
        exp >>= 1;
    }
    return result;
}

double strtod(const char *nptr, char **endptr)
{
    const char *p = nptr;
    double result = 0.0;
    int sign = 1;
    bool has_digits = false;
    while (isspace((unsigned char)*p)) {
        p++;
    }
    if (*p == '-') {
        sign = -1;
        p++;
    } else if (*p == '+') {
        p++;
    }
    while (*p >= '0' && *p <= '9') {
        result = result * 10.0 + (*p - '0');
        has_digits = true;
        p++;
    }
    if (*p == '.') {
        p++;
        double frac = parse_fraction(&p);
        result += frac;
        if (frac > 0) {
            has_digits = true;
        }
    }
    if (*p == 'e' || *p == 'E') {
        p++;
        double exp = parse_exponent(&p);
        result *= exp;
    }
    if (!has_digits) {
        if (strncasecmp(p, "inf", 3) == 0) {
            p += 3;
            if (strncasecmp(p, "inity", 5) == 0) {
                p += 5;
            }
            result = sign * (1.0 / 0.0);
        } else if (strncasecmp(p, "nan", 3) == 0) {
            p += 3;
            result = 0.0 / 0.0;
        } else {
            if (endptr) {
                *endptr = (char *)nptr;
            }
            return 0.0;
        }
    } else {
        result *= sign;
    }
    if (endptr) {
        *endptr = (char *)p;
    }
    return result;
}

double atof(const char *nptr)
{
    return strtod(nptr, NULL);
}

long strtol(const char *nptr, char **endptr, int base)
{
    long result = 0;
    int sign = 1;
    const char *p = nptr;
    bool overflow = false;
    while (isspace((unsigned char)*p)) {
        p++;
    }
    if (*p == '-') {
        sign = -1;
        p++;
    } else if (*p == '+') {
        p++;
    }
    if (base == 0) {
        if (*p == '0') {
            p++;
            if (*p == 'x' || *p == 'X') {
                base = 16;
                p++;
            } else {
                base = 8;
            }
        } else {
            base = 10;
        }
    } else if (base == 16) {
        if (*p == '0' && (*(p + 1) == 'x' || *(p + 1) == 'X')) {
            p += 2;
        }
    }
    while (*p) {
        int digit;
        if (*p >= '0' && *p <= '9') {
            digit = *p - '0';
        } else if (*p >= 'a' && *p <= 'z') {
            digit = *p - 'a' + 10;
        } else if (*p >= 'A' && *p <= 'Z') {
            digit = *p - 'A' + 10;
        } else {
            break;
        }
        if (digit >= base) {
            break;
        }
        if (result > (LONG_MAX - digit) / base) {
            overflow = true;
        }
        result = result * base + digit;
        p++;
    }
    if (endptr) {
        *endptr = (char *)p;
    }
    if (overflow) {
        errno = ERANGE;
        return (sign == 1) ? LONG_MAX : LONG_MIN;
    }
    return result * sign;
}

unsigned long strtoul(const char *nptr, char **endptr, int base)
{
    unsigned long result = 0;
    const char *p = nptr;
    bool overflow = false;
    while (isspace((unsigned char)*p)) {
        p++;
    }
    if (*p == '+') {
        p++;
    }
    if (base == 0) {
        if (*p == '0') {
            p++;
            if (*p == 'x' || *p == 'X') {
                base = 16;
                p++;
            } else {
                base = 8;
            }
        } else {
            base = 10;
        }
    } else if (base == 16) {
        if (*p == '0' && (*(p + 1) == 'x' || *(p + 1) == 'X')) {
            p += 2;
        }
    }
    while (*p) {
        int digit;
        if (*p >= '0' && *p <= '9') {
            digit = *p - '0';
        } else if (*p >= 'a' && *p <= 'z') {
            digit = *p - 'a' + 10;
        } else if (*p >= 'A' && *p <= 'Z') {
            digit = *p - 'A' + 10;
        } else {
            break;
        }
        if (digit >= base) {
            break;
        }
        if (result > (ULONG_MAX - digit) / base) {
            overflow = true;
        }
        result = result * base + digit;
        p++;
    }
    if (endptr) {
        *endptr = (char *)p;
    }
    if (overflow) {
        errno = ERANGE;
        return ULONG_MAX;
    }
    return result;
}

long long strtoll(const char *nptr, char **endptr, int base)
{
    long long result = 0;
    int sign = 1;
    const char *p = nptr;
    bool overflow = false;
    while (isspace((unsigned char)*p)) {
        p++;
    }
    if (*p == '-') {
        sign = -1;
        p++;
    } else if (*p == '+') {
        p++;
    }
    if (base == 0) {
        if (*p == '0') {
            p++;
            if (*p == 'x' || *p == 'X') {
                base = 16;
                p++;
            } else {
                base = 8;
            }
        } else {
            base = 10;
        }
    } else if (base == 16) {
        if (*p == '0' && (*(p + 1) == 'x' || *(p + 1) == 'X')) {
            p += 2;
        }
    }
    while (*p) {
        int digit;
        if (*p >= '0' && *p <= '9') {
            digit = *p - '0';
        } else if (*p >= 'a' && *p <= 'z') {
            digit = *p - 'a' + 10;
        } else if (*p >= 'A' && *p <= 'Z') {
            digit = *p - 'A' + 10;
        } else {
            break;
        }
        if (digit >= base) {
            break;
        }
        if (result > (LLONG_MAX - digit) / base) {
            overflow = true;
        }
        result = result * base + digit;
        p++;
    }
    if (endptr) {
        *endptr = (char *)p;
    }
    if (overflow) {
        errno = ERANGE;
        return (sign == 1) ? LLONG_MAX : LLONG_MIN;
    }
    return result * sign;
}

unsigned long long strtoull(const char *nptr, char **endptr, int base)
{
    unsigned long long result = 0;
    const char *p = nptr;
    bool overflow = false;
    while (isspace((unsigned char)*p)) {
        p++;
    }
    if (*p == '+') {
        p++;
    }
    if (base == 0) {
        if (*p == '0') {
            p++;
            if (*p == 'x' || *p == 'X') {
                base = 16;
                p++;
            } else {
                base = 8;
            }
        } else {
            base = 10;
        }
    } else if (base == 16) {
        if (*p == '0' && (*(p + 1) == 'x' || *(p + 1) == 'X')) {
            p += 2;
        }
    }
    while (*p) {
        int digit;
        if (*p >= '0' && *p <= '9') {
            digit = *p - '0';
        } else if (*p >= 'a' && *p <= 'z') {
            digit = *p - 'a' + 10;
        } else if (*p >= 'A' && *p <= 'Z') {
            digit = *p - 'A' + 10;
        } else {
            break;
        }
        if (digit >= base) {
            break;
        }
        if (result > (ULLONG_MAX - digit) / base) {
            overflow = true;
        }
        result = result * base + digit;
        p++;
    }
    if (endptr) {
        *endptr = (char *)p;
    }
    if (overflow) {
        errno = ERANGE;
        return ULLONG_MAX;
    }
    return result;
}

int abs(int j)
{
    return j < 0 ? -j : j;
}

long labs(long j)
{
    return j < 0 ? -j : j;
}

long long llabs(long long j)
{
    return j < 0 ? -j : j;
}

div_t div(int numer, int denom)
{
    div_t result;
    result.quot = numer / denom;
    result.rem = numer % denom;
    return result;
}

ldiv_t ldiv(long numer, long denom)
{
    ldiv_t result;
    result.quot = numer / denom;
    result.rem = numer % denom;
    return result;
}

lldiv_t lldiv(long long numer, long long denom)
{
    lldiv_t result;
    result.quot = numer / denom;
    result.rem = numer % denom;
    return result;
}

#define RAND_A 1103515245
#define RAND_C 12345
#define RAND_M 2147483648

static unsigned long rand_state = 1;

int rand(void)
{
    rand_state = (RAND_A * rand_state + RAND_C) % RAND_M;
    return (int)(rand_state & RAND_MAX);
}

void srand(unsigned int seed)
{
    rand_state = seed;
}

static void swap(void *a, void *b, size_t size)
{
    unsigned char *pa = a;
    unsigned char *pb = b;
    while (size--) {
        unsigned char tmp = *pa;
        *pa++ = *pb;
        *pb++ = tmp;
    }
}

typedef struct {
    size_t left;
    size_t right;
} qsort_stack_t;

#define QSORT_STACK_SIZE 64

void qsort(void *base, size_t nmemb, size_t size, int (*compar)(const void *, const void *))
{
    if (nmemb <= 1 || size == 0 || !base || !compar) {
        return;
    }
    char *arr = base;
    qsort_stack_t stack[QSORT_STACK_SIZE];
    int stack_ptr = 0;
    stack[stack_ptr].left = 0;
    stack[stack_ptr].right = nmemb - 1;
    stack_ptr++;
    while (stack_ptr > 0) {
        stack_ptr--;
        size_t left = stack[stack_ptr].left;
        size_t right = stack[stack_ptr].right;
        if (left >= right) {
            continue;
        }
        size_t pivot_idx = left + (right - left) / 2;
        size_t i = left;
        size_t j = right;
        swap(arr + pivot_idx * size, arr + j * size, size);
        pivot_idx = j;
        while (i < j) {
            while (i < j && compar(arr + i * size, arr + pivot_idx * size) <= 0) {
                i++;
            }
            while (i < j && compar(arr + j * size, arr + pivot_idx * size) >= 0) {
                j--;
            }
            if (i < j) {
                swap(arr + i * size, arr + j * size, size);
            }
        }
        swap(arr + i * size, arr + pivot_idx * size, size);
        if (i > left) {
            stack[stack_ptr].left = left;
            stack[stack_ptr].right = i - 1;
            stack_ptr++;
        }
        if (i + 1 < right) {
            stack[stack_ptr].left = i + 1;
            stack[stack_ptr].right = right;
            stack_ptr++;
        }
    }
}

void *bsearch(const void *key, const void *base, size_t nmemb, size_t size, int (*compar)(const void *, const void *))
{
    if (!key || !base || nmemb == 0 || size == 0 || !compar) {
        return NULL;
    }
    const char *arr = base;
    size_t left = 0;
    size_t right = nmemb;
    while (left < right) {
        size_t mid = left + (right - left) / 2;
        int cmp = compar(key, arr + mid * size);
        if (cmp == 0) {
            return (void *)(arr + mid * size);
        } else if (cmp < 0) {
            right = mid;
        } else {
            left = mid + 1;
        }
    }
    return NULL;
}

char *getenv(const char *name)
{
    if (!name || *name == '\0') {
        return NULL;
    }
    init_env_system();
    env_lock();
    int idx = find_env_index(name);
    char *result = (idx >= 0) ? env_vars[idx].value : NULL;
    env_unlock();
    return result;
}

int setenv(const char *name, const char *value, int overwrite)
{
    if (!name || *name == '\0' || strchr(name, '=') != NULL) {
        errno = EINVAL;
        return -1;
    }
    init_env_system();
    env_lock();
    int idx = find_env_index(name);
    if (idx >= 0 && !overwrite) {
        env_unlock();
        return 0;
    }
    if (idx >= 0) {
        free(env_vars[idx].value);
        env_vars[idx].value = value ? strdup(value) : strdup("");
        if (!env_vars[idx].value) {
            env_unlock();
            errno = ENOMEM;
            return -1;
        }
    } else {
        if (env_count >= env_capacity) {
            if (env_grow() < 0) {
                env_unlock();
                errno = ENOMEM;
                return -1;
            }
        }
        env_vars[env_count].name = strdup(name);
        env_vars[env_count].value = value ? strdup(value) : strdup("");
        if (!env_vars[env_count].name || !env_vars[env_count].value) {
            free(env_vars[env_count].name);
            free(env_vars[env_count].value);
            env_unlock();
            errno = ENOMEM;
            return -1;
        }
        env_count++;
    }
    env_unlock();
    return 0;
}

int unsetenv(const char *name)
{
    if (!name || *name == '\0') {
        errno = EINVAL;
        return -1;
    }
    init_env_system();
    env_lock();
    int idx = find_env_index(name);
    if (idx >= 0) {
        free(env_vars[idx].name);
        free(env_vars[idx].value);
        for (size_t i = idx; i < env_count - 1; i++) {
            env_vars[i] = env_vars[i + 1];
        }
        env_count--;
        memset(&env_vars[env_count], 0, sizeof(env_var_t));
    }
    env_unlock();
    return 0;
}

int putenv(char *string)
{
    if (!string || *string == '\0') {
        errno = EINVAL;
        return -1;
    }
    char *eq = strchr(string, '=');
    if (!eq) {
        errno = EINVAL;
        return -1;
    }
    size_t name_len = (size_t)(eq - string);
    char *name = (char *)malloc(name_len + 1);
    if (!name) {
        errno = ENOMEM;
        return -1;
    }
    strncpy(name, string, name_len);
    name[name_len] = '\0';
    int result = setenv(name, eq + 1, 1);
    free(name);
    return result;
}

int system(const char *command)
{
    if (!command) {
        return 1;
    }
#ifdef __PYSPOS__
    return -1;
#else
    return sp_system(command);
#endif
}

void *aligned_alloc(size_t alignment, size_t size)
{
    if (alignment == 0 || (alignment & (alignment - 1)) != 0) {
        errno = EINVAL;
        return NULL;
    }
    if (size % alignment != 0) {
        size = ((size + alignment - 1) / alignment) * alignment;
    }
    void *ptr = malloc(size + alignment + sizeof(void *));
    if (!ptr) {
        return NULL;
    }
    uintptr_t addr = (uintptr_t)ptr;
    uintptr_t aligned_addr = (addr + alignment + sizeof(void *)) & ~(alignment - 1);
    void **header = (void **)(aligned_addr - sizeof(void *));
    *header = ptr;
    return (void *)aligned_addr;
}

int posix_memalign(void **memptr, size_t alignment, size_t size)
{
    if (!memptr) {
        return EINVAL;
    }
    if (alignment == 0 || (alignment & (alignment - 1)) != 0) {
        return EINVAL;
    }
    void *ptr = aligned_alloc(alignment, size);
    if (!ptr) {
        return ENOMEM;
    }
    *memptr = ptr;
    return 0;
}

char *mktemp(char *template)
{
    if (!template) {
        errno = EINVAL;
        return NULL;
    }
    size_t len = strlen(template);
    if (len < 6 || strcmp(template + len - 6, "XXXXXX") != 0) {
        errno = EINVAL;
        return NULL;
    }
    static unsigned long temp_counter = 0;
    for (int attempt = 0; attempt < 100; attempt++) {
        unsigned long value = temp_counter++;
        for (int i = 0; i < 6; i++) {
            int digit = value % 36;
            char c = (digit < 10) ? '0' + digit : 'A' + (digit - 10);
            template[len - 6 + i] = c;
            value /= 36;
        }
#ifdef __PYSPOS__
        int fd = syscall3(SYS_open, (long)template, O_RDONLY, 0);
        if (fd < 0) {
            return template;
        }
        syscall1(SYS_close, fd);
#else
        int fd = sp_open(template, O_RDONLY, 0);
        if (fd < 0) {
            return template;
        }
        sp_close(fd);
#endif
    }
    errno = EEXIST;
    return NULL;
}

int mkstemp(char *template)
{
    char *name = mktemp(template);
    if (!name) {
        return -1;
    }
#ifdef __PYSPOS__
    int fd = syscall3(SYS_open, (long)name, O_RDWR | O_CREAT | O_EXCL, 0600);
#else
    int fd = sp_open(name, O_RDWR | O_CREAT | O_EXCL, 0600);
#endif
    if (fd < 0) {
        errno = EEXIST;
        return -1;
    }
    return fd;
}
