
#include <stdio.h>
#include <signal.h>
#include <unistd.h>
#include <stdbool.h>

static volatile sig_atomic_t keep_running = 1;

static void handle_signal(int signal_number)
{
    (void)signal_number;
    keep_running = 0;
}

int main(void)
{
    struct sigaction action = {0};

    action.sa_handler = handle_signal;
    sigemptyset(&action.sa_mask);

    if (sigaction(SIGTERM, &action, NULL) == -1 ||
        sigaction(SIGINT, &action, NULL) == -1) {
        perror("sigaction");
        return 1;
    }

    printf("[SecureEdge] Agent started. PID=%ld\n", (long)getpid());
    fflush(stdout);

    unsigned int counter = 0;

    while (keep_running) {
        printf("[SecureEdge] Heartbeat #%u\n", ++counter);
        fflush(stdout);
        sleep(5);
    }

    printf("[SecureEdge] Agent stopped gracefully.\n");
    fflush(stdout);

    return 0;
}
