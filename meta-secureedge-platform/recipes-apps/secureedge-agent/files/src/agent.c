#define _POSIX_C_SOURCE 200809L
#include <signal.h>
#include <unistd.h>

#include "agent.h"
#include "logger.h"

static volatile sig_atomic_t keep_running = 1;

void agent_request_stop(void)
{
    keep_running = 0;
}

void agent_run(void)
{
    unsigned int counter = 0;

    log_info("Agent started. PID=%ld", (long)getpid());

    while (keep_running) {
        log_info("Heartbeat #%u", ++counter);
        sleep(5);
    }

    log_info("Agent stopped gracefully.");
}
