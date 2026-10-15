#include <assert.h>
#include <stdio.h>

#include "sensor.h"

int main(void)
{
    sensor_data_t data = sensor_read();

    assert(data.sequence == 1);
    assert(data.temperature_c == 25.0f);
    assert(data.voltage_v == 24.0f);
    assert(data.valid == true);

    data.temperature_c = 150.0f;

    assert(sensor_validate(&data) == false);

    data.temperature_c = 25.0f;
    data.voltage_v = 0.0f;

    assert(sensor_validate(&data) == false);

    assert(sensor_validate(NULL) == false);

    printf("All sensor tests passed.\n");

    return 0;
}
