#include <stdio.h>
#include <stdarg.h>

void log_info(const char *format, ...)
{
    va_list args;

    va_start(args, format);

    printf("[SecureEdge] ");
    vprintf(format, args);
    printf("\n");

    fflush(stdout);

    va_end(args);
}
