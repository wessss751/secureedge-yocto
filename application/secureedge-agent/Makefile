CC ?= gcc

override CPPFLAGS += -Iinclude

CFLAGS += -Wall -Wextra -Wpedantic -std=c11 -O2 -pthread
LDFLAGS += -pthread
LDLIBS += -lmosquitto

TARGET = secureedge-agent

SOURCES = \
    src/main.c \
    src/agent.c \
    src/logger.c \
    src/sensor.c \
    src/mqtt_client.c \
    src/config.c

OBJECTS = $(SOURCES:.c=.o)

TEST_SENSOR = tests/test_sensor
TEST_CONFIG = tests/test_config

.PHONY: all clean test

all: $(TARGET)

$(TARGET): $(OBJECTS)
	$(CC) $(OBJECTS) -o $@ $(LDFLAGS) $(LDLIBS)

%.o: %.c
	$(CC) $(CPPFLAGS) $(CFLAGS) -c $< -o $@

$(TEST_SENSOR): tests/test_sensor.c src/sensor.c include/sensor.h
	$(CC) $(CPPFLAGS) $(CFLAGS) tests/test_sensor.c src/sensor.c -o $@ $(LDFLAGS)

$(TEST_CONFIG): tests/test_config.c src/config.c include/config.h
	$(CC) $(CPPFLAGS) $(CFLAGS) tests/test_config.c src/config.c -o $@ $(LDFLAGS)

test: $(TEST_SENSOR) $(TEST_CONFIG)
	./$(TEST_SENSOR)
	./$(TEST_CONFIG)

clean:
	rm -f $(OBJECTS) $(TARGET) $(TEST_SENSOR) $(TEST_CONFIG)
