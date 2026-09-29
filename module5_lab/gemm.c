#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define M 512
#define K 768
#define N 3072

// Allocate a contiguous 2D matrix (row-major)
float* alloc_matrix(int rows, int cols) {
    float* mat = (float*)calloc(rows * cols, sizeof(float));
    return mat;
}

// Access element at (i, j) in a rows x cols matrix
#define IDX(mat, i, j, cols) ((mat)[(i) * (cols) + (j)])

// Initialize matrix with random values
void init_matrix(float* mat, int rows, int cols) {
    for (int i = 0; i < rows * cols; i++)
        mat[i] = (float)(rand() % 100) / 100.0f;
}

// --- Naive GEMM: C = A * B ---
// A: MxK, B: KxN, C: MxN (i-j-k loop order)
void naive_gemm(float* A, float* B, float* C) {
    memset(C, 0, M * N * sizeof(float));
    for (int i = 0; i < M; i++) {
        for (int j = 0; j < N; j++) {
            float sum = 0.0f;
            for (int k = 0; k < K; k++) {
                sum += IDX(A, i, k, K) * IDX(B, k, j, N);
            }
            IDX(C, i, j, N) = sum;
        }
    }
}

// Compute checksum to prevent compiler optimization
double checksum(float* mat, int rows, int cols) {
    double sum = 0.0;
    for (int i = 0; i < rows * cols; i++)
        sum += mat[i];
    return sum;
}

int main() {
    srand(42);

    float* A = alloc_matrix(M, K);
    float* B = alloc_matrix(K, N);
    float* C = alloc_matrix(M, N);

    init_matrix(A, M, K);
    init_matrix(B, K, N);

    printf("Matrix dimensions: A(%dx%d) * B(%dx%d) = C(%dx%d)\n", M, K, K, N, M, N);
    printf("Total FLOPs: %lld\n", (long long)2 * M * K * N);

    // Warm-up run
    naive_gemm(A, B, C);

    // Timed run
    struct timespec start, end;
    clock_gettime(CLOCK_MONOTONIC, &start);
    naive_gemm(A, B, C);
    clock_gettime(CLOCK_MONOTONIC, &end);

    double elapsed = (end.tv_sec - start.tv_sec) +
                     (end.tv_nsec - start.tv_nsec) / 1e9;

    printf("\n--- Naive GEMM (i-j-k) ---\n");
    printf("Time: %.3f ms\n", elapsed * 1000);
    printf("Performance: %.2f GFLOPS\n",
           (2.0 * M * K * N) / elapsed / 1e9);
    printf("Checksum: %.4f\n", checksum(C, M, N));

    free(A); free(B); free(C);
    return 0;
}


// ============================================================
// Part B: Additional GEMM variant
// ============================================================

#define TILE 64

void tiled_gemm(float* A, float* B, float* C) {
    memset(C, 0, M * N * sizeof(float));
    for (int i0 = 0; i0 < M; i0 += TILE) {
        for (int j0 = 0; j0 < N; j0 += TILE) {
            for (int k0 = 0; k0 < K; k0 += TILE) {
                // Compute one tile of C
                int i_end = (i0 + TILE < M) ? i0 + TILE : M;
                int j_end = (j0 + TILE < N) ? j0 + TILE : N;
                int k_end = (k0 + TILE < K) ? k0 + TILE : K;
                for (int i = i0; i < i_end; i++) {
                    for (int k = k0; k < k_end; k++) {
                        float a_val = IDX(A, i, k, K);
                        for (int j = j0; j < j_end; j++) {
                            IDX(C, i, j, N) += a_val * IDX(B, k, j, N);
                        }
                    }
                }
            }
        }
    }
}


// ============================================================
// Part C: Additional GEMM variant
// ============================================================

#include <immintrin.h>

void vectorized_gemm(float* A, float* B, float* C) {
    memset(C, 0, M * N * sizeof(float));
    for (int i0 = 0; i0 < M; i0 += TILE) {
        for (int j0 = 0; j0 < N; j0 += TILE) {
            for (int k0 = 0; k0 < K; k0 += TILE) {
                int i_end = (i0 + TILE < M) ? i0 + TILE : M;
                int k_end = (k0 + TILE < K) ? k0 + TILE : K;
                int j_end = (j0 + TILE < N) ? j0 + TILE : N;
                for (int i = i0; i < i_end; i++) {
                    for (int k = k0; k < k_end; k++) {
                        __m256 a_vec = _mm256_set1_ps(IDX(A, i, k, K));
                        for (int j = j0; j < j_end; j += 8) {
                            __m256 c_vec = _mm256_loadu_ps(&IDX(C, i, j, N));
                            __m256 b_vec = _mm256_loadu_ps(&IDX(B, k, j, N));
                            c_vec = _mm256_fmadd_ps(a_vec, b_vec, c_vec);
                            _mm256_storeu_ps(&IDX(C, i, j, N), c_vec);
                        }
                    }
                }
            }
        }
    }
}
