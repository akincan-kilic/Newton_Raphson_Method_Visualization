import time
import numpy as np
import flet
import plotly.express as px
import logging
from flet.plotly_chart import PlotlyChart

# Initialize logger
# logging.basicConfig(filename='nrm.log', encoding='utf-8', level=logging.DEBUG)
# logger = logging.getLogger('nrm')
# logger.info('Starting Newton Raphson Method')
ITERATION_SPEEDS = {'Turtle': 1, 'Slow': 0.5, 'Medium': 0.25, 'Fast': 0.1, 'Sonic!': 0.01}

def finite_difference(func, x, h=1e-5):
    return (func(x + h) - func(x - h)) / (2 * h)

class NewtonRaphsonGUI:
    def __init__(self):
        # Page Related
        self.__page = None
        self.__app_icon = flet.Icon(name=flet.icons.CALCULATE, size=48)
        self.__app_title = flet.Text(value="Newton Raphson Method", style=flet.TextThemeStyle.DISPLAY_SMALL)
        self.__calculate_button = flet.IconButton(icon=flet.icons.NOT_STARTED, tooltip="Start", icon_size=48, on_click=self.__calculate_animate)
        self.__root_text = flet.Text(value="", style=flet.TextThemeStyle.BODY_LARGE, selectable=False, size=20, text_align=flet.TextAlign.CENTER, weight=flet.FontWeight.BOLD)
        self.__fig = px.line()
        self.__plot = PlotlyChart(self.__fig)
        self.__exit_button = flet.IconButton(icon=flet.icons.CANCEL_OUTLINED, tooltip="Exit", icon_size=48, on_click=self.__quit)

        # Logic Related
        self.__tolerance = 1e-6
        self.__starting_value = 10
        self.__x_limits = None
        self.__calculate_xlims(self.__starting_value)
        self.__root = 0

        # Input Related
        self.__function = 'x**3 - x**2 + 4'
        self.__function_input = flet.TextField(label="f(x)", value=self.__function, width=310, on_blur=self.__update_function)
        self.__starting_value_input = flet.TextField(label="X (Starting Value)", value=str(self.__starting_value), width=150, on_blur=self.__update_starting_value)
        self.__tolerance_slider = flet.Slider(min=1, max=16, value=6, divisions=15, label="{value} Tolerance", on_change=self.__tolerance_change, expand=True, active_color=flet.colors.PURPLE_ACCENT_400, thumb_color=flet.colors.AMBER)
        self.__tolerance_text = flet.Text(value=f"{self.__tolerance:.2e}", style=flet.TextThemeStyle.BODY_SMALL)
        self.__iteration_speed_dropdown = flet.Dropdown(label="Iteration Speed", width=150, options=[flet.dropdown.Option('Turtle'), flet.dropdown.Option('Slow'), flet.dropdown.Option('Medium'), flet.dropdown.Option('Fast'), flet.dropdown.Option('Sonic!')], on_change=self.__update_iteration_speed, value='Medium')
        self.__iteration_speed = ITERATION_SPEEDS['Medium']

        # Alerts
        self.__root_dlg = flet.AlertDialog(modal=True,
                                           title=flet.Text(value='Found a root!', style=flet.TextThemeStyle.TITLE_LARGE, selectable=False, weight=flet.FontWeight.BOLD, size=20),
                                           content=flet.Text(value=f"Root: {self.__root}", style=flet.TextThemeStyle.BODY_LARGE),
                                           actions=[flet.TextButton("Yes", on_click=self.__root_dlg_yes),
                                                    flet.TextButton("No", on_click=self.__quit),
                                                    ],
                                           on_dismiss=lambda e: print("Root alert dismissed!"),)

    def __quit(self, _):
        self.__page.window_destroy()

    def __update_iteration_speed(self, _):
        self.__iteration_speed = ITERATION_SPEEDS[self.__iteration_speed_dropdown.value]
        print(f"New Iteration Speed: {self.__iteration_speed}")

    def __calculate_xlims(self, x0):
        x0 = np.abs(x0 + 30)
        self.__x_limits = {'min': int(-2 * x0), 'max': int(2 * x0), 'amount': int(100 * x0)}

    def __tolerance_change(self, _):
        self.__tolerance = 10 ** -self.__tolerance_slider.value
        self.__tolerance_text.value = f"{self.__tolerance:.2e}"
        print(f"New Tolerance: {self.__tolerance:.2e}")
        self.__page.update()

    def __func(self, x: int):
        return eval(self.__function, {'x': x, 'sin': np.sin, 'cos': np.cos, 'tan': np.tan, 'log': np.log, 'ln': np.log, 'e': np.e, 'pi': np.pi})

    def __calculate_animate(self, _):
        self.__calculate_button.icon = flet.icons.PAUSE_CIRCLE
        x_points = np.linspace(self.__x_limits['min'], self.__x_limits['max'], self.__x_limits['amount'])
        y_points = self.__func(x_points)
        x_intercept = self.__starting_value
        i = 0
        while np.abs(self.__func(x_intercept)) > self.__tolerance:
            slope = finite_difference(self.__func, x_intercept)
            x_old = x_intercept
            x_intercept = x_intercept - self.__func(x_intercept) / slope

            self.__root_text.value = '   ' + f"X: {x_intercept:.2f} | Iteration No: {i}"
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

            self.__fig.add_vline(0, line_color='black', line_width=1)
            self.__fig.add_hline(0, line_color='black', line_width=1)

            min_x = min(x_old, x_intercept)
            max_x = max(x_old, x_intercept)
            # self.__fig.update_layout(
                # xaxis_range=[min_x - 1, max_x + 1],
                # yaxis_range=[-100, 100]
            # )
            self.__plot.figure = self.__fig
            self.__plot.update()
            self.__page.update()
            i += 1
            print(f"Sleeping for {self.__iteration_speed} seconds.")
            time.sleep(self.__iteration_speed)

        self.__root = x_intercept
        self.__alert_root_found()
        self.__calculate_button.icon = flet.icons.REFRESH
        self.__page.update()

    def __alert_root_found(self):
        self.__page.dialog = self.__root_dlg
        self.__root_dlg.content = flet.Text(value=f"Found root at x={self.__root:.2f}\nDo you want to enter another value to find another root?", style=flet.TextThemeStyle.BODY_LARGE)
        self.__root_dlg.open = True
        self.__page.update()

    def __root_dlg_yes(self, _):
        self.__root_dlg.open = False
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
                    self.__exit_button
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
                    self.__tolerance_slider,
                    self.__tolerance_text,
                    self.__calculate_button
                ],
                spacing=10
            ),
            flet.Row(
                wrap=False,
                alignment=flet.MainAxisAlignment.START,
                controls=[
                    self.__starting_value_input,
                    self.__iteration_speed_dropdown,
                    self.__root_text,
                ],
                spacing=10
            )
        )

    def __call__(self, flet_page: flet.Page):
        self.__page = flet_page
        self.__init_window()
        self.__add_apptitle()
        self.__add_controls()
        self.__page.add(self.__plot)
        self.__page.update()


if __name__ == '__main__':
    flet.app(target=NewtonRaphsonGUI())
