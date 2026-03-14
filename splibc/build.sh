#!/bin/bash
# 编译 splibc 和测试程序
# 支持模块化 src/ 目录架构

set -e

echo "=== 编译 splibc (模块化架构) ==="

SRC_DIR="src"
OBJ_DIR="obj"

mkdir -p "$OBJ_DIR"

CFLAGS="-c -fno-builtin -nostdlib -ffreestanding -fno-stack-protector \
        -fno-pic -fno-pie -m64 -O2 -Wall -Wextra -D__PYSPOS__ -I."

SOURCES=$(find "$SRC_DIR" -name "*.c" -type f)
OBJECTS=""

for src in $SOURCES; do
    obj_name=$(basename "${src%.c}.o")
    obj_path="$OBJ_DIR/$obj_name"
    echo "编译: $src -> $obj_path"
    gcc $CFLAGS -o "$obj_path" "$src"
    OBJECTS="$OBJECTS $obj_path"
done

echo ""
echo "创建静态库: libsplibc.a"
ar rcs libsplibc.a $OBJECTS

echo ""
echo "=== 编译 test_simple.elf ==="

gcc $CFLAGS -o test_simple.o test_simple.c
ld -e _start -o test_simple.elf test_simple.o -L. -lsplibc
rm -f test_simple.o

echo ""
echo "=== 编译 test_splibc.elf ==="

gcc $CFLAGS -o test_splibc.o test_splibc.c
ld -e _start -o test_splibc.elf test_splibc.o -L. -lsplibc
rm -f test_splibc.o

echo ""
echo "=== 完成 ==="
ls -lh *.elf *.a

echo ""
echo "=== 反汇编 test_simple.elf ==="
objdump -d test_simple.elf | head -40

echo ""
echo "运行方式:"
echo "  在 PySpOS 中执行: run test_simple.elf"
echo "  在 PySpOS 中执行: run test_splibc.elf"
