; Hacks in en_anubice_tag (Anubis Spawner)
.headersize(0x80A2FF70 - 0xDB9AA0)

; Hack call to Actor_SpawnAsChild so we can add a flag to the spawned anubis
.org 0x80a30018
; Replaces
;   jal     Actor_SpawnAsChild
    jal     EnAnubiceTag_SpawnChild
