from pygame import Color
from wideboy.sprites.image_helpers import MaterialIcons, number_to_color
from wideboy.sprites.homeassistant.entity_grid import HomeAssistantEntityGridTile
from wideboy.sprites.homeassistant.entity_row import HomeAssistantEntityTile
from wideboy.config import settings

from typing import Any, Optional, List


# COLORS

COLORS_DIM_BRIGHTNESS = 128
COLORS_DIM_ALPHA = 255
COLORS_TRAFFIC_LIGHT_DIM = [
    Color(COLORS_DIM_BRIGHTNESS, 0, 0, COLORS_DIM_ALPHA),
    Color(COLORS_DIM_BRIGHTNESS, COLORS_DIM_BRIGHTNESS, 0, COLORS_DIM_ALPHA),
    Color(0, COLORS_DIM_BRIGHTNESS, 0, COLORS_DIM_ALPHA),
]

# GENERAL


class GridTileStepsLouis(HomeAssistantEntityGridTile):
    icon = MaterialIcons.MDI_DIRECTIONS_WALK
    steps_per_day = 6000

    def process(self, state):
        value = float(state.get("sensor.steps_louis", 0))
        self.visible = value > 0
        self.label = f"{value:.0f}"
        self.label_color_bg = number_to_color(
            value / self.steps_per_day, colors=COLORS_TRAFFIC_LIGHT_DIM
        )
        self.progress = value / self.steps_per_day


# NETWORK


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
        self.label_color_bg = number_to_color(
            value / 100, colors=COLORS_TRAFFIC_LIGHT_DIM
        )
        self.progress = value / 100


class GridTileSpeedtestDownload(HomeAssistantEntityGridTile):
    icon = MaterialIcons.MDI_DOWNLOAD

    def process(self, state):
        self.visible = True
        try:
            value = float(state.get("sensor.speedtest_download_average", 0))
            self.label = f"{value:.0f}M"
            self.label_color_bg = number_to_color(
                value / 900, colors=COLORS_TRAFFIC_LIGHT_DIM
            )
            self.progress = value / 900
        except Exception as ex:
            self.visible = False

class GridTileSpeedtestUpload(HomeAssistantEntityGridTile):
    icon = MaterialIcons.MDI_UPLOAD

    def process(self, state):
        self.visible = True
        try:
            value = float(state.get("sensor.speedtest_upload_average", 0))
            self.label = f"{value:.0f}M"
            self.label_color_bg = number_to_color(
                value / 900, colors=COLORS_TRAFFIC_LIGHT_DIM
            ) 
            self.progress = value / 900
        except Exception as ex:
            self.visible = False

class GridTileSpeedtestPing(HomeAssistantEntityGridTile):
    icon = MaterialIcons.MDI_WIFI

    def process(self, state):
        self.visible = True
        try:
            value = state.get("sensor.speedtest_ping_average", 0)
            self.label = f"{value:.0f}ms"
            self.label_color_bg = number_to_color(
                value, [10, 20, 30], colors=COLORS_TRAFFIC_LIGHT_DIM, invert=True
            )
            self.progress = value / 30
        except Exception as ex:
            self.visible = False

# SENSORS


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


class GridTileTemperatureOutside(HomeAssistantEntityGridTile):
    icon = MaterialIcons.MDI_HOME

    def process(self, state):
        self.visible = True
        value = float(state.get("sensor.blink_back_temperature", 0))
        print(value)
        self.label = f"{value:.0f}°"


class GridTileTemperatureLounge(HomeAssistantEntityGridTile):
    icon = MaterialIcons.MDI_SOFA

    def process(self, state):
        self.visible = True
        value = float(state.get("sensor.hue_motion_sensor_1_temperature", 0))
        self.label = f"{value:.0f}°"


class GridTileTemperatureKitchen(HomeAssistantEntityGridTile):
    icon = MaterialIcons.MDI_KITCHEN

    def process(self, state):
        self.visible = True
        value = float(state.get("sensor.kitchen_temperature_sensor_temperature", 0))
        self.label = f"{value:.0f}°"


class GridTileTemperatureBedroom(HomeAssistantEntityGridTile):
    icon = MaterialIcons.MDI_BED

    def process(self, state):
        self.visible = True
        value = float(state.get("sensor.bedroom_temperature_sensor_temperature", 0))
        self.label = f"{value:.0f}°"


# SWITCHES


class GridTileHouseManual(HomeAssistantEntityGridTile):
    icon = "M"
    label = "ON"

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
        self.label_color_bg = number_to_color(
            value / 100, colors=COLORS_TRAFFIC_LIGHT_DIM
        )
        self.progress = value / 100


class GridTileBatteryDischargeRemainingTime(HomeAssistantEntityGridTile):
    icon = MaterialIcons.MDI_HOURGLASS
    icon_color_fg = Color(255, 0, 0, 255)

    def process(self, state):
        value = float(
            state.get("sensor.delta_2_max_downstairs_discharge_remaining_time", 0)
        )
        hours, mins = value // 60, value % 60
        self.visible = value > 0
        self.label = f"{hours:.0f}h{mins:.0f}m"


class GridTileBatteryChargeRemainingTime(HomeAssistantEntityGridTile):
    icon = MaterialIcons.MDI_HOURGLASS
    icon_color_fg = Color(0, 255, 0, 255)

    def process(self, state):
        value = float(
            state.get("sensor.delta_2_max_downstairs_charge_remaining_time", 0)
        )
        hours, mins = value // 60, value % 60
        self.visible = value > 0
        self.label = f"{hours:.0f}h{mins:.0f}m"


class GridTileBatteryAcInPower(HomeAssistantEntityGridTile):
    icon = MaterialIcons.MDI_POWER
    icon_color_fg = Color(0, 255, 0, 255)

    def process(self, state):
        value = float(state.get("sensor.delta_2_max_downstairs_ac_in_power", 0))
        self.visible = value > 0
        self.label = f"{value:.0f}w"


class GridTileBatteryAcOutPower(HomeAssistantEntityGridTile):
    icon = MaterialIcons.MDI_POWER
    icon_color_fg = Color(255, 0, 0, 255)

    def process(self, state):
        value = float(state.get("sensor.delta_2_max_downstairs_ac_out_power", 0))
        self.visible = value > 0
        self.label = f"{value:.0f}w"


# ELECTRICITY


class GridTileElectricityCurrentDemand(HomeAssistantEntityGridTile):
    icon = MaterialIcons.MDI_BOLT
    icon_color_fg = Color(192, 192, 192, 255)

    def process(self, state):
        value = float(state.get("sensor.octopus_energy_electricity_current_demand", 0))
        self.visible = value > 0
        self.label = f"{value:.0f}w"
        self.label_color_bg = number_to_color(
            value, [300, 600, 900], colors=COLORS_TRAFFIC_LIGHT_DIM, invert=True
        )


class GridTileElectricityCurrentRate(HomeAssistantEntityGridTile):
    icon = MaterialIcons.MDI_SYMBOL_AT

    def process(self, state: dict[str, Any]):
        value = float(state.get("sensor.octopus_energy_electricity_current_rate", 0))
        self.visible = value > 0
        self.label = f"£{value:.2f}"
        self.label_color_bg = number_to_color(
            value,
            ranges=[0.10, 0.30, 1.0],
            colors=COLORS_TRAFFIC_LIGHT_DIM,
            invert=True,
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
