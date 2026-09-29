/* hello.c -- Baremetal Hello World for RISC-V */

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

int main(void) {
    uart_puts("Hello, RISC-V!\n");

    // Test basic arithmetic
    int a = 42;
    int b = 58;
    int c = a + b;

    uart_puts("42 + 58 = ");
    print_int(c);
    uart_putc('\n');

    return 0;
}
