from pygame import Color
from wideboy.sprites.image_helpers import MaterialIcons
from wideboy.sprites.homeassistant.entity_row import HomeAssistantEntityTile
from wideboy.config import settings

from typing import Any

# GENERAL


class TileStepsLouis(HomeAssistantEntityTile):
    icon = MaterialIcons.MDI_DIRECTIONS_WALK
    icon_color = Color(255, 0, 255, 255)

    def process(self, state):
        value = state.get("sensor.steps_louis", 0)
        self.visible = value > 0
        self.label = f"{value:.0f}"


class TileVPN(HomeAssistantEntityTile):
    icon = MaterialIcons.MDI_LOCK
    icon_color = Color(255, 0, 0, 255)

    def process(self, state):
        value = state.get("sensor.privacy_ip_info", None)
        self.visible = value == settings.secrets.home_ip
        self.label = f"VPN DOWN ({value})"


class TileTransmission(HomeAssistantEntityTile):
    icon = MaterialIcons.MDI_VPN_LOCK
    icon_color = Color(255, 255, 255, 255)

    def process(self, state):
        value = state.get("sensor.transmission_down_speed", 0)
        self.visible = value > 0
        self.label = f"{value:.0f}Mbps"


class TileDS920Plus(HomeAssistantEntityTile):
    icon = MaterialIcons.MDI_DNS
    icon_color = Color(255, 255, 0, 255)

    def process(self, state):
        value = state.get("sensor.ds920plus_volume_used", 0)
        self.visible = value > 66.66
        self.label = f"{value:.0f}%"


class TileSpeedtestDownload(HomeAssistantEntityTile):
    icon = MaterialIcons.MDI_DOWNLOAD
    icon_color = Color(0, 255, 0, 255)

    def process(self, state):
        value = state.get("sensor.speedtest_download_average", 0)
        self.visible = value < 600
        self.label = f"{value:.0f}Mbps"


class TileSpeedtestUpload(HomeAssistantEntityTile):
    icon = MaterialIcons.MDI_UPLOAD
    icon_color = Color(255, 0, 0, 255)

    def process(self, state):
        value = state.get("sensor.speedtest_upload_average", 0)
        self.visible = value < 600
        self.label = f"{value:.0f}Mbps"


class TileSpeedtestPing(HomeAssistantEntityTile):
    icon = MaterialIcons.MDI_WIFI
    icon_color = Color(0, 0, 255, 255)

    def process(self, state):
        value = state.get("sensor.speedtest_ping_average", 0)
        self.visible = value > 10
        self.label = f"{value:.0f}ms"


class TileBinCollection(HomeAssistantEntityTile):
    icon = MaterialIcons.MDI_DELETE
    icon_color = Color(192, 192, 192, 255)

    def process(self, state):
        value = state.get("calendar.bin_collection")
        self.visible = value <= 1
        self.label = f"{value}"


class TileBackDoor(HomeAssistantEntityTile):
    icon = MaterialIcons.MDI_DOOR
    icon_color = Color(255, 64, 64, 255)
    label = "Back"

    def process(self, state):
        self.visible = (
            state.get("binary_sensor.back_door_contact_sensor_contact") == True
        )


class TileFrontDoor(HomeAssistantEntityTile):
    icon = MaterialIcons.MDI_DOOR
    icon_color = Color(255, 64, 64, 255)
    label = "Front"

    def process(self, state):
        self.visible = (
            state.get("binary_sensor.front_door_contact_sensor_contact") == True
        )


class TileHouseManual(HomeAssistantEntityTile):
    icon = MaterialIcons.MDI_TOGGLE_ON
    icon_color = Color(255, 0, 0, 255)
    label = "MANUAL"

    def process(self, state):
        self.visible = state.get("input_boolean.house_manual") == True


class TileSwitchLoungeFans(HomeAssistantEntityTile):
    icon = MaterialIcons.MDI_AC_UNIT
    icon_color = Color(196, 196, 255, 255)
    label = "ON"

    def process(self, state):
        self.visible = state.get("switch.lounge_fans") == True


# ELECTRICITY


class TileElectricityCurrentDemand(HomeAssistantEntityTile):
    icon = MaterialIcons.MDI_BOLT
    icon_color = Color(192, 192, 192, 255)

    def process(self, state):
        value = state.get("sensor.octopus_energy_electricity_current_demand", 0)
        self.visible = value > 0
        self.label = f"{value:.0f}w"
        self.icon_color = (
            Color(255, 64, 64, 255) if value > 500 else Color(64, 255, 64, 255)
        )


class TileElectricityCurrentRate(HomeAssistantEntityTile):
    icon = MaterialIcons.MDI_SYMBOL_AT
    icon_color = Color(192, 192, 192, 255)

    def process(self, state: dict[str, Any]):
        value = state.get("sensor.octopus_energy_electricity_current_rate", 0)
        self.visible = value > 0
        self.label = f"£{value:.2f}"
        self.icon_color = (
            Color(255, 64, 64, 255) if value > 0.30 else Color(64, 255, 64, 255)
        )


class TileElectricityHourlyRate(HomeAssistantEntityTile):
    icon = MaterialIcons.MDI_CURRENCY_DOLLAR
    icon_color = Color(255, 64, 64, 255)

    def process(self, state):
        value = state.get("sensor.electricity_hourly_rate", 0)
        self.visible = value > 0
        self.label = f"{value:.2f}"
        self.icon_color = (
            Color(255, 64, 64, 255) if value > 0.50 else Color(64, 255, 64, 255)
        )


class TileElectricityCurrentAccumulativeCost(HomeAssistantEntityTile):
    icon = MaterialIcons.MDI_SCHEDULE
    icon_color = Color(255, 64, 64, 255)

    def process(self, state):
        value = state.get(
            "sensor.octopus_energy_electricity_current_accumulative_cost", 0
        )
        self.visible = value > 0
        self.label = f"{value:.2f}"
        self.icon_color = (
            Color(255, 64, 64, 255) if value > 2.50 else Color(64, 255, 64, 255)
        )


# BATTERY


class TileBatteryLevel(HomeAssistantEntityTile):
    icon = MaterialIcons.MDI_BATTERY
    icon_color = Color(192, 192, 192, 255)

    def process(self, state):
        value = state.get("sensor.delta_2_max_downstairs_battery_level", 0)
        self.visible = value > 0
        self.label = f"{value:.0f}%"
        self.icon_color = (
            Color(255, 64, 64, 255) if value < 30 else Color(64, 255, 64, 255)
        )


class TileBatteryCycles(HomeAssistantEntityTile):
    icon = MaterialIcons.MDI_LOOP
    icon_color = Color(192, 192, 192, 255)

    def process(self, state):
        value = state.get("sensor.delta_2_max_downstairs_cycles", 0)
        self.visible = value > 0
        self.label = f"{value:.0f}"


class TileBatteryDischargeRemainingTime(HomeAssistantEntityTile):
    icon = MaterialIcons.MDI_HOURGLASS
    icon_color = Color(255, 64, 64, 255)

    def process(self, state):
        value = state.get("sensor.delta_2_max_downstairs_discharge_remaining_time", 0)
        hours, mins = value // 60, value % 60
        self.visible = value > 0
        self.label = f"{hours:.0f}h{mins:.0f}m"


class TileBatteryChargeRemainingTime(HomeAssistantEntityTile):
    icon = MaterialIcons.MDI_HOURGLASS
    icon_color = Color(64, 255, 64, 255)

    def process(self, state):
        value = state.get("sensor.delta_2_max_downstairs_charge_remaining_time", 0)
        hours, mins = value // 60, value % 60
        self.visible = value > 0
        self.label = f"{hours:.0f}h{mins:.0f}m"


class TileBatteryAcInPower(HomeAssistantEntityTile):
    icon = MaterialIcons.MDI_POWER
    icon_color = Color(255, 64, 64, 255)

    def process(self, state):
        value = state.get("sensor.delta_2_max_downstairs_ac_in_power", 0)
        self.visible = value > 0
        self.label = f"{value:.0f}w"
