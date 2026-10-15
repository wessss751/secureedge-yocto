#ifndef SECUREEDGE_MQTT_CLIENT_H
#define SECUREEDGE_MQTT_CLIENT_H

#include <stdbool.h>

#include "sensor.h"

bool mqtt_client_init(
    const char *host,
    int port,
    const char *device_id
);

bool mqtt_client_publish(const sensor_data_t *data);

void mqtt_client_cleanup(void);

#endif
