#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "config.h"

static char *trim(char *text)
{
    while (isspace((unsigned char)*text)) {
        text++;
    }

    if (*text == '\0') {
        return text;
    }

    char *end = text + strlen(text) - 1;

    while (end > text && isspace((unsigned char)*end)) {
        *end-- = '\0';
    }

    return text;
}

static bool copy_value(char *destination, size_t size, const char *value)
{
    size_t length = strlen(value);

    if (length == 0 || length >= size) {
        return false;
    }

    memcpy(destination, value, length + 1);
    return true;
}

static bool parse_number(const char *value, unsigned long maximum,
                         unsigned long *result)
{
    if (*value == '\0' || !isdigit((unsigned char)*value)) {
        return false;
    }

    char *end = NULL;
    unsigned long number = strtoul(value, &end, 10);

    if (*end != '\0' || number == 0 || number > maximum) {
        return false;
    }

    *result = number;
    return true;
}

bool config_load(const char *path, agent_config_t *config)
{
    if (path == NULL || config == NULL) {
        return false;
    }

    FILE *file = fopen(path, "r");

    if (file == NULL) {
        perror("SecureEdge config");
        return false;
    }

    *config = (agent_config_t){
        .mqtt_host = "127.0.0.1",
        .mqtt_port = 1883,
        .device_id = "device01",
        .sampling_interval = 5
    };

    char line[256];
    bool success = true;

    while (fgets(line, sizeof(line), file) != NULL) {
        if (strchr(line, '\n') == NULL && !feof(file)) {
            success = false;
            break;
        }

        char *entry = trim(line);

        if (*entry == '#' || *entry == '\0') {
            continue;
        }

        char *separator = strchr(entry, '=');

        if (separator == NULL) {
            success = false;
            break;
        }

        *separator = '\0';

        char *key = trim(entry);
        char *value = trim(separator + 1);

        unsigned long number;

        if (strcmp(key, "mqtt_host") == 0) {
            success = copy_value(config->mqtt_host,
                                 sizeof(config->mqtt_host), value);
        } else if (strcmp(key, "device_id") == 0) {
            success = copy_value(config->device_id,
                                 sizeof(config->device_id), value);
        } else if (strcmp(key, "mqtt_port") == 0) {
            success = parse_number(value, 65535, &number);

            if (success) {
                config->mqtt_port = (int)number;
            }
        } else if (strcmp(key, "sampling_interval") == 0) {
            success = parse_number(value, 3600, &number);

            if (success) {
                config->sampling_interval = (unsigned int)number;
            }
        } else {
            fprintf(stderr, "Unknown config key: %s\n", key);
            success = false;
        }

        if (!success) {
            fprintf(stderr, "Invalid configuration entry: %s\n", key);
            break;
        }
    }

    if (ferror(file)) {
        success = false;
    }

    fclose(file);

    return success;
}

