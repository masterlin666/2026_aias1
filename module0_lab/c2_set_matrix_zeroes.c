/*
 * Prerequisite Assessment — C Problem 2: Set Matrix Zeroes
 *
 * Given an m x n integer matrix, if an element is 0, set its entire
 * row and column to 0's. You must do it in place.
 *
 * Constraints:
 *   - 1 <= m, n <= 200
 *   - -2^31 <= matrix[i][j] <= 2^31 - 1
 *
 * Instructions:
 *   - Implement the setZeroes function below
 *   - Do NOT modify main()
 *   - Compile: gcc -o c2 c2_set_matrix_zeroes.c
 *   - Run:     ./c2 < input.txt
 */
#include <stdio.h>
#include <stdlib.h>

/* ──────────────────────────────────────────────
   TODO: Implement this function
   matrix:        array of row pointers
   matrixSize:    number of rows (m)
   matrixColSize: array where matrixColSize[i] = n (columns per row)
   ────────────────────────────────────────────── */
void setZeroes(int** matrix, int matrixSize, int* matrixColSize) {
    /* Your implementation here */
    int m = matrixSize;
    int n = matrixColSize[0];
    int firstRowZero = 0;
    int firstColZero = 0;

    for (int j = 0; j < n; j++) {
        if (matrix[0][j] == 0) {
            firstRowZero = 1;
            break;
        }
    }
    for (int i = 0; i < m; i++) {
        if (matrix[i][0] == 0) {
            firstColZero = 1;
            break;
        }
    }
    for (int i = 1; i < m; i++) {
        for (int j = 1; j < n; j++) {
            if (matrix[i][j] == 0) {
                matrix[i][0] = 0;
                matrix[0][j] = 0;
            }
        }
    }
    for (int i = 1; i < m; i++) {
    // 這一列的首位已經是 0
    if (matrix[i][0] == 0) {
        for (int j = 1; j < n; j++) matrix[i][j] = 0;
        continue; 
    }
    
    // 這一列首位不是 0
    for (int j = 1; j < n; j++) {
        if (matrix[0][j] == 0) {
            matrix[i][j] = 0;
        }
    }
}
    if (firstRowZero) {
        for (int j = 0; j < n; j++) matrix[0][j] = 0;
    }
    if (firstColZero) {
        for (int i = 0; i < m; i++) matrix[i][0] = 0;
    }
}

/* ── Harness (do NOT modify below) ────────────── */
int main() {
    int m, n;
    scanf("%d %d", &m, &n);

    int** matrix = malloc(m * sizeof(int*));
    int* colSizes = malloc(m * sizeof(int));
    for (int i = 0; i < m; i++) {
        matrix[i] = malloc(n * sizeof(int));
        colSizes[i] = n;
        for (int j = 0; j < n; j++) {
            scanf("%d", &matrix[i][j]);
        }
    }

    setZeroes(matrix, m, colSizes);

    /* Print result */
    for (int i = 0; i < m; i++) {
        for (int j = 0; j < n; j++) {
            if (j > 0) printf(" ");
            printf("%d", matrix[i][j]);
        }
        printf("\n");
    }

    for (int i = 0; i < m; i++) free(matrix[i]);
    free(matrix);
    free(colSizes);
    return 0;
}
