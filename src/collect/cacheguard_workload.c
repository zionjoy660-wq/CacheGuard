#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <time.h>

#define BUFFER_SIZE (16 * 1024 * 1024)
#define NORMAL_SIZE (256 * 1024)
#define WARMUP_SECONDS 5.0

static double elapsed_seconds(struct timespec start, struct timespec end) {
    return (end.tv_sec - start.tv_sec) +
           (end.tv_nsec - start.tv_nsec) / 1e9;
}

static void run_phase(uint8_t *buffer, size_t active_size,
                      size_t stride, double duration,
                      volatile uint64_t *checksum) {
    struct timespec start, now;

    clock_gettime(CLOCK_MONOTONIC, &start);

    do {
        for (size_t i = 0; i < active_size; i += stride) {
            *checksum += buffer[i];
        }

        clock_gettime(CLOCK_MONOTONIC, &now);
    } while (elapsed_seconds(start, now) < duration);
}

int main(int argc, char *argv[]) {
    if (argc != 3) {
        fprintf(stderr, "Usage: %s <normal|suspicious> <seconds>\n", argv[0]);
        return 1;
    }

    size_t stride, active_size;

    if (strcmp(argv[1], "normal") == 0) {
        stride = 64;
        active_size = NORMAL_SIZE;
    } else if (strcmp(argv[1], "suspicious") == 0) {
        stride = 4096;
        active_size = BUFFER_SIZE;
    } else {
        fprintf(stderr, "Invalid mode. Use normal or suspicious.\n");
        return 1;
    }

    char *endptr;
    double duration = strtod(argv[2], &endptr);

    if (*endptr != '\0' || duration <= 0) {
        fprintf(stderr, "Duration must be positive.\n");
        return 1;
    }

    uint8_t *buffer = malloc(BUFFER_SIZE);
    if (buffer == NULL) {
        perror("malloc");
        return 1;
    }

    for (size_t i = 0; i < BUFFER_SIZE; i++) {
        buffer[i] = (uint8_t)((i / 64) % 251 + 1);
    }

    volatile uint64_t checksum = 0;

    printf("Warm-up: %.0f seconds\n", WARMUP_SECONDS);
    fflush(stdout);

    run_phase(buffer, active_size, stride, WARMUP_SECONDS, &checksum);

    printf("Measurement: %.2f seconds\n", duration);
    fflush(stdout);

    run_phase(buffer, active_size, stride, duration, &checksum);

    printf("Mode: %s\n", argv[1]);
    printf("Working set: %zu bytes\n", active_size);
    printf("Stride: %zu bytes\n", stride);
    printf("Duration requested: %.2f seconds\n", duration);
    printf("Checksum: %llu\n", (unsigned long long)checksum);

    free(buffer);
    return 0;
}
