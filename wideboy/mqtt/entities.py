from wideboy.mqtt.homeassistant import HASSEntity

HASS_MASTER = HASSEntity(
    "master",
    "light",
    dict(brightness=True, color_mode=True, supported_color_modes=["brightness"]),
    initial_state=dict(state="ON", brightness=128),
)

HASS_ACTION_SCENE_NEXT = HASSEntity(
    "action_scene_next", "switch", initial_state=dict(state="OFF")
)
