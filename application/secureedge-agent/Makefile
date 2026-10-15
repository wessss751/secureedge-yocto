CC ?= gcc

override CPPFLAGS += -Iinclude
CFLAGS += -Wall -Wextra -Wpedantic -std=c11 -O2 -pthread
LDFLAGS += -pthread

TARGET = secureedge-agent
LDLIBS += -lmosquitto
SOURCES = \
    src/main.c \
    src/agent.c \
    src/logger.c \
    src/sensor.c \
    src/mqtt_client.c \
    src/config.c
OBJECTS = $(SOURCES:.c=.o)

.PHONY: all clean

all: $(TARGET)

$(TARGET): $(OBJECTS)
	$(CC) $(OBJECTS) -o $@ $(LDFLAGS) $(LDLIBS)
%.o: %.c
	$(CC) $(CPPFLAGS) $(CFLAGS) -c $< -o $@

clean:
	rm -f $(OBJECTS) $(TARGET)
