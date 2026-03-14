# splibc Makefile
# 支持模块化 src/ 目录架构

CC = gcc
AR = ar
LD = ld

CFLAGS = -c -fno-builtin -nostdlib -ffreestanding -fno-stack-protector \
         -fno-pic -fno-pie -m64 -O2 -Wall -Wextra -D__PYSPOS__
ARFLAGS = rcs

SRC_DIR = src
OBJ_DIR = obj

SRCS = $(wildcard $(SRC_DIR)/*.c)
OBJS = $(SRCS:$(SRC_DIR)/%.c=$(OBJ_DIR)/%.o)

LIB_TARGET = libsplibc.a

TEST_SIMPLE = test_simple.elf
TEST_SPLIBC = test_splibc.elf

all: $(OBJ_DIR) $(LIB_TARGET)

$(OBJ_DIR):
	mkdir -p $(OBJ_DIR)

$(LIB_TARGET): $(OBJS)
	$(AR) $(ARFLAGS) $@ $^

$(OBJ_DIR)/%.o: $(SRC_DIR)/%.c splibc.h
	$(CC) $(CFLAGS) -I. -o $@ $<

test: $(LIB_TARGET) $(TEST_SIMPLE) $(TEST_SPLIBC)

$(TEST_SIMPLE): test_simple.c $(LIB_TARGET)
	$(CC) $(CFLAGS) -I. -o test_simple.o test_simple.c
	$(LD) -e _start -o $@ test_simple.o -L. -lsplibc
	rm -f test_simple.o

$(TEST_SPLIBC): test_splibc.c $(LIB_TARGET)
	$(CC) $(CFLAGS) -I. -o test_splibc.o test_splibc.c
	$(LD) -e _start -o $@ test_splibc.o -L. -lsplibc
	rm -f test_splibc.o

clean:
	rm -rf $(OBJ_DIR)
	rm -f *.o *.a *.elf

.PHONY: all test clean
