#include "extern_ctxt.h"


typedef void (*spawn_actor_fn)(void* actor_ctxt, void* actor_data, z64_game_t* game_ctxt);
#define spawn_actor ((spawn_actor_fn)0x800255C4)
typedef int (*get_object_index_fn)(z64_obj_ctxt_t* obj_ctxt, uint16_t object_id);
#define get_object_index ((get_object_index_fn)0x80081628)
typedef void (*spawn_object_fn)(z64_obj_ctxt_t* obj_ctxt, uint16_t object_id);
#define spawn_object ((spawn_object_fn)0x800812F0)


typedef enum {
	UINT8  = 0,
	INT8   = 1,
	UINT16 = 2,
	INT16  = 3,
	UINT32 = 4,
	INT32  = 5,
	FLOAT  = 6,
} DataType_t;

typedef enum {
	DEAD   = 0,
	NEW    = 1,
	ACTIVE = 2,
	REVERT = 3,
} WriteState_t;

/*
	The addressWrites struct describes RAM data that should be 
	modified and held. Setting the state to NEW will initialize 
	the oldValue for reverting afterwards. Setting to REVERT will
	set it back to the original value and then change the
	state to DEAD. Setting to DEAD directly will immediate
	end the effect without revertting.

	Setting the interpolateSpeed to 0 will make it instant.
	Otherwise it will transition between the target and original
	value at the specified speed.
*/

struct extern_ctxt_t {
	uint16_t          version;         /* 0x0000 */
	uint16_t          newObject;       /* 0x0002 */
	struct {
		uint16_t      id;              /* 0x0004 */
		int16_t       x;               /* 0x0006 */
		int16_t       y;               /* 0x0008 */
		int16_t       z;               /* 0x000A */
		int16_t       xrot;            /* 0x000C */
		int16_t       yrot;            /* 0x000E */
		int16_t       zrot;            /* 0x0010 */
		uint16_t      var;             /* 0x0012 */
	} newActor;
	struct {
		uint32_t      address;         /* 0x0014 + (i * 0x18) */
		float         newValue;        /* 0x0018 + (i * 0x18) */
		float         speed;           /* 0x001C + (i * 0x18) */
		DataType_t    dataType;        /* 0x0020 + (i * 0x18) */
		WriteState_t  state;           /* 0x0021 + (i * 0x18) */
		float         curValue;        /* 0x0024 + (i * 0x18) */
		float         oldValue;        /* 0x0028 + (i * 0x18) */
	} addressWrites[0x10];
} extern_ctxt = { .version = 1 };


float readValue(uint32_t address, DataType_t type) {
	switch (type) {
		case UINT8:
			return (float)(*(uint8_t*)address);
		case INT8:
			return (float)(*(int8_t*)address);
		case UINT16:
			return (float)(*(uint16_t*)address);
		case INT16:
			return (float)(*(int16_t*)address);
		case UINT32:
			return (float)(*(uint32_t*)address);
		case INT32:
			return (float)(*(int32_t*)address);
		case FLOAT:
			return (float)(*(float*)address);
	}
}


void writeValue(uint32_t address, DataType_t type, float value) {
	switch (type) {
		case UINT8:
			(*(uint8_t*)address) = (uint8_t)value;
			break;
		case INT8:
			(*(int8_t*)address) = (int8_t)value;
			break;
		case UINT16:
			(*(uint16_t*)address) = (uint16_t)value;
			break;
		case INT16:
			(*(int16_t*)address) = (int16_t)value;
			break;
		case UINT32:
			(*(uint32_t*)address) = (uint32_t)value;
			break;
		case INT32:
			(*(int32_t*)address) = (int32_t)value;
			break;
		case FLOAT:
			(*(float*)address) = (float)value;
			break;
	}
}


float interpolate(float value, float target, float speed) {
	float newValue;

	if (speed == 0) {
		return target;
	}

	newValue = value + speed;
	if (value < target) {
		if (newValue > target) {
			return target;
		}
	} 
	else if (newValue < target) {
		return target;
	}

	return newValue;
}


void process_extern_ctxt() {
	/* Load an object */
	if (extern_ctxt.newObject != 0x0000) {
		if (get_object_index(&(z64_game.obj_ctxt), extern_ctxt.newObject) < 0) {
			/* Only load the object if it's not yet loaded */
			spawn_object(&(z64_game.obj_ctxt), extern_ctxt.newObject);
		}
		extern_ctxt.newObject = 0x0000;
	}

	/* Spawn an actor */
	if (extern_ctxt.newActor.id != 0x0000) {
		spawn_actor(&(z64_game.actor_ctxt), &extern_ctxt.newActor, &z64_game);
		extern_ctxt.newActor.id = 0x0000;
	}

	/* Run addressWrite commands */
	float value;
	for (int i = 0; i < 0x10; i++) {
		if (extern_ctxt.addressWrites[i].state == DEAD) {
			continue;
		}

		value = readValue(extern_ctxt.addressWrites[i].address, extern_ctxt.addressWrites[i].dataType);

		if (extern_ctxt.addressWrites[i].state == NEW) {
			/* Initialize the starting oldValue */
			extern_ctxt.addressWrites[i].oldValue = value;
			extern_ctxt.addressWrites[i].state = ACTIVE;
		}
		else if (value != extern_ctxt.addressWrites[i].curValue) {
			/* Update oldValue if the game modifies it */
			extern_ctxt.addressWrites[i].oldValue = value;
		}

		/* Write new value */
		if (extern_ctxt.addressWrites[i].state == REVERT) {
			value = interpolate(value, extern_ctxt.addressWrites[i].oldValue, -extern_ctxt.addressWrites[i].speed);
		} 
		else {
			value = interpolate(value, extern_ctxt.addressWrites[i].newValue, extern_ctxt.addressWrites[i].speed);
		}
		extern_ctxt.addressWrites[i].curValue = value;
		writeValue(extern_ctxt.addressWrites[i].address, extern_ctxt.addressWrites[i].dataType, value);
	}
}
