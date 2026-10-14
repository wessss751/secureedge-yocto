#define _POSIX_C_SOURCE 200809L

#include <stdio.h>
#include <signal.h>

#include "agent.h"

static void handle_signal(int signal_number)
{
    (void)signal_number;
    agent_request_stop();
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

    agent_run();

    return 0;
}
