#include "weather.h"
#include "z64.h"

#define KAKARIKO_WEATHER_REPORT_SUNNY_WITH_A_HIGH_OF_28_DEGREES 0
#define KAKARIKO_WEATHER_REPORT_A_MIX_OF_SUNNY_AND_OVERCAST_SKIES_WITH_A_HIGH_OF_32_DEGREES 1
#define KAKARIKO_WEATHER_REPORT_SUNNY_WITH_A_CHANCE_OF_SEVERE_THUNDERSTORMS 2

uint8_t KAKARIKO_WEATHER_FORECAST = 0;

void override_weather_state() {
    z64_fog_state = 0;
    KAKARIKO_WEATHER_FORECAST = KAKARIKO_WEATHER_REPORT_SUNNY_WITH_A_HIGH_OF_28_DEGREES;
    if (z64_file.link_age != 0 || z64_file.scene_setup_index >= 4) {
        return;
    }
    // Hyrule Market
    if (z64_file.entrance_index == 0x01FD) { //Hyrule Field by Market Entrance
        z64_fog_state = 1;
        return;
    }
    // Lon Lon Ranch (No Epona)
    if (!(z64_file.event_chk_inf[1] & 0x0100)){ //if you don't have Epona
        switch (z64_file.entrance_index) {
        case 0x0157: // Lon Lon Ranch
        case 0x01F9: // Hyrule Field
            z64_fog_state = 2;
            return;
        }
    }
    // Water Temple
    if (!(z64_file.event_chk_inf[4] & 0x0400)) { //have not beaten Water Temple
        switch (z64_file.entrance_index) {
        case 0x019D: //Zora River
        case 0x01DD: //Zora River
        case 0x04DA: //Lost Woods
            z64_fog_state = 3;
            return;
        }
        switch (z64_game.scene_index) {
        case 88: // Zora's Domain
        case 89: // Zora's Fountain
            z64_fog_state = 3;
            return;
        }
    }
    // Kakariko Thunderstorm
    if (z64_file.forest_medallion && z64_file.fire_medallion && z64_file.water_medallion
        && !(z64_file.scene_flags[24].clear & 0x02)) { //have not beaten Bongo Bongo
        switch (z64_game.scene_index)
        {
        case 82:
        case 83:
            KAKARIKO_WEATHER_FORECAST = KAKARIKO_WEATHER_REPORT_SUNNY_WITH_A_CHANCE_OF_SEVERE_THUNDERSTORMS;
            switch (z64_file.entrance_index)
            {
            case 0x00DB: // Kakariko Entrance
            case 0x0191: // Kakariko from Death Mountain Trail
            case 0x0205: // Graveyard from Shadow Temple
                break;
            default:
                z64_fog_state = 5;
                return;
            }
        }
    }
    // Death Mountain Cloudy
    if (!(z64_file.event_chk_inf[4] & 0x0200)) { //have not beaten Fire Temple
        if (z64_game.entrance_index == 0x04D6) { //Lost Woods Goron City Shortcut
            z64_fog_state = 2;
            return;
        }
        switch (z64_game.scene_index) {
        case 82: // Kakariko
        case 83: // Graveyard
        case 96: // Death Mountain Trail
        case 97: // Death Mountain Crater
            if (!KAKARIKO_WEATHER_FORECAST) {
                KAKARIKO_WEATHER_FORECAST = KAKARIKO_WEATHER_REPORT_A_MIX_OF_SUNNY_AND_OVERCAST_SKIES_WITH_A_HIGH_OF_32_DEGREES;
            }
            switch (z64_file.entrance_index) {
            case 0x00DB: // Kakariko Entrance
            case 0x0195: // Kakariko from Graveyard
                break;
            default:
                z64_fog_state = 2;
                return;
            }
        }
    }
}
