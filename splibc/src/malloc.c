#ifdef __PYSPOS__
#include "../splibc.h"
#else
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <spaceapi.h>
#endif

#define ALIGNMENT 16
#define ALIGN(size) (((size) + (ALIGNMENT - 1)) & ~(ALIGNMENT - 1))
#define MIN_BLOCK_SIZE 64
#ifndef PAGE_SIZE
#define PAGE_SIZE 4096
#endif

typedef struct block {
    size_t size;
    struct block *next;
    struct block *prev;
    bool free;
    uint32_t magic;
} block_t;

#define BLOCK_MAGIC 0xDEADBEEF
#define BLOCK_MAGIC_FREE 0xBEEFDEAD
#define BLOCK_HEADER_SIZE ALIGN(sizeof(block_t))

static block_t *heap_start = NULL;
static block_t *free_list_head = NULL;
static void *heap_end = NULL;
static intptr_t heap_size = 0;

#ifdef __PYSPOS__
static int malloc_mutex = -1;
static bool malloc_initialized = false;

static void malloc_init(void)
{
    if (malloc_initialized) {
        return;
    }
    heap_start = NULL;
    free_list_head = NULL;
    heap_end = NULL;
    heap_size = 0;
    malloc_initialized = true;
}

static void malloc_lock(void) {}
static void malloc_unlock(void) {}

static void *request_heap_space(intptr_t increment)
{
    if (heap_end == NULL) {
        heap_end = (void*)syscall1(SYS_brk, 0);
    }
    void *old_end = heap_end;
    void *new_end = (char*)heap_end + increment;
    void *result = (void*)syscall1(SYS_brk, (long)new_end);
    if (result != new_end) {
        return NULL;
    }
    heap_end = new_end;
    return old_end;
}
#else
static int malloc_mutex = -1;
static bool malloc_initialized = false;

static void malloc_init(void)
{
    if (malloc_initialized) {
        return;
    }
    malloc_mutex = sp_mutex_create();
    if (malloc_mutex < 0) {
        malloc_mutex = -1;
    }
    heap_start = NULL;
    free_list_head = NULL;
    heap_end = NULL;
    heap_size = 0;
    malloc_initialized = true;
}

static void malloc_lock(void)
{
    if (malloc_mutex >= 0) {
        sp_mutex_lock(malloc_mutex);
    }
}

static void malloc_unlock(void)
{
    if (malloc_mutex >= 0) {
        sp_mutex_unlock(malloc_mutex);
    }
}

static void *request_heap_space(intptr_t increment)
{
    void *result = sp_sbrk(increment);
    if (result == (void *)-1) {
        return NULL;
    }
    return result;
}
#endif

static void remove_from_free_list(block_t *block)
{
    if (!block || !block->free) {
        return;
    }
    if (block->prev) {
        block->prev->next = block->next;
    } else {
        free_list_head = block->next;
    }
    if (block->next) {
        block->next->prev = block->prev;
    }
    block->next = NULL;
    block->prev = NULL;
    block->free = false;
    block->magic = BLOCK_MAGIC;
}

static void add_to_free_list(block_t *block)
{
    if (!block) {
        return;
    }
    block->free = true;
    block->magic = BLOCK_MAGIC_FREE;
    if (!free_list_head) {
        free_list_head = block;
        block->next = NULL;
        block->prev = NULL;
        return;
    }
    if (block < free_list_head) {
        block->next = free_list_head;
        block->prev = NULL;
        free_list_head->prev = block;
        free_list_head = block;
        return;
    }
    block_t *current = free_list_head;
    while (current->next && current->next < block) {
        current = current->next;
    }
    block->next = current->next;
    block->prev = current;
    if (current->next) {
        current->next->prev = block;
    }
    current->next = block;
}

static block_t *find_free_block(size_t size)
{
    block_t *current = free_list_head;
    while (current) {
        if (current->free && current->size >= size) {
            remove_from_free_list(current);
            return current;
        }
        current = current->next;
    }
    return NULL;
}

static block_t *request_space(size_t size)
{
    size_t total_size = ALIGN(size + BLOCK_HEADER_SIZE);
    if (total_size < PAGE_SIZE) {
        total_size = PAGE_SIZE;
    }
    void *ptr = request_heap_space(total_size);
    if (!ptr) {
        return NULL;
    }
    block_t *block = (block_t *)ptr;
    block->size = total_size - BLOCK_HEADER_SIZE;
    block->next = NULL;
    block->prev = NULL;
    block->free = false;
    block->magic = BLOCK_MAGIC;
    heap_size += total_size;
    if (!heap_end || (char *)ptr + total_size > (char *)heap_end) {
        heap_end = (char *)ptr + total_size;
    }
    return block;
}

static void split_block(block_t *block, size_t size)
{
    if (!block || block->size < size + BLOCK_HEADER_SIZE + MIN_BLOCK_SIZE) {
        return;
    }
    block_t *new_block = (block_t *)((char *)block + BLOCK_HEADER_SIZE + size);
    new_block->size = block->size - size - BLOCK_HEADER_SIZE;
    new_block->next = NULL;
    new_block->prev = NULL;
    new_block->free = false;
    new_block->magic = BLOCK_MAGIC;
    block->size = size;
    add_to_free_list(new_block);
}

static void coalesce_blocks(block_t *block)
{
    if (!block || !block->free) {
        return;
    }
    block_t *next_block = (block_t *)((char *)block + BLOCK_HEADER_SIZE + block->size);
    if ((char *)next_block < (char *)heap_end &&
        next_block->free &&
        next_block->magic == BLOCK_MAGIC_FREE) {
        if (next_block->prev) {
            next_block->prev->next = next_block->next;
        } else {
            free_list_head = next_block->next;
        }
        if (next_block->next) {
            next_block->next->prev = next_block->prev;
        }
        block->size += BLOCK_HEADER_SIZE + next_block->size;
    }
    if (block->prev && block->prev->free && block->prev->magic == BLOCK_MAGIC_FREE) {
        block_t *prev_block = block->prev;
        prev_block->size += BLOCK_HEADER_SIZE + block->size;
        if (block->prev) {
            block->prev->next = block->next;
        }
        if (block->next) {
            block->next->prev = block->prev;
        }
    }
}

static bool validate_block(block_t *block)
{
    if (!block) {
        return false;
    }
    if (block->magic != BLOCK_MAGIC && block->magic != BLOCK_MAGIC_FREE) {
        return false;
    }
    if ((char *)block < (char *)heap_start ||
        (char *)block >= (char *)heap_end) {
        return false;
    }
    return true;
}

void *malloc(size_t size)
{
    if (size == 0) {
        return NULL;
    }
    if (!malloc_initialized) {
        malloc_init();
    }
    malloc_lock();
    size = ALIGN(size);
    block_t *block = NULL;
    if (!heap_start) {
        block = request_space(size);
        if (!block) {
            malloc_unlock();
            return NULL;
        }
        heap_start = block;
    } else {
        block = find_free_block(size);
        if (block) {
            split_block(block, size);
        } else {
            block_t *last = heap_start;
            while (last->next) {
                last = last->next;
            }
            block = request_space(size);
            if (!block) {
                malloc_unlock();
                return NULL;
            }
            last->next = block;
            block->prev = last;
        }
    }
    block->free = false;
    block->magic = BLOCK_MAGIC;
    void *result = (void *)((char *)block + BLOCK_HEADER_SIZE);
    malloc_unlock();
    return result;
}

void free(void *ptr)
{
    if (!ptr) {
        return;
    }
    if (!malloc_initialized) {
        malloc_init();
    }
    malloc_lock();
    block_t *block = (block_t *)((char *)ptr - BLOCK_HEADER_SIZE);
    if (!validate_block(block)) {
        malloc_unlock();
        return;
    }
    if (block->free) {
        malloc_unlock();
        return;
    }
    add_to_free_list(block);
    coalesce_blocks(block);
    malloc_unlock();
}

void *calloc(size_t nmemb, size_t size)
{
    if (nmemb == 0 || size == 0) {
        return NULL;
    }
    size_t total_size = nmemb * size;
    if (nmemb != 0 && total_size / nmemb != size) {
        return NULL;
    }
    void *ptr = malloc(total_size);
    if (!ptr) {
        return NULL;
    }
    memset(ptr, 0, total_size);
    return ptr;
}

void *realloc(void *ptr, size_t size)
{
    if (!ptr) {
        return malloc(size);
    }
    if (size == 0) {
        free(ptr);
        return NULL;
    }
    if (!malloc_initialized) {
        malloc_init();
    }
    malloc_lock();
    block_t *block = (block_t *)((char *)ptr - BLOCK_HEADER_SIZE);
    if (!validate_block(block)) {
        malloc_unlock();
        return NULL;
    }
    size = ALIGN(size);
    if (block->size >= size) {
        split_block(block, size);
        malloc_unlock();
        return ptr;
    }
    malloc_unlock();
    void *new_ptr = malloc(size);
    if (!new_ptr) {
        return NULL;
    }
    memcpy(new_ptr, ptr, block->size < size ? block->size : size);
    free(ptr);
    return new_ptr;
}

size_t malloc_usable_size(void *ptr)
{
    if (!ptr) {
        return 0;
    }
    block_t *block = (block_t *)((char *)ptr - BLOCK_HEADER_SIZE);
    if (!validate_block(block)) {
        return 0;
    }
    return block->size;
}

void malloc_stats(size_t *total_size, size_t *free_size, size_t *used_size)
{
    if (!malloc_initialized) {
        if (total_size) *total_size = 0;
        if (free_size) *free_size = 0;
        if (used_size) *used_size = 0;
        return;
    }
    malloc_lock();
    size_t free_bytes = 0;
    size_t used_bytes = 0;
    block_t *current = heap_start;
    while (current) {
        if (current->free) {
            free_bytes += current->size;
        } else {
            used_bytes += current->size;
        }
        current = current->next;
    }
    if (total_size) *total_size = heap_size;
    if (free_size) *free_size = free_bytes;
    if (used_size) *used_size = used_bytes;
    malloc_unlock();
}
