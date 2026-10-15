#include <stddef.h>

#include "sensor.h"

#define SENSOR_TEMP_MIN_C   (-20.0f)
#define SENSOR_TEMP_MAX_C   (85.0f)

#define SENSOR_VOLT_MIN_V   (20.0f)
#define SENSOR_VOLT_MAX_V   (28.0f)

sensor_data_t sensor_read(void)
{
    static uint32_t sequence = 0;

    sequence++;

    sensor_data_t data = {
        .temperature_c = 24.0f + (float)(sequence % 10),
        .voltage_v = 23.5f + (float)(sequence % 5) * 0.5f,
        .sequence = sequence,
        .valid = false
    };

    data.valid = sensor_validate(&data);

    return data;
}

bool sensor_validate(const sensor_data_t *data)
{
    if (data == NULL) {
        return false;
    }

    if (data->temperature_c < SENSOR_TEMP_MIN_C ||
        data->temperature_c > SENSOR_TEMP_MAX_C) {
        return false;
    }

    if (data->voltage_v < SENSOR_VOLT_MIN_V ||
        data->voltage_v > SENSOR_VOLT_MAX_V) {
        return false;
    }

    return true;
}
