#ifdef __PYSPOS__
#include "../splibc.h"
#else
#include <string.h>
#include <stdlib.h>
#include <stdint.h>
#include <ctype.h>
#endif

/* ============================================================================
 * 内存操作函数
 * ============================================================================ */

void *memcpy(void *dest, const void *src, size_t n)
{
    unsigned char *d = dest;
    const unsigned char *s = src;

    /* 处理空指针或零长度 */
    if (!dest || !src || n == 0) {
        return dest;
    }
    /* 字节级复制 */
    while (n--) {
        *d++ = *s++;
    }

    return dest;
}

void *memmove(void *dest, const void *src, size_t n)
{
    unsigned char *d = dest;
    const unsigned char *s = src;

    if (!dest || !src || n == 0) {
        return dest;
    }

    /* 检查重叠 */
    if (d < s) {
        /* 从前往后复制 */
        while (n--) {
            *d++ = *s++;
        }
    } else if (d > s) {
        /* 从后往前复制 */
        d += n;
        s += n;
        while (n--) {
            *--d = *--s;
        }
    }
    /* 如果 d == s，无需复制 */

    return dest;
}

void *memset(void *s, int c, size_t n)
{
    unsigned char *p = s;
    unsigned char val = (unsigned char)c;

    if (!s || n == 0) {
        return s;
    }

    while (n--) {
        *p++ = val;
    }

    return s;
}

int memcmp(const void *s1, const void *s2, size_t n)
{
    const unsigned char *p1 = s1;
    const unsigned char *p2 = s2;

    if (!s1 || !s2) {
        return (s1 == s2) ? 0 : (s1 ? 1 : -1);
    }

    while (n--) {
        if (*p1 != *p2) {
            return (int)*p1 - (int)*p2;
        }
        p1++;
        p2++;
    }

    return 0;
}

void *memchr(const void *s, int c, size_t n)
{
    const unsigned char *p = s;
    unsigned char val = (unsigned char)c;

    if (!s) {
        return NULL;
    }

    while (n--) {
        if (*p == val) {
            return (void *)p;
        }
        p++;
    }

    return NULL;
}

/* ============================================================================
 * 字符串操作函数
 * ============================================================================ */

size_t strlen(const char *s)
{
    const char *p = s;

    if (!s) {
        return 0;
    }

    while (*p) {
        p++;
    }

    return (size_t)(p - s);
}

size_t strnlen(const char *s, size_t maxlen)
{
    const char *p = s;

    if (!s) {
        return 0;
    }

    while (maxlen && *p) {
        p++;
        maxlen--;
    }

    return (size_t)(p - s);
}

char *strcpy(char *dest, const char *src)
{
    char *d = dest;

    if (!dest || !src) {
        return dest;
    }

    while ((*d++ = *src++));

    return dest;
}

char *strncpy(char *dest, const char *src, size_t n)
{
    char *d = dest;

    if (!dest || !src) {
        return dest;
    }

    while (n && *src) {
        *d++ = *src++;
        n--;
    }

    /* 填充剩余空间 */
    while (n--) {
        *d++ = '\0';
    }

    return dest;
}

char *strcat(char *dest, const char *src)
{
    char *d = dest;

    if (!dest || !src) {
        return dest;
    }

    while (*d) {
        d++;
    }

    while ((*d++ = *src++));

    return dest;
}

char *strncat(char *dest, const char *src, size_t n)
{
    char *d = dest;

    if (!dest || !src) {
        return dest;
    }

    while (*d) {
        d++;
    }

    while (n-- && (*d = *src)) {
        d++;
        src++;
    }

    *d = '\0';
    return dest;
}

int strcmp(const char *s1, const char *s2)
{
    if (!s1 || !s2) {
        return (s1 == s2) ? 0 : (s1 ? 1 : -1);
    }

    while (*s1 && (*s1 == *s2)) {
        s1++;
        s2++;
    }

    return (unsigned char)*s1 - (unsigned char)*s2;
}

int strncmp(const char *s1, const char *s2, size_t n)
{
    if (!s1 || !s2) {
        return (s1 == s2) ? 0 : (s1 ? 1 : -1);
    }

    while (n && *s1 && (*s1 == *s2)) {
        s1++;
        s2++;
        n--;
    }

    if (n == 0) {
        return 0;
    }

    return (unsigned char)*s1 - (unsigned char)*s2;
}

/* 不区分大小写的比较 */
int strcasecmp(const char *s1, const char *s2)
{
    if (!s1 || !s2) {
        return (s1 == s2) ? 0 : (s1 ? 1 : -1);
    }

    while (*s1 && (tolower((unsigned char)*s1) == tolower((unsigned char)*s2))) {
        s1++;
        s2++;
    }

    return tolower((unsigned char)*s1) - tolower((unsigned char)*s2);
}

int strncasecmp(const char *s1, const char *s2, size_t n)
{
    if (!s1 || !s2) {
        return (s1 == s2) ? 0 : (s1 ? 1 : -1);
    }

    while (n && *s1 && (tolower((unsigned char)*s1) == tolower((unsigned char)*s2))) {
        s1++;
        s2++;
        n--;
    }

    if (n == 0) {
        return 0;
    }

    return tolower((unsigned char)*s1) - tolower((unsigned char)*s2);
}

char *strchr(const char *s, int c)
{
    char ch = (char)c;

    if (!s) {
        return NULL;
    }

    while (*s) {
        if (*s == ch) {
            return (char *)s;
        }
        s++;
    }

    if (c == '\0') {
        return (char *)s;
    }

    return NULL;
}

char *strrchr(const char *s, int c)
{
    const char *last = NULL;
    char ch = (char)c;

    if (!s) {
        return NULL;
    }

    while (*s) {
        if (*s == ch) {
            last = s;
        }
        s++;
    }

    if (c == '\0') {
        return (char *)s;
    }

    return (char *)last;
}

char *strstr(const char *haystack, const char *needle)
{
    if (!haystack || !needle) {
        return NULL;
    }

    if (!*needle) {
        return (char *)haystack;
    }

    size_t needle_len = strlen(needle);

    while (*haystack) {
        if (*haystack == *needle && strncmp(haystack, needle, needle_len) == 0) {
            return (char *)haystack;
        }
        haystack++;
    }

    return NULL;
}

size_t strspn(const char *s, const char *accept)
{
    const char *p = s;

    if (!s || !accept) {
        return 0;
    }

    while (*p && strchr(accept, *p)) {
        p++;
    }

    return (size_t)(p - s);
}

size_t strcspn(const char *s, const char *reject)
{
    const char *p = s;

    if (!s || !reject) {
        return 0;
    }

    while (*p && !strchr(reject, *p)) {
        p++;
    }

    return (size_t)(p - s);
}

char *strpbrk(const char *s, const char *accept)
{
    if (!s || !accept) {
        return NULL;
    }

    while (*s) {
        if (strchr(accept, *s)) {
            return (char *)s;
        }
        s++;
    }

    return NULL;
}

char *strdup(const char *s)
{
    size_t len;
    char *new_str;

    if (!s) {
        return NULL;
    }

    len = strlen(s) + 1;
    new_str = (char *)malloc(len);

    if (new_str) {
        memcpy(new_str, s, len);
    }

    return new_str;
}

char *strndup(const char *s, size_t n)
{
    size_t len;
    char *new_str;

    if (!s) {
        return NULL;
    }

    len = strnlen(s, n);
    new_str = (char *)malloc(len + 1);

    if (new_str) {
        memcpy(new_str, s, len);
        new_str[len] = '\0';
    }

    return new_str;
}

/* ============================================================================
 * 字符串分割函数
 * ============================================================================ */

static char *strtok_saveptr = NULL;

char *strtok_r(char *str, const char *delim, char **saveptr)
{
    char *token;

    if (!delim || !saveptr) {
        return NULL;
    }

    /* 初始化或继续 */
    if (str) {
        *saveptr = str;
    }

    if (!*saveptr) {
        return NULL;
    }

    /* 跳过前导分隔符 */
    *saveptr += strspn(*saveptr, delim);

    /* 检查是否到达末尾 */
    if (**saveptr == '\0') {
        *saveptr = NULL;
        return NULL;
    }

    /* 找到令牌起始 */
    token = *saveptr;

    /* 找到令牌结束 */
    *saveptr = strpbrk(token, delim);
    if (*saveptr) {
        **saveptr = '\0';
        (*saveptr)++;
    }

    return token;
}

char *strtok(char *str, const char *delim)
{
    return strtok_r(str, delim, &strtok_saveptr);
}

/* ============================================================================
 * 错误字符串函数
 * ============================================================================ */

static const char *error_strings[] = {
    "Success",                          /* 0 */
    "Operation not permitted",          /* EPERM */
    "No such file or directory",        /* ENOENT */
    "No such process",                  /* ESRCH */
    "Interrupted system call",          /* EINTR */
    "Input/output error",               /* EIO */
    "No such device or address",        /* ENXIO */
    "Argument list too long",           /* E2BIG */
    "Exec format error",                /* ENOEXEC */
    "Bad file descriptor",              /* EBADF */
    "No child processes",               /* ECHILD */
    "Resource temporarily unavailable", /* EAGAIN */
    "Cannot allocate memory",           /* ENOMEM */
    "Permission denied",                /* EACCES */
    "Bad address",                      /* EFAULT */
    "Block device required",            /* ENOTBLK */
    "Device or resource busy",          /* EBUSY */
    "File exists",                      /* EEXIST */
    "Invalid cross-device link",        /* EXDEV */
    "No such device",                   /* ENODEV */
    "Not a directory",                  /* ENOTDIR */
    "Is a directory",                   /* EISDIR */
    "Invalid argument",                 /* EINVAL */
    "Too many open files in system",    /* ENFILE */
    "Too many open files",              /* EMFILE */
    "Inappropriate ioctl for device",   /* ENOTTY */
    "Text file busy",                   /* ETXTBSY */
    "File too large",                   /* EFBIG */
    "No space left on device",          /* ENOSPC */
    "Illegal seek",                     /* ESPIPE */
    "Read-only file system",            /* EROFS */
    "Too many links",                   /* EMLINK */
    "Broken pipe",                      /* EPIPE */
    "Numerical argument out of domain", /* EDOM */
    "Numerical result out of range",    /* ERANGE */
    "Resource deadlock avoided",        /* EDEADLK */
    "File name too long",               /* ENAMETOOLONG */
    "No locks available",               /* ENOLCK */
    "Function not implemented",         /* ENOSYS */
    "Directory not empty",              /* ENOTEMPTY */
    "Too many levels of symbolic links",/* ELOOP */
    "Unknown error"                     /* 默认 */
};

#define NUM_ERRORS (sizeof(error_strings) / sizeof(error_strings[0]))

char *strerror(int errnum)
{
    if (errnum < 0) {
        errnum = -errnum;
    }

    if ((size_t)errnum >= NUM_ERRORS) {
        return (char *)"Unknown error";
    }

    return (char *)error_strings[errnum];
}
