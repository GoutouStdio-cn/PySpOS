#ifdef __PYSPOS__
#include "../splibc.h"
#else
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>
#include <stdint.h>
#include <stdbool.h>
#include <errno.h>
#include <limits.h>
#include <ctype.h>
#include <spaceapi.h>
#include <fcntl.h>
#endif

#define FILE_BUFFER_SIZE 4096
#define MAX_OPEN_FILES 64

int errno = 0;

#define FILE_MODE_READ      0x01
#define FILE_MODE_WRITE     0x02
#define FILE_MODE_APPEND    0x04
#define FILE_MODE_BINARY    0x08
#define FILE_MODE_CREATE    0x10
#define FILE_MODE_TRUNCATE  0x20
#define FILE_MODE_EXCL      0x40

#define _IOFBF 0
#define _IOLBF 1
#define _IONBF 2

struct _FILE {
    int fd;
    int flags;
    int mode;
    int error;
    int eof;
    char *buffer;
    size_t buf_pos;
    size_t buf_size;
    size_t buf_capacity;
    bool buf_dirty;
    bool buf_allocated;
    int buf_type;
    size_t file_pos;
    size_t file_size;
};

static FILE _stdin = {0, FILE_MODE_READ, 0, 0, 0, NULL, 0, 0, 0, false, false, _IOLBF, 0, 0};
static FILE _stdout = {1, FILE_MODE_WRITE, 0, 0, 0, NULL, 0, 0, 0, false, false, _IOLBF, 0, 0};
static FILE _stderr = {2, FILE_MODE_WRITE, 0, 0, 0, NULL, 0, 0, 0, false, false, _IONBF, 0, 0};

FILE *stdin = &_stdin;
FILE *stdout = &_stdout;
FILE *stderr = &_stderr;

static FILE *open_files[MAX_OPEN_FILES];
static bool file_table_initialized = false;

#ifdef __PYSPOS__
#define SYS_READ  0
#define SYS_WRITE 1
#define SYS_OPEN  2
#define SYS_CLOSE 3
#define SYS_LSEEK 8

static inline long sys_read(int fd, void *buf, size_t count) {
    return syscall3(SYS_READ, fd, (long)buf, count);
}
static inline long sys_write(int fd, const void *buf, size_t count) {
    return syscall3(SYS_WRITE, fd, (long)buf, count);
}
static inline long sys_open(const char *path, int flags, int mode) {
    return syscall3(SYS_OPEN, (long)path, flags, mode);
}
static inline long sys_close(int fd) {
    return syscall1(SYS_CLOSE, fd);
}
static inline long sys_lseek(int fd, long offset, int whence) {
    return syscall3(SYS_LSEEK, fd, offset, whence);
}
#else
#define sys_read  sp_read
#define sys_write sp_write
#define sys_open  sp_open
#define sys_close sp_close
#define sys_lseek sp_lseek
#endif

static void init_file_table(void)
{
    if (file_table_initialized) {
        return;
    }
    for (int i = 0; i < MAX_OPEN_FILES; i++) {
        open_files[i] = NULL;
    }
    open_files[0] = &_stdin;
    open_files[1] = &_stdout;
    open_files[2] = &_stderr;
    file_table_initialized = true;
}

static FILE *alloc_file(void)
{
    init_file_table();
    FILE *fp = (FILE *)malloc(sizeof(FILE));
    if (!fp) {
        return NULL;
    }
    memset(fp, 0, sizeof(FILE));
    fp->fd = -1;
    fp->buf_type = _IOFBF;
    for (int i = 0; i < MAX_OPEN_FILES; i++) {
        if (open_files[i] == NULL) {
            open_files[i] = fp;
            return fp;
        }
    }
    free(fp);
    return NULL;
}

static void free_file(FILE *fp)
{
    if (!fp) {
        return;
    }
    for (int i = 0; i < MAX_OPEN_FILES; i++) {
        if (open_files[i] == fp) {
            open_files[i] = NULL;
            break;
        }
    }
    if (fp->buf_allocated && fp->buffer) {
        free(fp->buffer);
    }
    free(fp);
}

static int flush_buffer(FILE *fp)
{
    if (!fp || !fp->buf_dirty || fp->buf_size == 0) {
        return 0;
    }
    if (fp->mode & FILE_MODE_WRITE) {
        long written = sys_write(fp->fd, fp->buffer, fp->buf_size);
        if (written < 0) {
            fp->error = 1;
            errno = EIO;
            return EOF;
        }
        fp->file_pos += (size_t)written;
    }
    fp->buf_pos = 0;
    fp->buf_size = 0;
    fp->buf_dirty = false;
    return 0;
}

static int fill_buffer(FILE *fp)
{
    if (!fp || !(fp->mode & FILE_MODE_READ)) {
        return EOF;
    }
    if (!fp->buffer) {
        fp->buffer = (char *)malloc(FILE_BUFFER_SIZE);
        if (!fp->buffer) {
            fp->error = 1;
            errno = ENOMEM;
            return EOF;
        }
        fp->buf_capacity = FILE_BUFFER_SIZE;
        fp->buf_allocated = true;
    }
    long bytes_read = sys_read(fp->fd, fp->buffer, fp->buf_capacity);
    if (bytes_read < 0) {
        fp->error = 1;
        errno = EIO;
        return EOF;
    }
    if (bytes_read == 0) {
        fp->eof = 1;
        return EOF;
    }
    fp->buf_pos = 0;
    fp->buf_size = (size_t)bytes_read;
    fp->file_pos += (size_t)bytes_read;
    return 0;
}

static int parse_mode(const char *mode)
{
    int flags = 0;
    bool got_mode = false;
    while (*mode) {
        switch (*mode) {
            case 'r':
                if (!got_mode) {
                    flags |= FILE_MODE_READ;
                    got_mode = true;
                }
                break;
            case 'w':
                if (!got_mode) {
                    flags |= FILE_MODE_WRITE | FILE_MODE_CREATE | FILE_MODE_TRUNCATE;
                    got_mode = true;
                }
                break;
            case 'a':
                if (!got_mode) {
                    flags |= FILE_MODE_WRITE | FILE_MODE_APPEND | FILE_MODE_CREATE;
                    got_mode = true;
                }
                break;
            case 'b':
                flags |= FILE_MODE_BINARY;
                break;
            case '+':
                flags |= FILE_MODE_READ | FILE_MODE_WRITE;
                break;
            case 'x':
                flags |= FILE_MODE_EXCL;
                break;
        }
        mode++;
    }
    return flags;
}

static void print_num(char **buf, size_t *remaining, uint64_t num, int base, bool is_signed, bool uppercase, int width, int precision, bool left_justify, bool show_plus, bool show_space, bool alt_form, bool zero_pad)
{
    char digits[64];
    int i = 0;
    bool negative = false;
    char prefix[8] = {0};
    int prefix_len = 0;

    if (is_signed && (int64_t)num < 0) {
        negative = true;
        num = -(int64_t)num;
    }

    if (num == 0) {
        if (precision != 0) {
            digits[i++] = '0';
        }
    } else {
        while (num > 0) {
            int digit = num % base;
            if (digit < 10) {
                digits[i++] = '0' + digit;
            } else {
                digits[i++] = (uppercase ? 'A' : 'a') + (digit - 10);
            }
            num /= base;
        }
    }

    if (negative) {
        prefix[prefix_len++] = '-';
    } else if (show_plus) {
        prefix[prefix_len++] = '+';
    } else if (show_space) {
        prefix[prefix_len++] = ' ';
    }

    if (alt_form) {
        if (base == 8 && digits[i-1] != '0') {
            prefix[prefix_len++] = '0';
        } else if (base == 16) {
            prefix[prefix_len++] = '0';
            prefix[prefix_len++] = uppercase ? 'X' : 'x';
        }
    }

    int total_len = i + prefix_len;
    int pad_len = (width > total_len) ? width - total_len : 0;
    int zero_pad_len = (precision > i) ? precision - i : 0;

    if (!left_justify && pad_len > 0 && !zero_pad) {
        while (pad_len-- > 0 && *remaining > 0) {
            **buf = ' ';
            (*buf)++;
            (*remaining)--;
        }
    }

    for (int j = 0; j < prefix_len && *remaining > 0; j++) {
        **buf = prefix[j];
        (*buf)++;
        (*remaining)--;
    }

    if (zero_pad_len > 0) {
        while (zero_pad_len-- > 0 && *remaining > 0) {
            **buf = '0';
            (*buf)++;
            (*remaining)--;
        }
    }

    if (!left_justify && pad_len > 0 && zero_pad) {
        while (pad_len-- > 0 && *remaining > 0) {
            **buf = '0';
            (*buf)++;
            (*remaining)--;
        }
    }

    while (i > 0 && *remaining > 0) {
        **buf = digits[--i];
        (*buf)++;
        (*remaining)--;
    }

    if (left_justify && pad_len > 0) {
        while (pad_len-- > 0 && *remaining > 0) {
            **buf = ' ';
            (*buf)++;
            (*remaining)--;
        }
    }
}

int vsnprintf(char *str, size_t size, const char *format, va_list ap)
{
    if (!format) {
        return -1;
    }
    char *buf = str;
    size_t remaining = size > 0 ? size - 1 : 0;
    const char *p = format;

    while (*p && remaining > 0) {
        if (*p != '%') {
            *buf++ = *p++;
            remaining--;
            continue;
        }
        p++;
        if (*p == '%') {
            *buf++ = '%';
            p++;
            remaining--;
            continue;
        }

        bool left_justify = false;
        bool show_plus = false;
        bool show_space = false;
        bool alt_form = false;
        bool zero_pad = false;

        while (*p == '-' || *p == '+' || *p == ' ' || *p == '#' || *p == '0') {
            switch (*p) {
                case '-': left_justify = true; break;
                case '+': show_plus = true; break;
                case ' ': show_space = true; break;
                case '#': alt_form = true; break;
                case '0': zero_pad = true; break;
            }
            p++;
        }

        int width = 0;
        if (*p >= '0' && *p <= '9') {
            while (*p >= '0' && *p <= '9') {
                width = width * 10 + (*p - '0');
                p++;
            }
        } else if (*p == '*') {
            width = va_arg(ap, int);
            p++;
        }

        int precision = -1;
        if (*p == '.') {
            p++;
            precision = 0;
            if (*p >= '0' && *p <= '9') {
                while (*p >= '0' && *p <= '9') {
                    precision = precision * 10 + (*p - '0');
                    p++;
                }
            } else if (*p == '*') {
                precision = va_arg(ap, int);
                p++;
            }
        }

        bool long_flag = false;
        bool long_long_flag = false;
        bool size_t_flag = false;

        if (*p == 'l') {
            long_flag = true;
            p++;
            if (*p == 'l') {
                long_long_flag = true;
                p++;
            }
        } else if (*p == 'z') {
            size_t_flag = true;
            p++;
        } else if (*p == 'h') {
            p++;
            if (*p == 'h') {
                p++;
            }
        }

        switch (*p) {
            case 'd':
            case 'i': {
                int64_t val;
                if (long_long_flag) {
                    val = va_arg(ap, long long);
                } else if (long_flag) {
                    val = va_arg(ap, long);
                } else if (size_t_flag) {
                    val = va_arg(ap, ssize_t);
                } else {
                    val = va_arg(ap, int);
                }
                print_num(&buf, &remaining, val, 10, true, false, width, precision, left_justify, show_plus, show_space, alt_form, zero_pad);
                break;
            }
            case 'u': {
                uint64_t val;
                if (long_long_flag) {
                    val = va_arg(ap, unsigned long long);
                } else if (long_flag) {
                    val = va_arg(ap, unsigned long);
                } else if (size_t_flag) {
                    val = va_arg(ap, size_t);
                } else {
                    val = va_arg(ap, unsigned int);
                }
                print_num(&buf, &remaining, val, 10, false, false, width, precision, left_justify, show_plus, show_space, alt_form, zero_pad);
                break;
            }
            case 'o': {
                uint64_t val;
                if (long_long_flag) {
                    val = va_arg(ap, unsigned long long);
                } else if (long_flag) {
                    val = va_arg(ap, unsigned long);
                } else {
                    val = va_arg(ap, unsigned int);
                }
                print_num(&buf, &remaining, val, 8, false, false, width, precision, left_justify, show_plus, show_space, alt_form, zero_pad);
                break;
            }
            case 'x': {
                uint64_t val;
                if (long_long_flag) {
                    val = va_arg(ap, unsigned long long);
                } else if (long_flag) {
                    val = va_arg(ap, unsigned long);
                } else if (size_t_flag) {
                    val = va_arg(ap, size_t);
                } else {
                    val = va_arg(ap, unsigned int);
                }
                print_num(&buf, &remaining, val, 16, false, false, width, precision, left_justify, show_plus, show_space, alt_form, zero_pad);
                break;
            }
            case 'X': {
                uint64_t val;
                if (long_long_flag) {
                    val = va_arg(ap, unsigned long long);
                } else if (long_flag) {
                    val = va_arg(ap, unsigned long);
                } else {
                    val = va_arg(ap, unsigned int);
                }
                print_num(&buf, &remaining, val, 16, false, true, width, precision, left_justify, show_plus, show_space, alt_form, zero_pad);
                break;
            }
            case 'p': {
                void *ptr = va_arg(ap, void *);
                print_num(&buf, &remaining, (uint64_t)ptr, 16, false, false, width, precision, left_justify, show_plus, show_space, true, zero_pad);
                break;
            }
            case 's': {
                const char *s = va_arg(ap, const char *);
                if (!s) s = "(null)";
                size_t len = strlen(s);
                if (precision >= 0 && (size_t)precision < len) {
                    len = (size_t)precision;
                }
                int pad_len = (width > (int)len) ? width - (int)len : 0;
                if (!left_justify && pad_len > 0) {
                    while (pad_len-- > 0 && remaining > 0) {
                        *buf++ = ' ';
                        remaining--;
                    }
                }
                while (len-- > 0 && remaining > 0) {
                    *buf++ = *s++;
                    remaining--;
                }
                if (left_justify && pad_len > 0) {
                    while (pad_len-- > 0 && remaining > 0) {
                        *buf++ = ' ';
                        remaining--;
                    }
                }
                break;
            }
            case 'c': {
                char c = (char)va_arg(ap, int);
                int pad_len = (width > 1) ? width - 1 : 0;
                if (!left_justify && pad_len > 0) {
                    while (pad_len-- > 0 && remaining > 0) {
                        *buf++ = ' ';
                        remaining--;
                    }
                }
                if (remaining > 0) {
                    *buf++ = c;
                    remaining--;
                }
                if (left_justify && pad_len > 0) {
                    while (pad_len-- > 0 && remaining > 0) {
                        *buf++ = ' ';
                        remaining--;
                    }
                }
                break;
            }
            case 'n': {
                int *n = va_arg(ap, int *);
                *n = (int)(buf - str);
                break;
            }
        }
        p++;
    }
    if (size > 0) {
        *buf = '\0';
    }
    return (int)(buf - str);
}

int vsprintf(char *str, const char *format, va_list ap)
{
    return vsnprintf(str, (size_t)-1, format, ap);
}

int snprintf(char *str, size_t size, const char *format, ...)
{
    va_list ap;
    va_start(ap, format);
    int ret = vsnprintf(str, size, format, ap);
    va_end(ap);
    return ret;
}

int sprintf(char *str, const char *format, ...)
{
    va_list ap;
    va_start(ap, format);
    int ret = vsprintf(str, format, ap);
    va_end(ap);
    return ret;
}

int vfprintf(FILE *stream, const char *format, va_list ap)
{
    if (!stream) {
        errno = EINVAL;
        return -1;
    }
    char buf[1024];
    int len = vsnprintf(buf, sizeof(buf), format, ap);
    if (len < 0) {
        return len;
    }
    size_t written = fwrite(buf, 1, (size_t)len, stream);
    return (written == (size_t)len) ? len : -1;
}

int vprintf(const char *format, va_list ap)
{
    return vfprintf(stdout, format, ap);
}

int fprintf(FILE *stream, const char *format, ...)
{
    va_list ap;
    va_start(ap, format);
    int ret = vfprintf(stream, format, ap);
    va_end(ap);
    return ret;
}

int printf(const char *format, ...)
{
    va_list ap;
    va_start(ap, format);
    int ret = vprintf(format, ap);
    va_end(ap);
    return ret;
}

int putchar(int c)
{
    char ch = (char)c;
    long written = sys_write(STDOUT_FILENO, &ch, 1);
    return (written == 1) ? c : EOF;
}

int fputc(int c, FILE *stream)
{
    if (!stream) {
        errno = EINVAL;
        return EOF;
    }
    if (stream->buf_type == _IONBF) {
        char ch = (char)c;
        long written = sys_write(stream->fd, &ch, 1);
        if (written == 1) {
            stream->file_pos++;
            return c;
        } else {
            stream->error = 1;
            errno = EIO;
            return EOF;
        }
    }
    if (!stream->buffer) {
        stream->buffer = (char *)malloc(FILE_BUFFER_SIZE);
        if (!stream->buffer) {
            stream->error = 1;
            errno = ENOMEM;
            return EOF;
        }
        stream->buf_capacity = FILE_BUFFER_SIZE;
        stream->buf_allocated = true;
    }
    if (stream->buf_size >= stream->buf_capacity) {
        if (flush_buffer(stream) != 0) {
            return EOF;
        }
    }
    stream->buffer[stream->buf_size++] = (char)c;
    stream->buf_dirty = true;
    if (stream->buf_type == _IOLBF && c == '\n') {
        if (flush_buffer(stream) != 0) {
            return EOF;
        }
    }
    return c;
}

int puts(const char *s)
{
    if (!s) {
        errno = EINVAL;
        return EOF;
    }
    size_t len = strlen(s);
    long written = sys_write(STDOUT_FILENO, s, len);
    if (written < 0 || (size_t)written != len) {
        errno = EIO;
        return EOF;
    }
    sys_write(STDOUT_FILENO, "\n", 1);
    return (int)(len + 1);
}

int fputs(const char *s, FILE *stream)
{
    if (!s || !stream) {
        errno = EINVAL;
        return EOF;
    }
    size_t len = strlen(s);
    size_t written = fwrite(s, 1, len, stream);
    return (written == len) ? 0 : EOF;
}

int getchar(void)
{
    char ch;
    long read = sys_read(STDIN_FILENO, &ch, 1);
    return (read == 1) ? (int)ch : EOF;
}

int fgetc(FILE *stream)
{
    if (!stream) {
        errno = EINVAL;
        return EOF;
    }
    if (!(stream->mode & FILE_MODE_READ)) {
        stream->error = 1;
        errno = EBADF;
        return EOF;
    }
    if (stream->buf_type == _IONBF) {
        char ch;
        long read = sys_read(stream->fd, &ch, 1);
        if (read == 1) {
            stream->file_pos++;
            return (int)ch;
        } else if (read == 0) {
            stream->eof = 1;
            return EOF;
        } else {
            stream->error = 1;
            errno = EIO;
            return EOF;
        }
    }
    if (stream->buf_pos >= stream->buf_size) {
        if (fill_buffer(stream) != 0) {
            return EOF;
        }
    }
    return (int)(unsigned char)stream->buffer[stream->buf_pos++];
}

char *fgets(char *s, int size, FILE *stream)
{
    if (!s || !stream || size <= 0) {
        errno = EINVAL;
        return NULL;
    }
    char *p = s;
    int count = 0;
    while (count < size - 1) {
        int c = fgetc(stream);
        if (c == EOF) {
            if (count == 0) {
                return NULL;
            }
            break;
        }
        *p++ = (char)c;
        count++;
        if (c == '\n') {
            break;
        }
    }
    *p = '\0';
    return s;
}

size_t fread(void *ptr, size_t size, size_t nmemb, FILE *stream)
{
    if (!ptr || !stream || size == 0 || nmemb == 0) {
        return 0;
    }
    size_t total = size * nmemb;
    size_t read_count = 0;
    char *p = (char *)ptr;
    while (read_count < total) {
        int c = fgetc(stream);
        if (c == EOF) {
            break;
        }
        *p++ = (char)c;
        read_count++;
    }
    return read_count / size;
}

size_t fwrite(const void *ptr, size_t size, size_t nmemb, FILE *stream)
{
    if (!ptr || !stream || size == 0 || nmemb == 0) {
        return 0;
    }
    size_t total = size * nmemb;
    size_t written = 0;
    const char *p = (const char *)ptr;
    while (written < total) {
        if (fputc(*p++, stream) == EOF) {
            break;
        }
        written++;
    }
    return written / size;
}

int fflush(FILE *stream)
{
    if (!stream) {
        return 0;
    }
    return flush_buffer(stream);
}

int fclose(FILE *stream)
{
    if (!stream) {
        errno = EINVAL;
        return EOF;
    }
    flush_buffer(stream);
    sys_close(stream->fd);
    free_file(stream);
    return 0;
}

FILE *fopen(const char *pathname, const char *mode)
{
    if (!pathname || !mode) {
        errno = EINVAL;
        return NULL;
    }
    int flags = parse_mode(mode);
    int open_flags = 0;
    if (flags & FILE_MODE_READ && !(flags & FILE_MODE_WRITE)) {
        open_flags = O_RDONLY;
    } else if (flags & FILE_MODE_WRITE && !(flags & FILE_MODE_READ)) {
        open_flags = O_WRONLY;
        if (flags & FILE_MODE_CREATE) open_flags |= O_CREAT;
        if (flags & FILE_MODE_TRUNCATE) open_flags |= O_TRUNC;
    } else {
        open_flags = O_RDWR;
        if (flags & FILE_MODE_CREATE) open_flags |= O_CREAT;
        if (flags & FILE_MODE_TRUNCATE) open_flags |= O_TRUNC;
    }
    if (flags & FILE_MODE_APPEND) {
        open_flags &= ~O_TRUNC;
        open_flags |= O_APPEND;
    }
    int fd = sys_open(pathname, open_flags, 0644);
    if (fd < 0) {
        errno = ENOENT;
        return NULL;
    }
    FILE *fp = alloc_file();
    if (!fp) {
        sys_close(fd);
        errno = ENOMEM;
        return NULL;
    }
    fp->fd = fd;
    fp->mode = flags;
    return fp;
}

int feof(FILE *stream)
{
    return stream ? stream->eof : 0;
}

int ferror(FILE *stream)
{
    return stream ? stream->error : 0;
}

void clearerr(FILE *stream)
{
    if (stream) {
        stream->error = 0;
        stream->eof = 0;
    }
}

long ftell(FILE *stream)
{
    if (!stream) {
        errno = EINVAL;
        return -1;
    }
    return (long)stream->file_pos;
}

int fseek(FILE *stream, long offset, int whence)
{
    if (!stream) {
        errno = EINVAL;
        return -1;
    }
    flush_buffer(stream);
    long result = sys_lseek(stream->fd, offset, whence);
    if (result < 0) {
        errno = EIO;
        return -1;
    }
    stream->file_pos = (size_t)result;
    stream->buf_pos = 0;
    stream->buf_size = 0;
    return 0;
}

void rewind(FILE *stream)
{
    if (stream) {
        fseek(stream, 0, SEEK_SET);
        clearerr(stream);
    }
}

int fileno(FILE *stream)
{
    if (!stream) {
        errno = EINVAL;
        return -1;
    }
    return stream->fd;
}
