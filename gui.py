import time
import numpy as np
import flet
import plotly.express as px
from flet.plotly_chart import PlotlyChart


def finite_difference(func, x, h=1e-5):
    return (func(x + h) - func(x - h)) / (2 * h)


class NewtonRaphsonGUI:
    def __init__(self):
        self.__starting_value = 0
        self.__tolerance = 1e-5
        self.__root = 0
        self.__function = 'x**2 - 2'
        self.__page = None
        self.__app_icon = flet.Icon(name=flet.icons.CALCULATE, size=48)
        self.__app_title = flet.Text(value="Newton Raphson Method", style=flet.TextThemeStyle.DISPLAY_SMALL)
        self.__function_input = flet.TextField(
            label="f(x)",
            value=self.__function,
            width=300,
            on_blur=self.__update_function
        )
        self.__starting_value_input = flet.TextField(
            label="x0: Starting Value",
            value=str(self.__starting_value),
            width=100,
            on_blur=self.__update_starting_value
        )
        self.__tolerance_limits = {"high": 10 ** -1, "low": 10 ** -9, "value": 10 ** -5}
        self.__tolerance_slider = flet.Slider(min=self.__tolerance_limits["low"],
                                              max=self.__tolerance_limits["high"],
                                              value=self.__tolerance_limits["value"],
                                              divisions=10,
                                              label="{value} Tolerance",
                                              on_change=self.__tolerance_change,
                                              expand=True)

        self.__calculate_button = flet.IconButton(
            icon=flet.icons.START_OUTLINED,
            tooltip="Calculate",
            icon_size=48,
            on_click=self.__calculate_animate
        )
        self.__root_text = flet.Text(value="", style=flet.TextThemeStyle.DISPLAY_SMALL)
        self.__fig = px.line()
        self.__plot = PlotlyChart(self.__fig)

    def __tolerance_change(self, _):
        self.__tolerance_limits['value'] = int(self.__tolerance_slider.value)
        self.__page.update()

    def __func(self, x):
        return eval(self.__function, {'x': x})

    def __calculate_animate(self, _):
        self.__calculate_button.icon = flet.icons.PAUSE_OUTLINED

        x_points = np.linspace(self.__starting_value - 100, self.__starting_value + 100, 100)
        y_points = self.__func(x_points)
        i = 0

        x = self.__starting_value
        while np.abs(self.__func(x)) > self.__tolerance_limits['value']:
            slope = finite_difference(self.__func, x)
            old_x = x
            x = x - self.__func(x) / slope

            self.__root_text.value = f"Current X: {x:.2f} Iteration: {i}"
            self.__fig = px.line(x=x_points, y=y_points)
            # TODO: Add line to show tangent

            x_line_points = np.linspace(self.__starting_value - 100, self.__starting_value + 100, 100)
            y_line_points = np.copy(x_line_points)

            for i in range(len(y_line_points)):
                b = self.__func(old_x) - slope * old_x
                y_line_points[i] = slope * x_line_points[i] + b

            for i in range(len(y_line_points)):
                self.__fig.add_scatter(
                    x=[x_line_points[i]], y=[y_line_points[i]],
                    mode='markers', marker_color='blue', marker_size=1, marker_symbol='x',
                    name='31', showlegend=False
                )




            self.__fig.add_scatter(
                x=[x], y=[self.__func(x)],
                mode='markers', marker_color='red', marker_size=10, marker_symbol='x',
                name='root', showlegend=False
            )

            self.__plot.figure = self.__fig
            self.__plot.update()
            self.__page.update()

            i += 1
            time.sleep(0.5)
        self.__root = x
        # TODO: Implement alert box to show root
        self.__calculate_button.icon = flet.icons.REFRESH
        self.__page.update()

    def __update_function(self, _):
        self.__function = self.__function_input.value
        self.__page.update()

    def __update_starting_value(self, _):
        self.__starting_value = float(self.__starting_value_input.value)
        self.__page.update()

    def __update_tolerance(self, _):
        self.__tolerance = float(self.__tolerance_slider.value)
        self.__page.update()

    def __init_window(self):
        self.__page.title = "Newton Raphson Method"
        self.__page.window_min_width = 800
        self.__page.window_min_height = 800
        self.__page.window_width = 800
        self.__page.window_height = 800
        self.__page.window_frameless = False
        self.__page.window_always_on_top = True
        self.__page.window_focused = True
        self.__page.window_center()
        self.__page.theme_mode = flet.ThemeMode.LIGHT

    def __toggle_theme(self, _):
        if self.__page.theme_mode == flet.ThemeMode.LIGHT:
            self.__page.theme_mode = flet.ThemeMode.DARK
        else:
            self.__page.theme_mode = flet.ThemeMode.LIGHT
        self.__page.update()

    def __call__(self, flet_page: flet.Page):
        self.__page = flet_page
        self.__init_window()
        self.__page.add(
            flet.Row(
                wrap=False,
                alignment=flet.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    flet.Row(
                        wrap=False,
                        controls=[
                            self.__app_icon,
                            self.__app_title
                        ]
                    ),
                ]
            )
        )
        self.__page.add(
            flet.Row(
                wrap=False,
                alignment=flet.MainAxisAlignment.CENTER,
                controls=[
                    self.__function_input,
                    self.__starting_value_input,
                    self.__tolerance_slider,
                    self.__calculate_button
                ]
            )
        )
        self.__page.add(
            flet.Row(
                wrap=False,
                alignment=flet.MainAxisAlignment.CENTER,
                controls=[
                    self.__root_text
                ]
            )
        )
        self.__page.add(self.__plot)
        self.__page.update()


if __name__ == '__main__':
    flet.app(target=NewtonRaphsonGUI())
