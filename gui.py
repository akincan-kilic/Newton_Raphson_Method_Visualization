import time
import numpy as np
from bisection import bisection
import flet
import plotly.express as px
from flet.plotly_chart import PlotlyChart


class NewtonRaphsonGUI:
    def __init__(self):
        self.__starting_value = 0
        self.__tolerance = 1e-5
        self.__root = 0
        self.__function = 'x**2 - 2'
        self.__page = None
        self.__app_icon = flet.Icon(name=flet.icons.CALCULATE, size=48)
        self.__app_title = flet.Text(value="Newton Raphson Method", style=flet.TextThemeStyle.DISPLAY_SMALL)
        self.__theme_toggle_button = flet.IconButton(
            icon=flet.icons.DARK_MODE_OUTLINED,
            tooltip="Toggle Dark/Light Theme",
            on_click=self.__toggle_theme
        )
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
        self.__tolerance_input = flet.TextField(
            label="Tolerance",
            value=str(self.__tolerance),
            width=100,
            on_blur=self.__update_tolerance
        )
        self.__calculate_button = flet.IconButton(
            icon=flet.icons.START_OUTLINED,
            tooltip="Calculate",
            icon_size=48,
            on_click=self.__calculate_animate
        )
        self.__root_text = flet.Text(value="", style=flet.TextThemeStyle.DISPLAY_SMALL)
        self.__fig = px.line()
        self.__plot = PlotlyChart(self.__fig)

    def __func(self, x):
        return eval(self.__function, {'x': x})

    def __calculate(self, _):
        self.__root = bisection(self.__func, self.__starting_value, self.__b, self.__tolerance)
        self.__root_text.value = f"Root: {self.__root:.5f}"
        d = self.__b - self.__starting_value
        x_points = np.linspace(self.__starting_value - d, self.__b + d, 100)
        y_points = self.__func(x_points)
        self.__fig = px.line(x=x_points, y=y_points)
        self.__fig.add_scatter(
            x=[self.__root], y=[self.__func(self.__root)],
            mode='markers', marker_color='red', marker_size=10, marker_symbol='x',
            name='root', showlegend=False
        )
        self.__plot.figure = self.__fig
        self.__plot.update()
        self.__page.update()

    def __calculate_animate(self, _):
        self.__calculate_button.icon = flet.icons.PAUSE_OUTLINED
        d = self.__b - self.__starting_value
        x_points = np.linspace(self.__starting_value - d, self.__b + d, 100)
        y_points = self.__func(x_points)
        fa = self.__func(self.__starting_value)
        fb = self.__func(self.__b)
        m = (self.__starting_value + self.__b) / 2
        fm = self.__func(m)
        i = 0
        while abs(fm) > self.__tolerance:
            self.__root_text.value = f"a: {self.__starting_value:.2f} b: {self.__b:.2f} m: {m:.5f} i: {i}"
            self.__fig = px.line(x=x_points, y=y_points)
            self.__fig.add_scatter(
                x=[m], y=[self.__func(m)],
                mode='markers', marker_color='red', marker_size=10, marker_symbol='x',
                name='root', showlegend=False
            )
            self.__plot.figure = self.__fig
            self.__plot.update()
            self.__page.update()
            if np.sign(fa) == np.sign(fm):
                self.__starting_value = m
                fa = fm
            elif np.sign(fb) == np.sign(fm):
                self.__b = m
                fb = fm
            m = (self.__starting_value + self.__b) / 2
            fm = self.__func(m)
            i += 1
            time.sleep(0.5)
        self.__root = m
        self.__calculate_button.icon = flet.icons.REFRESH
        self.__page.update()

    def __update_function(self, _):
        self.__function = self.__function_input.value
        self.__page.update()

    def __update_starting_value(self, _):
        self.__starting_value = float(self.__starting_value_input.value)
        self.__page.update()

    def __update_tolerance(self, _):
        self.__tolerance = float(self.__tolerance_input.value)
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
                    self.__theme_toggle_button
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
                    self.__tolerance_input,
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
