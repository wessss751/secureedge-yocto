#define _POSIX_C_SOURCE 200809L

#include <signal.h>
#include <stdbool.h>
#include <stdlib.h>
#include <unistd.h>

#include "agent.h"
#include "logger.h"
#include "sensor.h"
#include "mqtt_client.h"
#include "config.h"

static volatile sig_atomic_t keep_running = 1;

void agent_request_stop(void)
{
    keep_running = 0;
}

void agent_run(void)
{
    agent_config_t config;

    const char *config_path = getenv("SECUREEDGE_CONFIG");

    if (config_path == NULL || config_path[0] == '\0') {
        config_path = "config/agent.conf";
    }

    if (!config_load(config_path, &config)) {
        log_info("Configuration loading failed");
        return;
    }

    log_info("Agent started. PID=%ld", (long)getpid());

    log_info(
        "Configuration loaded: device=%s, broker=%s:%d, interval=%u s",
        config.device_id,
        config.mqtt_host,
        config.mqtt_port,
        config.sampling_interval
    );

    bool mqtt_ready = mqtt_client_init(
        config.mqtt_host,
        config.mqtt_port
    );

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

        sleep(config.sampling_interval);
    }

    if (mqtt_ready) {
        mqtt_client_cleanup();
    }

    log_info("Agent stopped gracefully.");
}
