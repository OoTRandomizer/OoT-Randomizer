#include "entrance_table.h"

// Entrance Table
//
// Copy of the vanilla entrance table, populated at patch time
// Additional entries are appended for new entrances and exits, such as grottos
//
// See cloudmodding for table format: https://wiki.cloudmodding.com/oot/Entrance_Table
// New entrances must have a minimum of four entries appended to work with the entrance system.
// Each entry is 4 bytes.

EntranceInfo gExtendedEntranceTable[EXTENDED_TABLE_SIZE] = {};
