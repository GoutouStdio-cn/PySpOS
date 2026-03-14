/*
 * splibc - PySpOS C 标准库
 * 
 * 这是一个轻量级的 C 标准库实现，专为 PySpOS ELF 程序设计
 * 提供基本的系统调用封装和常用函数
 */

#ifndef _SPLIBC_H
#define _SPLIBC_H

/* ==================== 基本类型定义 ==================== */

typedef unsigned char      uint8_t;
typedef unsigned short     uint16_t;
typedef unsigned int       uint32_t;
typedef unsigned long      uint64_t;

typedef signed char        int8_t;
typedef signed short       int16_t;
typedef signed int         int32_t;
typedef signed long        int64_t;

typedef int64_t            intptr_t;
typedef uint64_t           uintptr_t;

typedef uint64_t           size_t;
typedef int64_t            ssize_t;
typedef int64_t            ptrdiff_t;
typedef int64_t            off_t;
typedef int32_t            pid_t;

#define NULL ((void*)0)

/* ==================== EOF 标志 ==================== */

#define EOF    (-1)

/* ==================== 文件定位常量 ==================== */

#define SEEK_SET  0
#define SEEK_CUR  1
#define SEEK_END  2

/* ==================== 布尔类型 ==================== */

typedef _Bool bool;
#define true  1
#define false 0

/* ==================== 变长参数 ==================== */

typedef __builtin_va_list va_list;
#define va_start(ap, last) __builtin_va_start(ap, last)
#define va_end(ap)         __builtin_va_end(ap)
#define va_arg(ap, type)   __builtin_va_arg(ap, type)

/* ==================== 错误号 ==================== */

extern int errno;

#define EINVAL 22
#define ENOMEM 12
#define ENOENT 2
#define ERANGE 34
#define EDOM   33
#define EIO    5
#define EBADF  9
#define EEXIST 17

/* ==================== 限制值 ==================== */

#define INT_MAX    2147483647
#define INT_MIN    (-INT_MAX - 1)
#define LONG_MAX   9223372036854775807L
#define LONG_MIN   (-LONG_MAX - 1L)
#define UINT_MAX   4294967295U
#define ULONG_MAX  18446744073709551615UL
#define LLONG_MAX  9223372036854775807LL
#define LLONG_MIN  (-LLONG_MAX - 1LL)
#define ULLONG_MAX 18446744073709551615ULL
#define RAND_MAX   32767

/* ==================== exit 状态码 ==================== */

#define EXIT_SUCCESS 0
#define EXIT_FAILURE 1

/* ==================== div 类型 ==================== */

typedef struct {
    int quot;
    int rem;
} div_t;

typedef struct {
    long quot;
    long rem;
} ldiv_t;

typedef struct {
    long long quot;
    long long rem;
} lldiv_t;

/* ==================== 系统调用号 (x86_64) ==================== */

#define SYS_read           0
#define SYS_write          1
#define SYS_open           2
#define SYS_close          3
#define SYS_stat           4
#define SYS_fstat          5
#define SYS_lstat          6
#define SYS_lseek          8
#define SYS_mmap           9
#define SYS_mprotect       10
#define SYS_munmap         11
#define SYS_brk            12
#define SYS_exit           60
#define SYS_exit_group     231

/* ==================== 文件描述符 ==================== */

#define STDIN_FILENO       0
#define STDOUT_FILENO      1
#define STDERR_FILENO      2

/* ==================== 文件打开标志 ==================== */

#define O_RDONLY           0
#define O_WRONLY           1
#define O_RDWR             2
#define O_CREAT            0100
#define O_TRUNC            01000
#define O_APPEND           02000
#define O_EXCL             0200

/* ==================== 内存保护标志 ==================== */

#define PROT_NONE          0
#define PROT_READ          1
#define PROT_WRITE         2
#define PROT_EXEC          4

#define MAP_SHARED         1
#define MAP_PRIVATE        2
#define MAP_FIXED          16
#define MAP_ANONYMOUS      32

/* ==================== 系统调用封装 ==================== */

/* 单参数系统调用 */
static inline long syscall1(long num, long arg1) {
    long ret;
    __asm__ volatile (
        "syscall"
        : "=a"(ret)
        : "a"(num), "D"(arg1)
        : "rcx", "r11", "memory"
    );
    return ret;
}

/* 两参数系统调用 */
static inline long syscall2(long num, long arg1, long arg2) {
    long ret;
    __asm__ volatile (
        "syscall"
        : "=a"(ret)
        : "a"(num), "D"(arg1), "S"(arg2)
        : "rcx", "r11", "memory"
    );
    return ret;
}

/* 三参数系统调用 */
static inline long syscall3(long num, long arg1, long arg2, long arg3) {
    long ret;
    __asm__ volatile (
        "syscall"
        : "=a"(ret)
        : "a"(num), "D"(arg1), "S"(arg2), "d"(arg3)
        : "rcx", "r11", "memory"
    );
    return ret;
}

/* 四参数系统调用 */
static inline long syscall4(long num, long arg1, long arg2, long arg3, long arg4) {
    long ret;
    register long r10 __asm__("r10") = arg4;
    __asm__ volatile (
        "syscall"
        : "=a"(ret)
        : "a"(num), "D"(arg1), "S"(arg2), "d"(arg3), "r"(r10)
        : "rcx", "r11", "memory"
    );
    return ret;
}

/* 六参数系统调用 */
static inline long syscall6(long num, long arg1, long arg2, long arg3, 
                            long arg4, long arg5, long arg6) {
    long ret;
    register long r10 __asm__("r10") = arg4;
    register long r8 __asm__("r8") = arg5;
    register long r9 __asm__("r9") = arg6;
    __asm__ volatile (
        "syscall"
        : "=a"(ret)
        : "a"(num), "D"(arg1), "S"(arg2), "d"(arg3), "r"(r10), "r"(r8), "r"(r9)
        : "rcx", "r11", "memory"
    );
    return ret;
}

/* ==================== 字符类型函数 ==================== */

int isalnum(int c);
int isalpha(int c);
int isdigit(int c);
int islower(int c);
int isupper(int c);
int isspace(int c);
int isprint(int c);
int iscntrl(int c);
int isgraph(int c);
int ispunct(int c);
int isxdigit(int c);
int tolower(int c);
int toupper(int c);

/* ==================== 字符串函数 ==================== */

/* 计算字符串长度 */
size_t strlen(const char *s);

/* 复制字符串 */
char *strcpy(char *dest, const char *src);

/* 复制字符串（带长度限制） */
char *strncpy(char *dest, const char *src, size_t n);

/* 连接字符串 */
char *strcat(char *dest, const char *src);

/* 比较字符串 */
int strcmp(const char *s1, const char *s2);

/* 比较字符串（带长度限制） */
int strncmp(const char *s1, const char *s2, size_t n);

/* 查找字符 */
char *strchr(const char *s, int c);

/* 查找子字符串 */
char *strstr(const char *haystack, const char *needle);

/* 复制字符串（动态分配） */
char *strdup(const char *s);

/* 字符串比较（不区分大小写） */
int strcasecmp(const char *s1, const char *s2);
int strncasecmp(const char *s1, const char *s2, size_t n);

/* ==================== 内存函数 ==================== */

/* 设置内存 */
void *memset(void *s, int c, size_t n);

/* 复制内存 */
void *memcpy(void *dest, const void *src, size_t n);

/* 移动内存 */
void *memmove(void *dest, const void *src, size_t n);

/* 比较内存 */
int memcmp(const void *s1, const void *s2, size_t n);

/* ==================== 标准 I/O 函数 ==================== */

/* FILE 类型前向声明 */
typedef struct _FILE FILE;

/* 标准 I/O 流 */
extern FILE *stdin;
extern FILE *stdout;
extern FILE *stderr;

/* 写入文件 */
ssize_t write(int fd, const void *buf, size_t count);

/* 读取文件 */
ssize_t read(int fd, void *buf, size_t count);

/* 打开文件 */
int open(const char *pathname, int flags, ...);

/* 关闭文件 */
int close(int fd);

/* 文件定位 */
off_t lseek(int fd, off_t offset, int whence);

/* ==================== 进程函数 ==================== */

/* 退出进程 */
void exit(int status);

/* 获取进程 ID */
pid_t getpid(void);

/* ==================== 输出函数 ==================== */

/* 输出字符串到 stdout */
int puts(const char *s);

/* 输出字符到 stdout */
int putchar(int c);

/* 格式化输出 */
int printf(const char *format, ...);

/* 格式化输出到字符串 */
int sprintf(char *str, const char *format, ...);

/* ==================== 字符串转换函数 ==================== */

long strtol(const char *nptr, char **endptr, int base);
long long strtoll(const char *nptr, char **endptr, int base);
unsigned long strtoul(const char *nptr, char **endptr, int base);
unsigned long long strtoull(const char *nptr, char **endptr, int base);
int atoi(const char *nptr);
long atol(const char *nptr);
long long atoll(const char *nptr);
double strtod(const char *nptr, char **endptr);

/* ==================== FILE 操作函数 ==================== */

FILE *fopen(const char *pathname, const char *mode);
int fclose(FILE *stream);
int fflush(FILE *stream);
int feof(FILE *stream);
int ferror(FILE *stream);
void clearerr(FILE *stream);
char *fgets(char *s, int size, FILE *stream);
int fputs(const char *s, FILE *stream);
int fgetc(FILE *stream);
int fputc(int c, FILE *stream);
size_t fread(void *ptr, size_t size, size_t nmemb, FILE *stream);
size_t fwrite(const void *ptr, size_t size, size_t nmemb, FILE *stream);
int fseek(FILE *stream, long offset, int whence);
long ftell(FILE *stream);
void rewind(FILE *stream);
int fileno(FILE *stream);
int getchar(void);

/* ==================== 内存分配函数 ==================== */

/* 分配内存 */
void *malloc(size_t size);

/* 释放内存 */
void free(void *ptr);

/* 重新分配内存 */
void *realloc(void *ptr, size_t size);

/* 分配并清零内存 */
void *calloc(size_t nmemb, size_t size);

#endif /* _SPLIBC_H */
