import time
import numpy as np
import flet
import plotly.express as px
import plotly.graph_objects
from threading import Thread
from flet.plotly_chart import PlotlyChart
import random

ITERATION_SPEEDS = {'Turtle': 5, 'Slow': 2, 'Medium': 1, 'Fast': 0.5, 'Sonic!': 0.01}


def finite_difference(func, x, h=1e-5):
    return (func(x + h) - func(x - h)) / (2 * h)


class NewtonRaphsonGUI:
    # Static content
    __app_icon: flet.Icon
    __app_title: flet.Text
    __exit_button: flet.IconButton

    # Dynamic content
    __calculate_button: flet.IconButton
    __root_text: flet.Text
    __fig: plotly.graph_objects.Figure
    __plot: PlotlyChart

    # Dynamic, input related
    __function_string_value: str
    __function_input: flet.TextField
    __starting_value_input: flet.TextField
    __tolerance_slider: flet.Slider
    __tolerance_text: flet.Text
    __iteration_speed_dropdown: flet.Dropdown
    __iteration_speed: float

    # Alerts
    __root_dlg: flet.AlertDialog

    # Logic related
    __thread: Thread
    __tolerance: float
    __starting_value: float
    __x_limits: dict
    __function_string_value: str
    __known_root: float
    __running: bool
    __page: flet.Page

    def __init__(self, flet_page: flet.Page):
        # Logic Related
        self.__tolerance = 1e-6
        self.__starting_value = 10
        self.__function_string_value = "3 * x ** 2"
        self.__x_limits = {'min': -2, 'max': 2, 'amount': 1000}
        self.__zoom_limits = {'x_min': -1, 'x_max': 1, 'y_min': -1, 'y_max': 1}
        self.__running = False
        # ----------------------------------------------------
        self.__page = flet_page
        self.__init_input_related_content()
        self.__init_dynamic_content()
        self.__init_static_content()
        self.__show_page()

    def __brute_calculate(self):
        current_x_value = self.__starting_value
        while True:
            # Calculate derivative at current value of x and interpret as slope.
            slope = finite_difference(self.__function, current_x_value)

            # Store the previous x value for visualization purposes.
            previous_x_value = current_x_value
            # Update the current x value. Essential part of Newton Raphson algorithm.
            current_x_value = current_x_value - self.__function(current_x_value) / slope
            # Recalculate function value for updated x value.
            current_function_value = self.__function(current_x_value)

            root_found = abs(current_function_value) < 0.01

            if root_found:
                return current_x_value

    def __calculate_interval(self, current_x, previous_x):
        self.__x_limits['min'] = -2 * current_x
        self.__x_limits['max'] = 2 * current_x

    def __function(self, x):
        return eval(self.__function_string_value,
                    {'x': x, 'sin': np.sin, 'cos': np.cos, 'tan': np.tan, 'log': np.log, 'ln': np.log, 'e': np.e,
                     'pi': np.pi})

    def __on_calculate_button_clicked(self, _):
        if not self.__running:
            self.__known_root = self.__brute_calculate()
            self.__set_state_to_running()
            self.__thread = NewtonRaphsonThread(self, self.__iteration_speed, self.__starting_value, self.__function, self.__tolerance)
            self.__thread.start()
        else:
            self.__thread.kill()
            self.__set_state_to_ready()

    def on_notify(self, slope, previous_x_value, current_x_value, current_function_value, iteration_counter, root_found):
        self.__on_figure_changed(slope, previous_x_value, current_x_value, current_function_value)
        self.__on_root_text_value_changed(current_x_value, iteration_counter)
        self.__page.update()

        if root_found:
            self.__on_root_found(current_x_value)

    def __calculate_zoom_limits(self, current_x_value, previous_x_value):
        middle_x = (current_x_value + previous_x_value) / 2
        middle_y = self.__function(middle_x)

        self.__zoom_limits['x_min'] = current_x_value * -1.10
        self.__zoom_limits['x_max'] = previous_x_value * 1.10
        self.__zoom_limits['y_min'] = -1 * middle_y
        self.__zoom_limits['y_max'] = 3 * middle_y

    def __on_figure_changed(self, slope, previous_x_value, current_x_value, current_function_value):
        # self.__calculate_interval(current_x_value, previous_x_value)
        x_points = np.linspace(self.__x_limits['min'], self.__x_limits['max'], self.__x_limits['amount'])
        y_points = self.__function(x_points)
        fig = px.line(x=x_points, y=y_points)

        x_line_points = np.array([current_x_value, previous_x_value])
        y_line_points = slope * (x_line_points - previous_x_value) + self.__function(previous_x_value) # y = mx + b

        fig.add_scatter(x=x_line_points, y=y_line_points, name='line', showlegend=False, line_color='red', line_width=1)
        fig.add_vline(previous_x_value, line_color='blue', line_width=1)

        fig.add_scatter(
            x=[current_x_value], y=[0],
            mode='markers', marker_color='red', marker_size=10, marker_symbol='circle',
            name='root', showlegend=False
        )

        fig.add_vline(0, line_color='black', line_width=1)
        fig.add_hline(0, line_color='black', line_width=1)

        # fig.update_xaxes(range=[self.__x_limits['min'], self.__x_limits['max']], constrain='domain')
        # fig.update_yaxes(range=[self.__function(self.__x_limits['min']), self.__function(self.__x_limits['max'])], constrain='domain')
        self.__calculate_zoom_limits(current_x_value, previous_x_value)
        fig.update_xaxes(range=[self.__zoom_limits['x_min'], self.__zoom_limits['x_max']], constrain='domain')
        fig.update_yaxes(range=[self.__zoom_limits['y_min'], self.__zoom_limits['y_max']], constrain='domain')

        self.__plot.figure = fig
        self.__plot.update()
        self.__page.update()

    def __on_root_found(self, root):
        self.__page.dialog.content = flet.Text(
            value=f"Found root at x={root:.2f}\nDo you want to enter another value to find another root?",
            style=flet.TextThemeStyle.BODY_LARGE)

        self.__page.dialog.open = True

        self.__page.update()

    def __set_state_to_running(self):
        self.__calculate_button.icon = flet.icons.PAUSE_CIRCLE
        self.__calculate_button.tooltip = "Stop"
        self.__function_input.disabled = True
        self.__starting_value_input.disabled = True
        self.__tolerance_slider.disabled = True
        self.__iteration_speed_dropdown.disabled = True
        self.__running = True
        self.__page.update()

    def __set_state_to_ready(self):
        self.__running = False
        self.__page.dialog.open = False
        self.__calculate_button.icon = flet.icons.NOT_STARTED
        self.__calculate_button.tooltip = "Start"
        self.__function_input.disabled = False
        self.__starting_value_input.disabled = False
        self.__tolerance_slider.disabled = False
        self.__iteration_speed_dropdown.disabled = False
        self.__page.update()

    def __on_root_text_value_changed(self, current_x_value, iteration):
        self.__root_text.value = '   ' + f"X: {current_x_value:.2f} | Iteration No: {iteration}"

    def __on_exit_button_clicked(self, _):
        self.__page.window_destroy()

    def __on_root_found_dialog_yes_button_clicked(self, _):
        self.__set_state_to_ready()

    def __on_function_string_value_changed(self, _):
        self.__function_string_value = self.__function_input.value
        self.__page.update()

    def __on_starting_value_changed(self, _):
        self.__starting_value = float(self.__starting_value_input.value)
        self.__page.update()

    def __on_tolerance_slider_change(self, _):
        self.__tolerance = 10 ** -self.__tolerance_slider.value
        self.__tolerance_text.value = f"{self.__tolerance:.2e}"
        self.__page.update()

    def __on_iteration_speed_dropdown_change(self, _):
        self.__iteration_speed = ITERATION_SPEEDS[self.__iteration_speed_dropdown.value]

    """
        Init helpers
        ----------------------------------------------------
    """

    def __init_window(self):
        self.__page.title = "Newton Raphson Method"
        self.__page.window_min_width = 800
        self.__page.window_min_height = 800
        self.__page.window_width = 800
        self.__page.window_height = 800
        self.__page.window_frameless = False
        self.__page.window_always_on_top = False
        self.__page.window_focused = True
        self.__page.window_center()
        self.__page.theme_mode = flet.ThemeMode.LIGHT

    def __add_app_title_and_dialog(self):
        self.__page.dialog = flet.AlertDialog(modal=True,
                                              title=flet.Text(value='Found a root!',
                                                              style=flet.TextThemeStyle.TITLE_LARGE,
                                                              selectable=False, weight=flet.FontWeight.BOLD, size=20),
                                              actions=[flet.TextButton("Yes",
                                                                       on_click=self.__on_root_found_dialog_yes_button_clicked),
                                                       flet.TextButton("No", on_click=self.__on_exit_button_clicked),
                                                       ],
                                              )

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

    def __show_page(self):
        self.__init_window()
        self.__add_app_title_and_dialog()
        self.__add_controls()
        self.__page.add(self.__plot)
        self.__page.update()

    def __init_input_related_content(self):
        self.__function_input = flet.TextField(label="f(x)", value=self.__function_string_value, width=310,
                                               on_change=self.__on_function_string_value_changed)

        self.__starting_value_input = flet.TextField(label="X (Starting Value)", value=str(self.__starting_value),
                                                     width=150, on_change=self.__on_starting_value_changed)
        self.__tolerance_slider = flet.Slider(min=1, max=16, value=6, divisions=15, label="{value} Tolerance",
                                              on_change=self.__on_tolerance_slider_change, expand=True,
                                              active_color=flet.colors.PURPLE_ACCENT_400, thumb_color=flet.colors.AMBER)
        self.__tolerance_text = flet.Text(value=f"{self.__tolerance:.2e}", style=flet.TextThemeStyle.BODY_SMALL)
        self.__iteration_speed_dropdown = flet.Dropdown(label="Iteration Speed", width=150,
                                                        options=[flet.dropdown.Option('Turtle'),
                                                                 flet.dropdown.Option('Slow'),
                                                                 flet.dropdown.Option('Medium'),
                                                                 flet.dropdown.Option('Fast'),
                                                                 flet.dropdown.Option('Sonic!')],
                                                        on_change=self.__on_iteration_speed_dropdown_change,
                                                        value='Medium')
        self.__iteration_speed = ITERATION_SPEEDS['Medium']

    def __init_static_content(self):
        self.__app_icon = flet.Icon(name=flet.icons.CALCULATE, size=48)
        self.__app_title = flet.Text(value="Newton Raphson Method", style=flet.TextThemeStyle.DISPLAY_SMALL)
        self.__exit_button = flet.IconButton(icon=flet.icons.CANCEL_OUTLINED, tooltip="Exit", icon_size=48,
                                             on_click=self.__on_exit_button_clicked)

    def __init_dynamic_content(self):
        self.__calculate_button = flet.IconButton(icon=flet.icons.NOT_STARTED, tooltip="Start", icon_size=48,
                                                  on_click=self.__on_calculate_button_clicked)
        self.__root_text = flet.Text(value="", style=flet.TextThemeStyle.BODY_LARGE, selectable=False, size=20,
                                     text_align=flet.TextAlign.CENTER, weight=flet.FontWeight.BOLD)
        self.__fig = px.line()
        self.__plot = PlotlyChart(self.__fig)


class NewtonRaphsonThread(Thread):
    __iteration_speed: float
    __starting_value: float
    __function: callable
    __tolerance: float
    __parent: NewtonRaphsonGUI
    __cancellation_token: bool

    def __init__(self, parent: NewtonRaphsonGUI, speed, starting_value, function, tolerance):
        super().__init__()
        self.__iteration_speed = speed
        self.__starting_value = starting_value
        self.__function = function
        self.__tolerance = tolerance
        self.__parent = parent
        self.__cancellation_token = False

    def kill(self):
        self.__cancellation_token = True

    def run(self) -> None:
        current_x_value = self.__starting_value
        current_function_value = self.__function(current_x_value)
        iteration_counter = 0
        while True:
            iteration_counter += 1
            # Calculate derivative at current value of x and interpret as slope.
            slope = finite_difference(self.__function, current_x_value)

            # Store the previous x value for visualization purposes.
            previous_x_value = current_x_value
            # Update the current x value. Essential part of Newton Raphson algorithm.
            current_x_value = current_x_value - self.__function(current_x_value) / slope
            # Recalculate function value for updated x value.
            current_function_value = self.__function(current_x_value)

            root_found = abs(current_function_value) < self.__tolerance

            if not self.__cancellation_token:
                self.__parent.on_notify(slope, previous_x_value, current_x_value, current_function_value,
                                        iteration_counter,
                                        root_found)

            if root_found or self.__cancellation_token:
                break
            time.sleep(self.__iteration_speed)


if __name__ == '__main__':
    flet.app(target=NewtonRaphsonGUI)
