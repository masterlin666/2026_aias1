#define UART_THR (unsigned int*)(0x10000000)

void uart_putchar(char c) {
    *UART_THR = c;
}

void uart_puts(const char *s) {
    while (*s) uart_putchar(*s++);
}

void print_int(int n) {
    if (n == 0) { uart_putchar('0'); return; }
    char buf[10];
    int i = 0;
    while (n > 0) {
        buf[i++] = (n % 10) + '0';
        n /= 10;
    }
    while (i--) uart_putchar(buf[i]);
}

extern int fibonacci_asm(int n);

int fibonacci_c(int n) {
    if (n <= 1) return n;
    int a = 0, b = 1, c;
    for (int i = 2; i <= n; i++) {
        c = a + b;
        a = b;
        b = c;
    }
    return b;
}

int main() {
    uart_puts("=== Fibonacci Test ===\n");
    int passed = 0;

    for (int n = 0; n <= 10; n++) {
        int res_asm = fibonacci_asm(n);
        int res_c = fibonacci_c(n);
        
        uart_puts("fib("); print_int(n); uart_puts(") = ");
        print_int(res_c);
        uart_puts(" (asm="); print_int(res_asm);
        uart_puts(", c="); print_int(res_c);
        uart_puts(") ");

        if (res_asm == res_c) {
            uart_puts("[PASS]\n");
            passed++;
        } else {
            uart_puts("[FAIL]\n");
        }
    }

    uart_puts("Result: ");
    print_int(passed);
    uart_puts("/11 tests passed\n");

    while (1); // 停止執行
    return 0;
}