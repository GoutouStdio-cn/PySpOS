/* test_simple.c */
/* 此程序可以同时在SpaceOS和PySpOS上运行 */
/* PySpOS主要依靠ELF兼容层，windows也可以跑 */

#ifndef __SPACEOS__
#include "splibc.h"
#else
#   include <stdio.h>
#   include <spaceapi.h>
#   define printf(...) printf(__VA_ARGS__)
#   define exit(status) sp_exit(status)
#endif

void _start(void) {
    printf("Hello from SpLibC!\n");
    printf("This program can run both SpaceOS and PySpOS!\n");
#ifdef __SPACEOS__
    printf("Running on SpaceOS!\n\n");
#elif __PYSPOS__
    printf("Running on PySpOS!!!\n\n");
#endif
    exit(0);
}

#ifdef __SPACEOS__
void sp_main(void) {
    _start();
}
#endif