#ifndef SECUREEDGE_CONFIG_H
#define SECUREEDGE_CONFIG_H

#include <stdbool.h>

#define CONFIG_HOST_SIZE 128
#define CONFIG_DEVICE_SIZE 64

typedef struct {
    char mqtt_host[CONFIG_HOST_SIZE];
    int mqtt_port;
    char device_id[CONFIG_DEVICE_SIZE];
    unsigned int sampling_interval;
} agent_config_t;

bool config_load(const char *path, agent_config_t *config);

#endif

