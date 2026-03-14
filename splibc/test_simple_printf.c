/* test_simple_printf.c - 测试 printf */

#include "splibc.h"

int main(void) {
    // 测试简单字符串
    write(1, "Test 1: ", 8);
    write(1, "Hello\n", 6);
    
    // 测试整数
    write(1, "Test 2: ", 8);
    char buf[32];
    buf[0] = '5';
    buf[1] = '\n';
    write(1, buf, 2);
    
    // 测试 itoa
    write(1, "Test 3: itoa(5) = ", 18);
    itoa(5, buf, 10);
    int len = 0;
    while (buf[len]) len++;
    write(1, buf, len);
    write(1, "\n", 1);
    
    // 测试 printf %d
    write(1, "Test 4: printf %d\n", 18);
    printf("   Value: %d\n", 5);
    
    return 0;
}

void _start(void) {
    int ret = main();
    exit(ret);
}
