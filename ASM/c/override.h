#ifndef OVERRIDE_H
#define OVERRIDE_H

#include <stdint.h>

typedef union overide_key_t {
    uint64_t all;
    struct {
        uint8_t scene;
        uint8_t type;
        uint16_t pad;
        uint32_t flag;
    };
} override_key_t;

// a type used when the cloak of an ice trap is irrelevant
typedef union override_value_base_t {
    uint32_t all;
    struct {
        uint16_t item_id;
        uint8_t player;
        uint8_t _pad;
    };
} override_value_base_t;

typedef struct {
    override_value_base_t base;
    uint16_t looks_like_item_id;
    uint16_t _pad;
} override_value_t;

typedef struct {
    override_key_t key;
    override_value_t value;
} override_t;

typedef struct {
    override_key_t  alt;
    override_key_t  primary;
} alt_override_t;

#endif
