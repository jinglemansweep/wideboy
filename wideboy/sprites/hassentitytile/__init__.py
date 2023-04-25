import logging
from pygame import Clock, Color, Event, Rect, Surface, SRCALPHA
from typing import Optional
from wideboy.constants import EVENT_EPOCH_SECOND

# from wideboy.mqtt.homeassistant import HASS
from wideboy.scenes.base import BaseScene
from wideboy.sprites.base import BaseSprite
from wideboy.sprites.image_helpers import render_text, render_material_icon

logger = logging.getLogger("sprite.hassentitytile")


class HassEntityTileSprite(BaseSprite):
    def __init__(
        self,
        scene: BaseScene,
        rect: Rect,
        icon: str,
        template: Optional[str] = None,
        entity_id: Optional[str] = None,
        state_callback: callable = lambda state: state.state == "on",
        color_icon: Color = Color(255, 255, 255, 255),
        color_template: Color = Color(255, 255, 255, 255),
        color_bg: Color = Color(0, 0, 0, 0),
        update_interval: int = 10,
    ) -> None:
        super().__init__(scene, rect)
        self.icon = icon
        self.template = template
        self.entity_id = entity_id
        self.state_callback = state_callback
        self.color_icon = color_icon
        self.color_template = color_template
        self.color_bg = color_bg
        self.update_interval = update_interval
        self.icon_size = int(self.rect.width * 0.6)
        self.render()

    def update(
        self,
        frame: str,
        clock: Clock,
        delta: float,
        events: list[Event],
    ) -> None:
        super().update(frame, clock, delta, events)
        for event in events:
            if (
                event.type == EVENT_EPOCH_SECOND
                and event.unit % self.update_interval == 0
            ):
                self.render()

    def render(self) -> None:
        # Entity
        if self.entity_id:
            entity = self.scene.engine.hass.client.get_entity(entity_id=self.entity_id)
            state = entity.get_state()
            active = self.state_callback(state) if self.state_callback else True
        else:
            active = True
        # Template
        template_text = None
        if self.template:
            template_text = self.scene.engine.hass.client.get_rendered_template(
                self.template
            )
        # Render
        self.image = Surface((self.rect.width, self.rect.height), SRCALPHA)
        self.image.fill(self.color_bg)
        icon_y = 0
        if active:
            icon_text = render_material_icon(
                self.icon, self.icon_size, self.color_icon, Color(0, 0, 0, 255)
            )
            if template_text:
                template_text = render_text(
                    template_text,
                    "fonts/bitstream-vera.ttf",
                    8,
                    color_fg=self.color_template,
                    color_outline=Color(0, 0, 0, 255),
                )
                text_pos = (
                    (self.rect.width / 2) - (icon_text.get_width() / 2),
                    self.rect.height - template_text.get_height(),
                )
                self.image.blit(template_text, text_pos)
            else:
                icon_y += 4
            icon_pos = ((self.rect.width / 2) - (icon_text.get_width() / 2), icon_y)
            self.image.blit(icon_text, icon_pos)
        self.dirty = 1
