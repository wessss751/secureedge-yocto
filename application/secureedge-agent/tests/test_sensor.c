#include <assert.h>
#include <stdio.h>

#include "sensor.h"

int main(void)
{
    sensor_data_t data = sensor_read();

    /* Test 1: expected first simulated sample */
    assert(data.sequence == 1);
    assert(data.temperature_c == 25.0f);
    assert(data.voltage_v == 24.0f);
    assert(data.valid == true);

    /* Test 2: valid measurement */
    assert(sensor_validate(&data) == true);

    /* Test 3: temperature outside accepted range */
    data.temperature_c = 150.0f;
    assert(sensor_validate(&data) == false);

    /* Test 4: voltage outside accepted range */
    data.temperature_c = 25.0f;
    data.voltage_v = 0.0f;
    assert(sensor_validate(&data) == false);

    /* Test 5: null pointer */
    assert(sensor_validate(NULL) == false);

    puts("PASS: sensor tests");

    return 0;
}
