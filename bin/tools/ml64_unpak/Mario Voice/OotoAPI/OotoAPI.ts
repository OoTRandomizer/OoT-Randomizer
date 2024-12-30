import { INetworkPlayer } from "modloader64_api/NetworkHandler";

export enum OotOnlineEvents {
  PLAYER_PUPPET_PRESPAWN = 'OotOnline:onPlayerPuppetPreSpawned',
  PLAYER_PUPPET_SPAWNED = 'OotOnline:onPlayerPuppetSpawned',
  PLAYER_PUPPET_DESPAWNED = 'OotOnline:onPlayerPuppetDespawned',
  SERVER_PLAYER_CHANGED_SCENES = 'OotOnline:onServerPlayerChangedScenes',
  CLIENT_REMOTE_PLAYER_CHANGED_SCENES = 'OotOnline:onRemotePlayerChangedScenes',
  GHOST_MODE = 'OotOnline:EnableGhostMode',
  GAINED_HEART_CONTAINER = 'OotOnline:GainedHeartContainer',
  GAINED_PIECE_OF_HEART = 'OotOnline:GainedPieceOfHeart',
  MAGIC_METER_INCREASED = 'OotOnline:GainedMagicMeter',
  CUSTOM_MODEL_APPLIED_ADULT = 'OotOnline:ApplyCustomModelAdult',
  CUSTOM_MODEL_APPLIED_CHILD = 'OotOnline:ApplyCustomModelChild',
  CUSTOM_MODEL_APPLIED_ANIMATIONS = 'OotOnline:ApplyCustomAnims',
  CUSTOM_MODEL_APPLIED_ICON_ADULT = 'OotOnline:ApplyCustomIconAdult',
  CUSTOM_MODEL_APPLIED_ICON_CHILD = 'OotOnline:ApplyCustomIconChild',
  CUSTOM_MODEL_APPLIED_EQUIPMENT = "OotOnline:ApplyCustomEquipment",
  CUSTOM_MODEL_APPLIED_ADULT_MATRIX_SWORD_BACK = "OotOnline:CUSTOM_MODEL_APPLIED_ADULT_MATRIX_SWORD_BACK",
  CUSTOM_MODEL_APPLIED_ADULT_MATRIX_SHIELD_BACK = "OotOnline:CUSTOM_MODEL_APPLIED_ADULT_MATRIX_MATRIX_SHIELD_BACK",
  CUSTOM_MODEL_APPLIED_CHILD_MATRIX_SWORD_BACK = "OotOnline:CUSTOM_MODEL_APPLIED_CHILD_MATRIX_SWORD_BACK",
  CUSTOM_MODEL_APPLIED_CHILD_MATRIX_SHIELD_BACK = "OotOnline:CUSTOM_MODEL_APPLIED_CHILD_MATRIX_SHIELD_BACK",
  CUSTOM_MODEL_APPLIED_CHILD_MATRIX_ITEM_SHIELD = "OotOnline:CUSTOM_MODEL_APPLIED_CHILD_MATRIX_ITEM_SHIELD",
  CUSTOM_ICONS_APPLIED = "OotOnline:CUSTOM_ICONS_APPLIED",
  ON_INVENTORY_UPDATE = 'OotOnline:OnInventoryUpdate',
  ON_EXTERNAL_ACTOR_SYNC_LOAD = 'OotOnline:OnExternalActorSyncLoad',
  ON_REGISTER_EMOTE = 'OotOnline:OnRegisterEmote',
  ON_LOAD_SOUND_PACK = "OotOnline:OnLoadSoundPack",
  ON_REMOTE_SOUND_PACK = "OotOnline:OnRemoteSoundPack",
  ON_REMOTE_PLAY_SOUND = "OotOnline:OnRemotePlaySound"
}

export class RemoteSoundPlayRequest {

  player: INetworkPlayer;
  puppet: any;
  sound_id: number;
  isCanceled: boolean = false;

  constructor(player: INetworkPlayer, puppet: any, sound_id: number){
    this.player = player;
    this.puppet = puppet;
    this.sound_id = sound_id;
  }
}