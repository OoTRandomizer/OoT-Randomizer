//Change En_Weather_Tag to check for medallions
.headersize (0x80AD7270 - 0xE570B0)

//Weather Tag 4 (Cloudy, Fire Temple hasn't been beaten)
.org 0x80AD7390
.area 0x18, 0
    lui v1, hi(KAKARIKO_WEATHER_FORECAST)
    lbu t5, lo(KAKARIKO_WEATHER_FORECAST)(v1)
    li  t4, 1 // Cloudy
    beq t5, t4, @tag4_skip_actor_kill
    nop
.endarea
// Fall into Actor Kill call

.org 0x80AD73B0
@tag4_skip_actor_kill:

//Weather Tag 5 (Thunderstorm, Shadow Temple hasn't been completed)
.org 0x80AD73C8
.area 0x3C, 0
    lui v1, hi(KAKARIKO_WEATHER_FORECAST)
    lbu t5, lo(KAKARIKO_WEATHER_FORECAST)(v1)
    li  t4, 2 // Thunderstorm
    beq t5, t4, @tag5_skip_actor_kill
    nop
.endarea

.org 0x80AD740C
@tag5_skip_actor_kill:

.headersize 0