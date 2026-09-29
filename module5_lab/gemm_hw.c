#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define M 512
#define K 768
#define N 3072

#define IDX(mat, i, j, cols) ((mat)[(i) * (cols) + (j)])

float* alloc_matrix(int rows, int cols) {
    return (float*)calloc(rows * cols, sizeof(float));
}

void init_matrix(float* mat, int rows, int cols) {
    for (int i = 0; i < rows * cols; i++)
        mat[i] = (float)(rand() % 100) / 100.0f;
}

double checksum(float* mat, int rows, int cols) {
    double sum = 0.0;
    for (int i = 0; i < rows * cols; i++) sum += mat[i];
    return sum;
}

// 1. Naive GEMM (i-j-k)
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

// 2. Permuted GEMM (i-k-j) - No Tiling
void permuted_gemm(float* A, float* B, float* C) {
    memset(C, 0, M * N * sizeof(float));
    for (int i = 0; i < M; i++) {
        for (int k = 0; k < K; k++) {
            float a_val = IDX(A, i, k, K);
            for (int j = 0; j < N; j++) {
                IDX(C, i, j, N) += a_val * IDX(B, k, j, N);
            }
        }
    }
}

// 3. Tiled GEMM (General implementation for different TILE sizes)
void tiled_gemm_generic(float* A, float* B, float* C, int TILE) {
    memset(C, 0, M * N * sizeof(float));
    for (int i0 = 0; i0 < M; i0 += TILE) {
        for (int j0 = 0; j0 < N; j0 += TILE) {
            for (int k0 = 0; k0 < K; k0 += TILE) {
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

void run_benchmark(const char* name, void (*func)(float*, float*, float*), float* A, float* B, float* C, double ref_sum) {
    struct timespec start, end;
    // Warm-up
    func(A, B, C);
    
    clock_gettime(CLOCK_MONOTONIC, &start);
    func(A, B, C);
    clock_gettime(CLOCK_MONOTONIC, &end);
    
    double elapsed = (end.tv_sec - start.tv_sec) + (end.tv_nsec - start.tv_nsec) / 1e9;
    double gflops = (2.0 * M * K * N) / elapsed / 1e9;
    double current_sum = checksum(C, M, N);
    
    printf("%-20s | %10.2f ms | %10.2f GFLOPS | Checksum Match: %s\n", 
           name, elapsed * 1000, gflops, (abs(current_sum - ref_sum) < 1e-2) ? "YES" : "NO");
}

// Wrappers for Tiled versions
void tiled_16(float* A, float* B, float* C) { tiled_gemm_generic(A, B, C, 16); }
void tiled_64(float* A, float* B, float* C) { tiled_gemm_generic(A, B, C, 64); }
void tiled_128(float* A, float* B, float* C) { tiled_gemm_generic(A, B, C, 128); }

int main() {
    srand(42);
    float *A = alloc_matrix(M, K), *B = alloc_matrix(K, N), *C = alloc_matrix(M, N);
    init_matrix(A, M, K); init_matrix(B, K, N);

    // Get reference checksum from naive
    naive_gemm(A, B, C);
    double ref_sum = checksum(C, M, N);

    printf("Variant              | Time (ms)   | GFLOPS     | Status\n");
    printf("------------------------------------------------------------\n");
    run_benchmark("Naive (i-j-k)", naive_gemm, A, B, C, ref_sum);
    run_benchmark("Permuted (i-k-j)", permuted_gemm, A, B, C, ref_sum);
    run_benchmark("Tiled T=16", tiled_16, A, B, C, ref_sum);
    run_benchmark("Tiled T=64", tiled_64, A, B, C, ref_sum);
    run_benchmark("Tiled T=128", tiled_128, A, B, C, ref_sum);

    free(A); free(B); free(C);
    return 0;
}