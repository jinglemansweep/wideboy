from pygame import Color
from wideboy.sprites.image_helpers import MaterialIcons
from wideboy.sprites.homeassistant.entity_grid import HomeAssistantEntityGridTile
from wideboy.sprites.homeassistant.entity_row import HomeAssistantEntityTile
from wideboy.config import settings

from typing import Any


def number_to_color(
    number: float, ranges=[0.3, 0.6, 1.0], brightness=255, invert=False
) -> Color:
    color_low = Color(brightness, 0, 0, 255)
    color_mid = Color(brightness, brightness, 0, 255)
    color_high = Color(0, brightness, 0, 255)
    color_default = Color(0, 0, 0, 255)
    if invert:
        color_low, color_high = color_high, color_low
    if number < ranges[0]:
        return color_low
    elif ranges[0] <= number < ranges[1]:
        return color_mid
    elif ranges[1] <= number <= ranges[2]:
        return color_high
    else:
        return Color(0, 0, 0, 255)


# GENERAL


class GridTileStepsLouis(HomeAssistantEntityGridTile):
    icon = MaterialIcons.MDI_DIRECTIONS_WALK
    steps_per_day = 6000

    def process(self, state):
        value = float(state.get("sensor.steps_louis", 0))
        self.visible = value > 0
        self.label = f"{value:.0f}"
        self.label_color_bg = number_to_color(
            value / self.steps_per_day, brightness=128
        )
        self.progress = value / self.steps_per_day


class GridTileVPN(HomeAssistantEntityGridTile):
    icon = MaterialIcons.MDI_LOCK

    def process(self, state):
        value = state.get("sensor.privacy_ip_info", None)
        self.visible = value == settings.secrets.home_ip
        self.label = f"VPN DOWN ({value})"


class GridTileTransmission(HomeAssistantEntityGridTile):
    icon = MaterialIcons.MDI_VPN_LOCK

    def process(self, state):
        value = state.get("sensor.transmission_down_speed", 0)
        self.visible = value > 0
        self.label = f"{value:.0f}Mbps"


class GridTileDS920Plus(HomeAssistantEntityGridTile):
    icon = MaterialIcons.MDI_DNS

    def process(self, state):
        value = float(state.get("sensor.ds920plus_volume_used", 0))
        self.visible = value > 66.66
        self.label = f"{value:.0f}%"
        self.label_color_bg = number_to_color(value / 100, brightness=128)
        self.progress = value / 100


class GridTileSpeedtestDownload(HomeAssistantEntityGridTile):
    icon = MaterialIcons.MDI_DOWNLOAD

    def process(self, state):
        self.visible = True
        value = float(state.get("sensor.speedtest_download_average", 0))
        self.label = f"{value:.0f}Mbs"
        self.label_color_bg = number_to_color(value / 900, brightness=128)
        self.progress = value / 900


class GridTileSpeedtestUpload(HomeAssistantEntityGridTile):
    icon = MaterialIcons.MDI_UPLOAD

    def process(self, state):
        self.visible = True
        value = float(state.get("sensor.speedtest_upload_average", 0))
        self.label = f"{value:.0f}Mbs"
        self.label_color_bg = number_to_color(value / 900, brightness=128)
        self.progress = value / 900


class GridTileSpeedtestPing(HomeAssistantEntityGridTile):
    icon = MaterialIcons.MDI_WIFI

    def process(self, state):
        self.visible = True
        value = state.get("sensor.speedtest_ping_average", 0)
        self.label = f"{value:.0f}ms"
        self.label_color_bg = number_to_color(
            value, [10, 20, 30], brightness=128, invert=True
        )
        self.progress = value / 30


class GridTileBinCollection(HomeAssistantEntityGridTile):
    icon = MaterialIcons.MDI_DELETE

    def process(self, state):
        value = state.get("calendar.bin_collection")
        self.visible = value <= 1
        self.label = f"{value}"


class GridTileBackDoor(HomeAssistantEntityGridTile):
    icon = MaterialIcons.MDI_DOOR
    label = "Back"

    def process(self, state):
        self.visible = (
            state.get("binary_sensor.back_door_contact_sensor_contact") == True
        )


class GridTileFrontDoor(HomeAssistantEntityGridTile):
    icon = MaterialIcons.MDI_DOOR
    label = "Front"

    def process(self, state):
        self.visible = (
            state.get("binary_sensor.front_door_contact_sensor_contact") == True
        )


class GridTileHouseManual(HomeAssistantEntityGridTile):
    icon = MaterialIcons.MDI_TOGGLE_ON
    label = "MANUAL"

    def process(self, state):
        self.visible = state.get("input_boolean.house_manual") == True


class GridTileSwitchLoungeFans(HomeAssistantEntityGridTile):
    icon = MaterialIcons.MDI_AC_UNIT
    label = "ON"

    def process(self, state):
        self.visible = state.get("switch.lounge_fans") == True


# BATTERY


class GridTileBatteryLevel(HomeAssistantEntityGridTile):
    icon = MaterialIcons.MDI_BATTERY

    def process(self, state):
        value = float(state.get("sensor.delta_2_max_downstairs_battery_level", 0))
        self.visible = value > 0
        self.label = f"{value:.0f}%"
        self.label_color_bg = number_to_color(value / 100, brightness=128)
        self.progress = value / 100


class GridTileBatteryDischargeRemainingTime(HomeAssistantEntityGridTile):
    icon = MaterialIcons.MDI_HOURGLASS

    def process(self, state):
        value = float(
            state.get("sensor.delta_2_max_downstairs_discharge_remaining_time", 0)
        )
        hours, mins = value // 60, value % 60
        self.visible = value > 0
        self.label = f"{hours:.0f}h{mins:.0f}m"
        self.label_color_bg = Color(128, 0, 0, 255)


class GridTileBatteryChargeRemainingTime(HomeAssistantEntityGridTile):
    icon = MaterialIcons.MDI_HOURGLASS

    def process(self, state):
        value = float(
            state.get("sensor.delta_2_max_downstairs_charge_remaining_time", 0)
        )
        hours, mins = value // 60, value % 60
        self.visible = value > 0
        self.label = f"{hours:.0f}h{mins:.0f}m"
        self.label_color_bg = Color(0, 128, 0, 255)


class GridTileBatteryAcInPower(HomeAssistantEntityGridTile):
    icon = MaterialIcons.MDI_POWER

    def process(self, state):
        value = state.get("sensor.delta_2_max_downstairs_ac_in_power", 0)
        self.visible = value > 0
        self.label = f"{value:.0f}w"
        self.icon_color_fg = Color(0, 128, 0, 255)


class GridTileBatteryAcOutPower(HomeAssistantEntityGridTile):
    icon = MaterialIcons.MDI_POWER

    def process(self, state):
        value = state.get("sensor.delta_2_max_downstairs_ac_out_power", 0)
        self.visible = value > 0
        self.label = f"{value:.0f}w"
        self.icon_color_fg = Color(128, 0, 0, 255)


# POWER


class GridTileElectricityCurrentDemand(HomeAssistantEntityGridTile):
    icon = MaterialIcons.MDI_BOLT
    icon_color_fg = Color(192, 192, 192, 255)

    def process(self, state):
        value = float(state.get("sensor.octopus_energy_electricity_current_demand", 0))
        self.visible = value > 0
        self.label = f"{value:.0f}w"
        self.label_color_bg = number_to_color(
            value, [300, 600, 900], brightness=128, invert=True
        )


class GridTileElectricityCurrentRate(HomeAssistantEntityGridTile):
    icon = MaterialIcons.MDI_SYMBOL_AT

    def process(self, state: dict[str, Any]):
        value = float(state.get("sensor.octopus_energy_electricity_current_rate", 0))
        self.visible = value > 0
        self.label = f"£{value:.2f}"
        self.label_color_bg = number_to_color(
            value, [0.10, 0.30, 1.0], brightness=128, invert=True
        )


class GridTileElectricityHourlyRate(HomeAssistantEntityGridTile):
    icon = MaterialIcons.MDI_CURRENCY_DOLLAR

    def process(self, state):
        value = float(state.get("sensor.electricity_hourly_rate", 0))
        self.visible = value > 0
        self.label = f"£{value:.2f}"


class GridTileElectricityCurrentAccumulativeCost(HomeAssistantEntityGridTile):
    icon = MaterialIcons.MDI_SCHEDULE

    def process(self, state):
        value = float(
            state.get("sensor.octopus_energy_electricity_current_accumulative_cost", 0)
        )
        self.visible = value > 0
        self.label = f"£{value:.2f}"
