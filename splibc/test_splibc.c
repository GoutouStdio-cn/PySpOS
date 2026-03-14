/* test_splibc.c - 测试 splibc 库 */

#include "splibc.h"

int main(void) {
    printf("=== splibc 测试 ===\n\n");
    
    printf("1. 字符串函数测试:\n");
    printf("   strlen(\"Hello\") = %d\n", (int)strlen("Hello"));
    
    char buf[64];
    strcpy(buf, "Hello ");
    strcat(buf, "World!");
    printf("   strcpy + strcat: %s\n", buf);
    
    printf("   strcmp(\"abc\", \"abc\") = %d\n", strcmp("abc", "abc"));
    printf("   strcmp(\"abc\", \"abd\") = %d\n", strcmp("abc", "abd"));
    
    printf("\n2. 内存函数测试:\n");
    char membuf[16];
    memset(membuf, 'A', 10);
    membuf[10] = '\0';
    printf("   memset: %s\n", membuf);
    
    printf("\n3. 整数格式化测试:\n");
    printf("   十进制: %d\n", 12345);
    printf("   负数: %d\n", -6789);
    printf("   十六进制: 0x%x\n", 0xDEADBEEF);
    
    printf("\n4. 内存分配测试:\n");
    char *dynamic = (char*)malloc(32);
    if (dynamic) {
        strcpy(dynamic, "动态分配成功!");
        printf("   %s\n", dynamic);
        free(dynamic);
    } else {
        printf("   内存分配失败\n");
    }
    
    printf("\n=== 测试完成 ===\n");
    return 0;
}

/* 程序入口点 */
void _start(void) {
    int ret = main();
    exit(ret);
}
