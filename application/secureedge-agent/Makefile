CC ?= gcc

override CPPFLAGS += -Iinclude
CFLAGS += -Wall -Wextra -Wpedantic -std=c11 -O2

TARGET = secureedge-agent

SOURCES = \
    src/main.c \
    src/agent.c \
    src/logger.c

OBJECTS = $(SOURCES:.c=.o)

.PHONY: all clean

all: $(TARGET)

$(TARGET): $(OBJECTS)
	$(CC) $(OBJECTS) -o $@ $(LDFLAGS)

%.o: %.c
	$(CC) $(CPPFLAGS) $(CFLAGS) -c $< -o $@

clean:
	rm -f $(OBJECTS) $(TARGET)
