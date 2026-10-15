#define _POSIX_C_SOURCE 200809L

#include <signal.h>
#include <stdbool.h>
#include <stdlib.h>
#include <unistd.h>

#include "agent.h"
#include "logger.h"
#include "sensor.h"
#include "mqtt_client.h"

static volatile sig_atomic_t keep_running = 1;

void agent_request_stop(void)
{
    keep_running = 0;
}

void agent_run(void)
{
    const char *mqtt_host = getenv("SECUREEDGE_MQTT_HOST");

    if (mqtt_host == NULL || mqtt_host[0] == '\0') {
        mqtt_host = "127.0.0.1";
    }

    log_info("Agent started. PID=%ld", (long)getpid());

    bool mqtt_ready = mqtt_client_init(mqtt_host, 1883);

    if (!mqtt_ready) {
        log_info("MQTT initialization failed; acquisition continues");
    }

    while (keep_running) {
        sensor_data_t data = sensor_read();

        if (data.valid) {
            log_info(
                "Sample #%u | Temperature: %.2f C | Voltage: %.2f V | Status: OK",
                (unsigned int)data.sequence,
                (double)data.temperature_c,
                (double)data.voltage_v
            );

            if (mqtt_ready && !mqtt_client_publish(&data)) {
                log_info("MQTT unavailable; sample not published");
            }
        } else {
            log_info(
                "Sample #%u | Status: INVALID",
                (unsigned int)data.sequence
            );
        }

        sleep(5);
    }

    if (mqtt_ready) {
        mqtt_client_cleanup();
    }

    log_info("Agent stopped gracefully.");
}
