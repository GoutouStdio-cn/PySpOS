/*
 * splibc - PySpOS C 标准库实现
 */

#include "splibc.h"

/* ==================== 字符串函数实现 ==================== */

size_t strlen(const char *s) {
    size_t len = 0;
    while (s[len]) len++;
    return len;
}

char *strcpy(char *dest, const char *src) {
    char *ret = dest;
    while ((*dest++ = *src++));
    return ret;
}

char *strncpy(char *dest, const char *src, size_t n) {
    char *ret = dest;
    while (n && (*dest++ = *src++)) n--;
    while (n--) *dest++ = '\0';
    return ret;
}

char *strcat(char *dest, const char *src) {
    char *ret = dest;
    while (*dest) dest++;
    while ((*dest++ = *src++));
    return ret;
}

int strcmp(const char *s1, const char *s2) {
    while (*s1 && (*s1 == *s2)) {
        s1++;
        s2++;
    }
    return *(unsigned char*)s1 - *(unsigned char*)s2;
}

int strncmp(const char *s1, const char *s2, size_t n) {
    while (n && *s1 && (*s1 == *s2)) {
        s1++;
        s2++;
        n--;
    }
    if (n == 0) return 0;
    return *(unsigned char*)s1 - *(unsigned char*)s2;
}

char *strchr(const char *s, int c) {
    while (*s) {
        if (*s == (char)c) return (char*)s;
        s++;
    }
    return NULL;
}

char *strstr(const char *haystack, const char *needle) {
    size_t needle_len = strlen(needle);
    if (needle_len == 0) return (char*)haystack;
    
    while (*haystack) {
        if (*haystack == *needle && 
            strncmp(haystack, needle, needle_len) == 0) {
            return (char*)haystack;
        }
        haystack++;
    }
    return NULL;
}

/* ==================== 内存函数实现 ==================== */

void *memset(void *s, int c, size_t n) {
    unsigned char *p = (unsigned char*)s;
    while (n--) *p++ = (unsigned char)c;
    return s;
}

void *memcpy(void *dest, const void *src, size_t n) {
    unsigned char *d = (unsigned char*)dest;
    const unsigned char *s = (const unsigned char*)src;
    while (n--) *d++ = *s++;
    return dest;
}

void *memmove(void *dest, const void *src, size_t n) {
    unsigned char *d = (unsigned char*)dest;
    const unsigned char *s = (const unsigned char*)src;
    
    if (d < s) {
        while (n--) *d++ = *s++;
    } else {
        d += n;
        s += n;
        while (n--) *--d = *--s;
    }
    return dest;
}

int memcmp(const void *s1, const void *s2, size_t n) {
    const unsigned char *p1 = (const unsigned char*)s1;
    const unsigned char *p2 = (const unsigned char*)s2;
    
    while (n--) {
        if (*p1 != *p2) return *p1 - *p2;
        p1++;
        p2++;
    }
    return 0;
}

/* ==================== 标准 I/O 函数实现 ==================== */

ssize_t write(int fd, const void *buf, size_t count) {
    return syscall3(SYS_write, fd, (long)buf, count);
}

ssize_t read(int fd, void *buf, size_t count) {
    return syscall3(SYS_read, fd, (long)buf, count);
}

int open(const char *pathname, int flags, ...) {
    return syscall2(SYS_open, (long)pathname, flags);
}

int close(int fd) {
    return syscall1(SYS_close, fd);
}

off_t lseek(int fd, off_t offset, int whence) {
    return syscall3(SYS_lseek, fd, offset, whence);
}

/* ==================== 进程函数实现 ==================== */

void exit(int status) {
    syscall1(SYS_exit, status);
    __builtin_unreachable();
}

pid_t getpid(void) {
    return syscall1(39, 0);
}

/* ==================== 输出函数实现 ==================== */

int puts(const char *s) {
    size_t len = strlen(s);
    write(STDOUT_FILENO, s, len);
    write(STDOUT_FILENO, "\n", 1);
    return len + 1;
}

int putchar(int c) {
    char ch = (char)c;
    write(STDOUT_FILENO, &ch, 1);
    return c;
}

/* 简单的整数转字符串 */
static void itoa(long value, char *buf, int base) {
    char *p = buf;
    int is_negative = 0;
    
    if (value < 0 && base == 10) {
        is_negative = 1;
        value = -value;
    }
    
    if (value == 0) {
        *p++ = '0';
    } else {
        while (value) {
            int digit = value % base;
            *p++ = (digit < 10) ? ('0' + digit) : ('a' + digit - 10);
            value /= base;
        }
    }
    
    if (is_negative) *p++ = '-';
    *p = '\0';
    
    /* 反转字符串 */
    char *start = buf;
    char *end = p - 1;
    while (start < end) {
        char tmp = *start;
        *start++ = *end;
        *end-- = tmp;
    }
}

/* 简单的 printf 实现 */
int printf(const char *format, ...) {
    __builtin_va_list args;
    __builtin_va_start(args, format);
    
    int count = 0;
    char buf[32];
    
    while (*format) {
        if (*format == '%') {
            format++;
            
            switch (*format) {
                case 'd':
                case 'i': {
                    long val = __builtin_va_arg(args, int);
                    itoa(val, buf, 10);
                    write(STDOUT_FILENO, buf, strlen(buf));
                    count += strlen(buf);
                    break;
                }
                case 'l': {
                    format++;
                    if (*format == 'd') {
                        long val = __builtin_va_arg(args, long);
                        itoa(val, buf, 10);
                        write(STDOUT_FILENO, buf, strlen(buf));
                        count += strlen(buf);
                    }
                    break;
                }
                case 'x': {
                    unsigned long val = __builtin_va_arg(args, unsigned int);
                    itoa(val, buf, 16);
                    write(STDOUT_FILENO, buf, strlen(buf));
                    count += strlen(buf);
                    break;
                }
                case 's': {
                    const char *s = __builtin_va_arg(args, const char*);
                    if (s == NULL) s = "(null)";
                    write(STDOUT_FILENO, s, strlen(s));
                    count += strlen(s);
                    break;
                }
                case 'c': {
                    char c = (char)__builtin_va_arg(args, int);
                    write(STDOUT_FILENO, &c, 1);
                    count++;
                    break;
                }
                case '%': {
                    write(STDOUT_FILENO, "%", 1);
                    count++;
                    break;
                }
                default:
                    break;
            }
        } else {
            write(STDOUT_FILENO, format, 1);
            count++;
        }
        format++;
    }
    
    __builtin_va_end(args);
    return count;
}

int sprintf(char *str, const char *format, ...) {
    __builtin_va_list args;
    __builtin_va_start(args, format);
    
    char *p = str;
    char buf[32];
    
    while (*format) {
        if (*format == '%') {
            format++;
            
            switch (*format) {
                case 'd':
                case 'i': {
                    long val = __builtin_va_arg(args, int);
                    itoa(val, buf, 10);
                    strcpy(p, buf);
                    p += strlen(buf);
                    break;
                }
                case 's': {
                    const char *s = __builtin_va_arg(args, const char*);
                    if (s == NULL) s = "(null)";
                    strcpy(p, s);
                    p += strlen(s);
                    break;
                }
                case 'c': {
                    *p++ = (char)__builtin_va_arg(args, int);
                    break;
                }
                case '%': {
                    *p++ = '%';
                    break;
                }
                default:
                    break;
            }
        } else {
            *p++ = *format;
        }
        format++;
    }
    
    *p = '\0';
    __builtin_va_end(args);
    return p - str;
}

/* ==================== 内存分配函数实现 ==================== */

static void *heap_start = NULL;
static void *heap_end = NULL;

void *malloc(size_t size) {
    if (heap_start == NULL) {
        heap_start = (void*)syscall1(SYS_brk, 0);
        heap_end = heap_start;
    }
    
    size = (size + 15) & ~15;
    
    void *new_brk = (char*)heap_end + size;
    void *result = (void*)syscall1(SYS_brk, (long)new_brk);
    
    if (result != new_brk) return NULL;
    
    void *ptr = heap_end;
    heap_end = new_brk;
    return ptr;
}

void free(void *ptr) {
    /* 简单实现：不回收内存 */
    (void)ptr;
}

void *realloc(void *ptr, size_t size) {
    if (ptr == NULL) return malloc(size);
    if (size == 0) {
        free(ptr);
        return NULL;
    }
    
    void *new_ptr = malloc(size);
    if (new_ptr == NULL) return NULL;
    
    memcpy(new_ptr, ptr, size);
    return new_ptr;
}

void *calloc(size_t nmemb, size_t size) {
    size_t total = nmemb * size;
    void *ptr = malloc(total);
    if (ptr) memset(ptr, 0, total);
    return ptr;
}

/* ==================== 程序入口点 ==================== */

/* 
 * 注意：_start 需要用户程序自己定义
 * 如果想使用 main 函数，可以这样定义：
 * 
 * extern int main(void);
 * void _start(void) {
 *     int ret = main();
 *     exit(ret);
 * }
 */
