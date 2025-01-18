extended_object_lookup_GI:
    BGE     T8, 0x192, @@extended_item
    nop
    @@normal_item:
    LUI     T0, 0x8010
    JR RA
    ADDIU   T0, T0, 0x8FF8
    @@extended_item:
    LA      T0, EXTENDED_OBJECT_TABLE
    JR      RA
    ADDIU   T8, T8, -0x193

extended_object_lookup_load:
    ADDU    V1, A0, T6  ; displaced
    BGE     A2, 0x192, @@extended_item
    nop
    @@normal_item:
    LUI     T9, 0x8010
    JR      RA
    ADDIU   T9, T9, 0x8FF8
    @@extended_item:
    LA      T9, EXTENDED_OBJECT_TABLE
    JR      RA
    ADDIU   A2, A2, -0x193


extended_object_lookup_shop:
    LH      T9, 0x00(S0) ; displaced
    LW      A1, 0x04(S0) ; displaced
    ADDIU   A0, S0, 0x08 ; displaced
    SUBU    T0, R0, T9 ; displaced
    ; T0 is item ID, S3 is table start
    BGE     T0, 0x192, @@extended_item
    nop
    @@normal_item:
    LUI     S3, 0x8010
    JR RA
    ADDIU   S3, S3, 0x8FF8
    @@extended_item:
    LA      S3, EXTENDED_OBJECT_TABLE
    JR      RA
    ADDIU   T0, T0, -0x193

extended_object_lookup_shop_unpause:
    LW      A0, 0x10(S0) ; displaced
    ; V1 is item ID, S3 is table start
    BGE     V1, 0x192, @@extended_item
    nop
    @@normal_item:
    LUI     S3, 0x8010
    J @@return
    ADDIU   S3, S3, 0x8FF8
    @@extended_item:
    LA      S3, EXTENDED_OBJECT_TABLE
    ADDIU   V1, V1, -0x193
    @@return:
    SLL     T7, V1, 0x3
    ADDU    V0, S3, T7
    JR      RA
    LW      A1, 0x0(V0)
