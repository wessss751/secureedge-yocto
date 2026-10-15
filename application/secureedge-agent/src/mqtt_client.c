#include <stdbool.h>
#include <stddef.h>
#include <stdio.h>
#include <stdatomic.h>
#include <ctype.h>
#include <string.h>
#include <mosquitto.h>

#include "mqtt_client.h"
#include "logger.h"

#define MQTT_TOPIC_SIZE 128

static char mqtt_topic[MQTT_TOPIC_SIZE];
static struct mosquitto *client = NULL;
static atomic_bool connected = ATOMIC_VAR_INIT(false);
static bool library_initialized = false;
static bool loop_started = false;

/*
 * Called when the broker accepts or rejects our MQTT connection.
 */
static void on_connect(
    struct mosquitto *mosq,
    void *userdata,
    int result
)
{
    (void)mosq;
    (void)userdata;

    atomic_store(&connected, result == 0);

    if (result == 0) {
        log_info("MQTT connected successfully");
    } else {
        log_info("MQTT connection refused: %d", result);
    }
}

/*
 * Called when the MQTT connection is interrupted or closed.
 */
static void on_disconnect(
    struct mosquitto *mosq,
    void *userdata,
    int result
)
{
    (void)mosq;
    (void)userdata;

    atomic_store(&connected, false);

    log_info("MQTT disconnected (code=%d)", result);
}
static bool device_id_is_valid(const char *device_id)
{
    if (device_id == NULL || device_id[0] == '\0') {
        return false;
    }

    for (const unsigned char *p =
             (const unsigned char *)device_id; *p != '\0'; ++p) {

        if (!isalnum(*p) && *p != '-' && *p != '_') {
            return false;
        }
    }

    return true;

}
bool mqtt_client_init(
    const char *host,
    int port,
    const char *device_id
)
{
if (host == NULL || host[0] == '\0' ||
    port <= 0 || port > 65535 ||
    !device_id_is_valid(device_id)) {

    log_info("Invalid MQTT configuration");
    return false;
    }
    int topic_length = snprintf(
    mqtt_topic,
    sizeof(mqtt_topic),
    "secureedge/%s/telemetry",
    device_id
);

if (topic_length < 0 ||
    (size_t)topic_length >= sizeof(mqtt_topic)) {

    log_info("MQTT topic is too long");
    return false;
}

log_info("MQTT topic configured: %s", mqtt_topic);
    int rc = mosquitto_lib_init();

    if (rc != MOSQ_ERR_SUCCESS) {
        log_info("MQTT library initialization failed: %s",
                 mosquitto_strerror(rc));
        return false;
    }

    library_initialized = true;

    client = mosquitto_new("secureedge-device01", true, NULL);

    if (client == NULL) {
        log_info("MQTT client creation failed");
        mqtt_client_cleanup();
        return false;
    }

    mosquitto_connect_callback_set(client, on_connect);
    mosquitto_disconnect_callback_set(client, on_disconnect);

    /*
     * Retry after 5 seconds, increasing up to 30 seconds.
     */
    rc = mosquitto_reconnect_delay_set(client, 5, 30, true);

    if (rc != MOSQ_ERR_SUCCESS) {
        log_info("MQTT reconnect configuration failed: %s",
                 mosquitto_strerror(rc));
        mqtt_client_cleanup();
        return false;
    }

    /*
     * Configure an asynchronous connection.
     */
    rc = mosquitto_connect_async(client, host, port, 60);

    if (rc != MOSQ_ERR_SUCCESS) {
        log_info("MQTT connection setup failed: %s",
                 mosquitto_strerror(rc));
        mqtt_client_cleanup();
        return false;
    }

    /*
     * Start a background thread to process MQTT network traffic.
     */
    rc = mosquitto_loop_start(client);

    if (rc != MOSQ_ERR_SUCCESS) {
        log_info("MQTT loop start failed: %s",
                 mosquitto_strerror(rc));
        mqtt_client_cleanup();
        return false;
    }

    loop_started = true;

    log_info("MQTT network loop started");

    return true;
}

bool mqtt_client_publish(const sensor_data_t *data)
{
    if (client == NULL ||
        data == NULL ||
        !atomic_load(&connected)) {
        return false;
    }

    char payload[256];

    int length = snprintf(
        payload,
        sizeof(payload),
        "{\"sequence\":%u,"
        "\"temperature_c\":%.2f,"
        "\"voltage_v\":%.2f,"
        "\"valid\":%s}",
        (unsigned int)data->sequence,
        (double)data->temperature_c,
        (double)data->voltage_v,
        data->valid ? "true" : "false"
    );

    if (length < 0 || (size_t)length >= sizeof(payload)) {
        log_info("MQTT payload formatting failed");
        return false;
    }

    int rc = mosquitto_publish(
       client,
       NULL,
       mqtt_topic,
       length,
       payload,
       0,
       false
);
    if (rc != MOSQ_ERR_SUCCESS) {
        log_info("MQTT publish failed: %s",
                 mosquitto_strerror(rc));
        return false;
    }

    log_info("MQTT message queued: %s", payload);

    return true;
}

void mqtt_client_cleanup(void)
{
    atomic_store(&connected, false);

    if (client != NULL) {
        if (loop_started) {
            mosquitto_disconnect(client);
            mosquitto_loop_stop(client, false);
            loop_started = false;
        }

        mosquitto_destroy(client);
        client = NULL;
    }

    if (library_initialized) {
        mosquitto_lib_cleanup();
        library_initialized = false;
    }
}
