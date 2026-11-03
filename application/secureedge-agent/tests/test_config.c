#define _POSIX_C_SOURCE 200809L

#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#include "config.h"

static void write_config(FILE *file, const char *content)
{
    assert(fputs(content, file) >= 0);
    assert(fflush(file) == 0);
}

int main(void)
{
    char path[] = "/tmp/secureedge-config-test-XXXXXX";

    int fd = mkstemp(path);
    assert(fd >= 0);

    FILE *file = fdopen(fd, "w");
    assert(file != NULL);

    agent_config_t config;

    write_config(
        file,
        "mqtt_host=127.0.0.1\n"
        "mqtt_port=1883\n"
        "device_id=device02\n"
        "sampling_interval=2\n"
    );

    assert(config_load(path, &config) == true);

    assert(strcmp(config.mqtt_host, "127.0.0.1") == 0);
    assert(config.mqtt_port == 1883);
    assert(strcmp(config.device_id, "device02") == 0);
    assert(config.sampling_interval == 2);

    assert(freopen(path, "w", file) != NULL);

    write_config(file, "mqtt_port=99999\n");

    assert(config_load(path, &config) == false);

    assert(freopen(path, "w", file) != NULL);

    write_config(file, "unknown_parameter=test\n");

    assert(config_load(path, &config) == false);

    assert(fclose(file) == 0);
    assert(unlink(path) == 0);

    puts("PASS: configuration tests");

    return 0;
}
