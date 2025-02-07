UIElement:
widget: WidgetClass

    class WidgetClass:

        expressions = {
            "visible": "ctx.visible == True",
        }

        def **init**(self):
            pass

        def surface(self):
            # renders pygame surface
