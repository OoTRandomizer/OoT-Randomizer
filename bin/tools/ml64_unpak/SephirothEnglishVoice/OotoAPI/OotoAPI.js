"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.RemoteSoundPlayRequest = exports.OotOnlineEvents = void 0;
var OotOnlineEvents;
(function (OotOnlineEvents) {
    OotOnlineEvents["PLAYER_PUPPET_PRESPAWN"] = "OotOnline:onPlayerPuppetPreSpawned";
    OotOnlineEvents["PLAYER_PUPPET_SPAWNED"] = "OotOnline:onPlayerPuppetSpawned";
    OotOnlineEvents["PLAYER_PUPPET_DESPAWNED"] = "OotOnline:onPlayerPuppetDespawned";
    OotOnlineEvents["SERVER_PLAYER_CHANGED_SCENES"] = "OotOnline:onServerPlayerChangedScenes";
    OotOnlineEvents["CLIENT_REMOTE_PLAYER_CHANGED_SCENES"] = "OotOnline:onRemotePlayerChangedScenes";
    OotOnlineEvents["GHOST_MODE"] = "OotOnline:EnableGhostMode";
    OotOnlineEvents["GAINED_HEART_CONTAINER"] = "OotOnline:GainedHeartContainer";
    OotOnlineEvents["GAINED_PIECE_OF_HEART"] = "OotOnline:GainedPieceOfHeart";
    OotOnlineEvents["MAGIC_METER_INCREASED"] = "OotOnline:GainedMagicMeter";
    OotOnlineEvents["CUSTOM_MODEL_APPLIED_ADULT"] = "OotOnline:ApplyCustomModelAdult";
    OotOnlineEvents["CUSTOM_MODEL_APPLIED_CHILD"] = "OotOnline:ApplyCustomModelChild";
    OotOnlineEvents["CUSTOM_MODEL_APPLIED_ANIMATIONS"] = "OotOnline:ApplyCustomAnims";
    OotOnlineEvents["CUSTOM_MODEL_APPLIED_ICON_ADULT"] = "OotOnline:ApplyCustomIconAdult";
    OotOnlineEvents["CUSTOM_MODEL_APPLIED_ICON_CHILD"] = "OotOnline:ApplyCustomIconChild";
    OotOnlineEvents["CUSTOM_MODEL_APPLIED_EQUIPMENT"] = "OotOnline:ApplyCustomEquipment";
    OotOnlineEvents["CUSTOM_MODEL_APPLIED_ADULT_MATRIX_SWORD_BACK"] = "OotOnline:CUSTOM_MODEL_APPLIED_ADULT_MATRIX_SWORD_BACK";
    OotOnlineEvents["CUSTOM_MODEL_APPLIED_ADULT_MATRIX_SHIELD_BACK"] = "OotOnline:CUSTOM_MODEL_APPLIED_ADULT_MATRIX_MATRIX_SHIELD_BACK";
    OotOnlineEvents["CUSTOM_MODEL_APPLIED_CHILD_MATRIX_SWORD_BACK"] = "OotOnline:CUSTOM_MODEL_APPLIED_CHILD_MATRIX_SWORD_BACK";
    OotOnlineEvents["CUSTOM_MODEL_APPLIED_CHILD_MATRIX_SHIELD_BACK"] = "OotOnline:CUSTOM_MODEL_APPLIED_CHILD_MATRIX_SHIELD_BACK";
    OotOnlineEvents["CUSTOM_MODEL_APPLIED_CHILD_MATRIX_ITEM_SHIELD"] = "OotOnline:CUSTOM_MODEL_APPLIED_CHILD_MATRIX_ITEM_SHIELD";
    OotOnlineEvents["CUSTOM_ICONS_APPLIED"] = "OotOnline:CUSTOM_ICONS_APPLIED";
    OotOnlineEvents["ON_INVENTORY_UPDATE"] = "OotOnline:OnInventoryUpdate";
    OotOnlineEvents["ON_EXTERNAL_ACTOR_SYNC_LOAD"] = "OotOnline:OnExternalActorSyncLoad";
    OotOnlineEvents["ON_REGISTER_EMOTE"] = "OotOnline:OnRegisterEmote";
    OotOnlineEvents["ON_LOAD_SOUND_PACK"] = "OotOnline:OnLoadSoundPack";
    OotOnlineEvents["ON_REMOTE_SOUND_PACK"] = "OotOnline:OnRemoteSoundPack";
    OotOnlineEvents["ON_REMOTE_PLAY_SOUND"] = "OotOnline:OnRemotePlaySound";
})(OotOnlineEvents = exports.OotOnlineEvents || (exports.OotOnlineEvents = {}));
class RemoteSoundPlayRequest {
    player;
    puppet;
    sound_id;
    isCanceled = false;
    constructor(player, puppet, sound_id) {
        this.player = player;
        this.puppet = puppet;
        this.sound_id = sound_id;
    }
}
exports.RemoteSoundPlayRequest = RemoteSoundPlayRequest;
//# sourceMappingURL=OotoAPI.js.map