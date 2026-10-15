#ifndef SECUREEDGE_SENSOR_H
#define SECUREEDGE_SENSOR_H

#include <stdbool.h>
#include <stdint.h>

typedef struct {
    float temperature_c;
    float voltage_v;
    uint32_t sequence;
    bool valid;
} sensor_data_t;

sensor_data_t sensor_read(void);
bool sensor_validate(const sensor_data_t *data);

#endif
