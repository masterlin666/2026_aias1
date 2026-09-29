/* main.c -- Test C/Assembly hybrid programming */

#define UART_BASE 0x10000000

void uart_putc(char c) {
    *(volatile char *)UART_BASE = c;
}

void uart_puts(const char *s) {
    while (*s) {
        uart_putc(*s++);
    }
}

void print_int(int n) {
    if (n < 0) {
        uart_putc('-');
        n = -n;
    }
    if (n >= 10) {
        print_int(n / 10);
    }
    uart_putc('0' + (n % 10));
}

/* Declare assembly function */
extern int array_sum(int *arr, int n);

/* C reference implementation for verification */
int array_sum_c(int *arr, int n) {
    int sum = 0;
    for (int i = 0; i < n; i++) {
        sum += arr[i];
    }
    return sum;
}

int main(void) {
    int test1[] = {1, 2, 3, 4, 5};
    int test2[] = {10, 20, 30};
    int test3[] = {-5, 10, -3, 8};

    uart_puts("=== C/Assembly Hybrid Test ===\n");

    /* Test 1 */
    int asm_result = array_sum(test1, 5);
    int c_result = array_sum_c(test1, 5);
    uart_puts("Test 1: sum({1,2,3,4,5}) = ");
    print_int(asm_result);
    uart_puts(asm_result == c_result ? " [PASS]\n" : " [FAIL]\n");

    /* Test 2 */
    asm_result = array_sum(test2, 3);
    c_result = array_sum_c(test2, 3);
    uart_puts("Test 2: sum({10,20,30}) = ");
    print_int(asm_result);
    uart_puts(asm_result == c_result ? " [PASS]\n" : " [FAIL]\n");

    /* Test 3 */
    asm_result = array_sum(test3, 4);
    c_result = array_sum_c(test3, 4);
    uart_puts("Test 3: sum({-5,10,-3,8}) = ");
    print_int(asm_result);
    uart_puts(asm_result == c_result ? " [PASS]\n" : " [FAIL]\n");

    return 0;
}
