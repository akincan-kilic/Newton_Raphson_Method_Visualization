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
        self.__x_limits = None
        self.__root = 0
        # self.__function = '-2 * x**5 + 3 * x**3 -0.3 * x**2 + 1'
        self.__function = 'sin(x)'
        self.__page = None
        self.__app_icon = flet.Icon(name=flet.icons.CALCULATE, size=48)
        self.__app_title = flet.Text(
            value="Newton Raphson Method", style=flet.TextThemeStyle.DISPLAY_SMALL)
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
        self.__root_text = flet.Text(
            value="", style=flet.TextThemeStyle.DISPLAY_SMALL)
        self.__fig = px.line()
        self.__plot = PlotlyChart(self.__fig)

    def __calculate_xlims(self, x0):
        x0 = np.abs(x0 + 30)
        self.__x_limits = {'min': int(-2 * x0), 'max': int(2 * x0), 'amount': int(100 * x0)}

    def __tolerance_change(self, _):
        self.__tolerance_limits['value'] = int(self.__tolerance_slider.value)
        self.__page.update()

    def __func(self, x: int):
        return eval(self.__function, {'x': x, 'sin': np.sin, 'cos': np.cos, 'tan': np.tan, 'log': np.log, 'ln': np.log, 'e': np.e, 'pi': np.pi})

    def __calculate_animate(self, _):
        self.__calculate_button.icon = flet.icons.PAUSE_OUTLINED
        x_points = np.linspace(self.__x_limits['min'], self.__x_limits['max'], self.__x_limits['amount'])
        y_points = self.__func(x_points)
        i = 0
        x_intercept = self.__starting_value
        while np.abs(self.__func(x_intercept)) > self.__tolerance_limits['value']:
            slope = finite_difference(self.__func, x_intercept)
            x_old = x_intercept
            x_intercept = x_intercept - self.__func(x_intercept) / slope

            self.__root_text.value = f"Current X: {x_intercept:.2f} Iteration: {i}"
            self.__fig = px.line(x=x_points, y=y_points)

            x_line_points = np.linspace(self.__x_limits['min'], self.__x_limits['max'], self.__x_limits['amount'])
            y_line_points = slope * (x_line_points - x_old) + self.__func(x_old)

            self.__fig.add_scatter(x=x_line_points, y=y_line_points, name='line', showlegend=False, line_color='red', line_width=1)
            self.__fig.add_vline(x_old, line_color='blue', line_width=1)

            self.__fig.add_scatter(
                x=[x_intercept], y=[self.__func(x_intercept)],
                mode='markers', marker_color='red', marker_size=10, marker_symbol='circle',
                name='root', showlegend=False
            )

            self.__fig.add_scatter(
                x=[x_intercept], y=[0],
                mode='markers', marker_color='red', marker_size=10, marker_symbol='circle',
                name='root', showlegend=False
            )

            self.__fig.add_vline(0, line_color='green', line_width=1)
            self.__fig.add_hline(0, line_color='green', line_width=1)

            min_x = min(x_old, x_intercept)
            max_x = max(x_old, x_intercept)
            self.__fig.update_layout(
                xaxis_range=[min_x - 1, max_x + 1],
                yaxis_range=[-2, 2]
            )
            self.__plot.figure = self.__fig
            self.__plot.update()
            self.__page.update()
            i += 1
            time.sleep(0.7)


        # TODO: Implement alert box to show root after calculation.
        # https://flet.dev/docs/controls/alertdialog
        # https://flet.dev/docs/controls/snackbar
        # Found root, it is x
        self.__calculate_button.icon = flet.icons.REFRESH
        self.__page.update()

    def __update_function(self, _):
        self.__function = self.__function_input.value
        self.__page.update()

    def __update_starting_value(self, _):
        self.__starting_value = float(self.__starting_value_input.value)
        self.__calculate_xlims(self.__starting_value)
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

    def __add_apptitle(self):
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

    def __add_controls(self):
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

    def __add_root_text(self):
        self.__page.add(
            flet.Row(
                wrap=False,
                alignment=flet.MainAxisAlignment.CENTER,
                controls=[
                    self.__root_text
                ]
            )
        )

    def __call__(self, flet_page: flet.Page):
        self.__page = flet_page
        self.__init_window()
        self.__add_apptitle()
        self.__add_controls()
        self.__add_root_text()
        self.__page.add(self.__plot)
        self.__page.update()


if __name__ == '__main__':
    flet.app(target=NewtonRaphsonGUI())
