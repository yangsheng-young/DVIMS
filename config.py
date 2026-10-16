# -*- coding: utf-8 -*-

"""
==========================================================
Project : NNBI_database
File    : config.py
Author  :
Date    :
==========================================================
"""

import os
import configparser


class Config(object):
    """
    Application Configuration
    """

    def __init__(self):
        self.ini_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "config",
            "config.ini"
        )

        self.parser = configparser.ConfigParser()

        # ==================================================
        # APP
        # ==================================================

        self.name = "NNBI_database"
        self.version = "1.0.0"
        self.author = ""
        self.check_update = False

        # ==================================================
        # MDSPLUS
        # ==================================================

        self.host = "localhost"
        self.port = 8000
        self.tree = "RFDATA_TREE"
        self.shot = -1

        self.auto_connect = False
        self.auto_open_tree = False
        self.timeout = 5

        # ==================================================
        # UI
        # ==================================================

        self.theme = "Light"

        self.show_statusbar = True
        self.show_toolbar = True
        self.show_tree = True
        self.show_parameter_panel = True
        self.show_additional_parameter_panel = False

        self.maximized = True

        self.font = "Microsoft YaHei"
        self.font_size = 10

        # ==================================================
        # TREE
        # ==================================================

        self.auto_expand = True
        self.double_click_open = True
        self.show_full_path = False

        # ==================================================
        # WAVEFORM
        # ==================================================

        self.new_tab = True

        self.background = "w"
        self.foreground = "k"

        self.antialias = True
        self.show_grid = True

        self.wheel_zoom = True
        self.auto_range = True

        self.show_crosshair = True
        self.show_legend = True

        self.panel_layout = "auto"
        self.panel_rows = 2
        self.panel_columns = 2
        self.default_panel_count = 1

        self.downsample_enabled = True
        self.max_points = 10000
        self.downsample_mode = "stride"

        # ==================================================
        # CURRENT SHOT PARAMETERS
        # ==================================================

        self.voltage_node = ""
        self.set_voltage_node = ""
        self.hv_status_node = ""

        self.beam_current_node = ""
        self.arc_current_node = ""
        self.filament_current_node = ""

        self.voltage_unit = "kV"
        self.set_voltage_unit = "kV"
        self.beam_current_unit = "mA"
        self.arc_current_unit = "A"
        self.filament_current_unit = "A"

        # ==================================================
        # REFRESH
        # ==================================================

        self.auto_refresh = False
        self.interval = 1000

        # ==================================================
        # LOG
        # ==================================================

        self.log_enable = True
        self.log_level = "INFO"

        self.log_path = "logs"

        self.max_size = 10
        self.backup_count = 5

        # ==================================================
        # EXPORT
        # ==================================================

        self.export_path = "export"

        self.image_format = "png"
        self.data_format = "csv"

        self.export_image_width = 1600

    # ======================================================
    # Load
    # ======================================================

    def load(self):
        if not os.path.exists(self.ini_path):
            self.save()
            return

        self.parser.read(self.ini_path, encoding="utf-8")

        # APP

        self.name = self.parser.get(
            "APP",
            "name",
            fallback=self.name
        )

        self.version = self.parser.get(
            "APP",
            "version",
            fallback=self.version
        )

        self.author = self.parser.get(
            "APP",
            "author",
            fallback=self.author
        )

        self.check_update = self.parser.getboolean(
            "APP",
            "check_update",
            fallback=self.check_update
        )

        # MDSPLUS

        self.host = self.parser.get(
            "MDSPLUS",
            "host",
            fallback=self.host
        )

        self.port = self.parser.getint(
            "MDSPLUS",
            "port",
            fallback=self.port
        )

        self.tree = self.parser.get(
            "MDSPLUS",
            "tree",
            fallback=self.tree
        )

        self.shot = self.parser.getint(
            "MDSPLUS",
            "shot",
            fallback=self.shot
        )

        self.auto_connect = self.parser.getboolean(
            "MDSPLUS",
            "auto_connect",
            fallback=self.auto_connect
        )

        self.auto_open_tree = self.parser.getboolean(
            "MDSPLUS",
            "auto_open_tree",
            fallback=self.auto_open_tree
        )

        self.timeout = self.parser.getint(
            "MDSPLUS",
            "timeout",
            fallback=self.timeout
        )

        # UI

        self.theme = self.parser.get(
            "UI",
            "theme",
            fallback=self.theme
        )

        self.show_statusbar = self.parser.getboolean(
            "UI",
            "show_statusbar",
            fallback=self.show_statusbar
        )

        self.show_toolbar = self.parser.getboolean(
            "UI",
            "show_toolbar",
            fallback=self.show_toolbar
        )

        self.show_tree = self.parser.getboolean(
            "UI",
            "show_tree",
            fallback=self.show_tree
        )

        self.show_parameter_panel = self.parser.getboolean(
            "UI",
            "show_parameter_panel",
            fallback=self.show_parameter_panel
        )

        self.show_additional_parameter_panel = self.parser.getboolean(
            "UI",
            "show_additional_parameter_panel",
            fallback=self.show_additional_parameter_panel
        )

        self.maximized = self.parser.getboolean(
            "UI",
            "maximized",
            fallback=self.maximized
        )

        self.font = self.parser.get(
            "UI",
            "font",
            fallback=self.font
        )

        self.font_size = self.parser.getint(
            "UI",
            "font_size",
            fallback=self.font_size
        )

        # TREE

        self.auto_expand = self.parser.getboolean(
            "TREE",
            "auto_expand",
            fallback=self.auto_expand
        )

        self.double_click_open = self.parser.getboolean(
            "TREE",
            "double_click_open",
            fallback=self.double_click_open
        )

        self.show_full_path = self.parser.getboolean(
            "TREE",
            "show_full_path",
            fallback=self.show_full_path
        )

        # WAVEFORM

        self.new_tab = self.parser.getboolean(
            "WAVEFORM",
            "new_tab",
            fallback=self.new_tab
        )

        self.background = self.parser.get(
            "WAVEFORM",
            "background",
            fallback=self.background
        )

        self.foreground = self.parser.get(
            "WAVEFORM",
            "foreground",
            fallback=self.foreground
        )

        self.antialias = self.parser.getboolean(
            "WAVEFORM",
            "antialias",
            fallback=self.antialias
        )

        self.show_grid = self.parser.getboolean(
            "WAVEFORM",
            "show_grid",
            fallback=self.show_grid
        )

        self.wheel_zoom = self.parser.getboolean(
            "WAVEFORM",
            "wheel_zoom",
            fallback=self.wheel_zoom
        )

        self.auto_range = self.parser.getboolean(
            "WAVEFORM",
            "auto_range",
            fallback=self.auto_range
        )

        self.show_crosshair = self.parser.getboolean(
            "WAVEFORM",
            "show_crosshair",
            fallback=self.show_crosshair
        )

        self.show_legend = self.parser.getboolean(
            "WAVEFORM",
            "show_legend",
            fallback=self.show_legend
        )

        self.panel_layout = self.parser.get(
            "WAVEFORM",
            "panel_layout",
            fallback=self.panel_layout
        ).strip().lower()

        if self.panel_layout not in (
                "vertical",
                "horizontal",
                "auto",
                "grid"
        ):
            self.panel_layout = "auto"

        self.panel_rows = max(
            1,
            self.parser.getint(
                "WAVEFORM",
                "panel_rows",
                fallback=self.panel_rows
            )
        )

        self.panel_columns = max(
            1,
            self.parser.getint(
                "WAVEFORM",
                "panel_columns",
                fallback=self.panel_columns
            )
        )

        self.default_panel_count = max(
            1,
            self.parser.getint(
                "WAVEFORM",
                "default_panel_count",
                fallback=self.default_panel_count
            )
        )

        self.downsample_enabled = self.parser.getboolean(
            "WAVEFORM",
            "downsample_enabled",
            fallback=self.downsample_enabled
        )

        self.max_points = max(
            100,
            self.parser.getint(
                "WAVEFORM",
                "max_points",
                fallback=self.max_points
            )
        )

        self.downsample_mode = self.parser.get(
            "WAVEFORM",
            "downsample_mode",
            fallback=self.downsample_mode
        ).strip().lower()

        if self.downsample_mode != "stride":
            self.downsample_mode = "stride"

        # CURRENT SHOT PARAMETERS

        self.voltage_node = self.parser.get(
            "SHOT_PARAMETERS",
            "voltage_node",
            fallback=self.voltage_node
        )

        self.set_voltage_node = self.parser.get(
            "SHOT_PARAMETERS",
            "set_voltage_node",
            fallback=self.set_voltage_node
        )

        self.hv_status_node = self.parser.get(
            "SHOT_PARAMETERS",
            "hv_status_node",
            fallback=self.hv_status_node
        )

        self.beam_current_node = self.parser.get(
            "SHOT_PARAMETERS",
            "beam_current_node",
            fallback=self.beam_current_node
        )

        self.arc_current_node = self.parser.get(
            "SHOT_PARAMETERS",
            "arc_current_node",
            fallback=self.arc_current_node
        )

        self.filament_current_node = self.parser.get(
            "SHOT_PARAMETERS",
            "filament_current_node",
            fallback=self.filament_current_node
        )

        self.voltage_unit = self.parser.get(
            "SHOT_PARAMETERS",
            "voltage_unit",
            fallback=self.voltage_unit
        )

        self.set_voltage_unit = self.parser.get(
            "SHOT_PARAMETERS",
            "set_voltage_unit",
            fallback=self.set_voltage_unit
        )

        self.beam_current_unit = self.parser.get(
            "SHOT_PARAMETERS",
            "beam_current_unit",
            fallback=self.beam_current_unit
        )

        self.arc_current_unit = self.parser.get(
            "SHOT_PARAMETERS",
            "arc_current_unit",
            fallback=self.arc_current_unit
        )

        self.filament_current_unit = self.parser.get(
            "SHOT_PARAMETERS",
            "filament_current_unit",
            fallback=self.filament_current_unit
        )

        # REFRESH

        self.auto_refresh = self.parser.getboolean(
            "REFRESH",
            "auto_refresh",
            fallback=self.auto_refresh
        )

        self.interval = self.parser.getint(
            "REFRESH",
            "interval",
            fallback=self.interval
        )

        # LOG

        self.log_enable = self.parser.getboolean(
            "LOG",
            "enable",
            fallback=self.log_enable
        )

        self.log_level = self.parser.get(
            "LOG",
            "level",
            fallback=self.log_level
        )

        self.log_path = self.parser.get(
            "LOG",
            "path",
            fallback=self.log_path
        )

        self.max_size = self.parser.getint(
            "LOG",
            "max_size",
            fallback=self.max_size
        )

        self.backup_count = self.parser.getint(
            "LOG",
            "backup_count",
            fallback=self.backup_count
        )

        # EXPORT

        self.export_path = self.parser.get(
            "EXPORT",
            "path",
            fallback=self.export_path
        )

        self.image_format = self.parser.get(
            "EXPORT",
            "image_format",
            fallback=self.image_format
        )

        self.data_format = self.parser.get(
            "EXPORT",
            "data_format",
            fallback=self.data_format
        )

        self.export_image_width = self.parser.getint(
            "EXPORT",
            "image_width",
            fallback=self.export_image_width
        )

        if self.export_image_width < 100:
            self.export_image_width = 100

    # ======================================================
    # Save
    # ======================================================

    def save(self):
        self.parser["APP"] = {
            "name": self.name,
            "version": self.version,
            "author": self.author,
            "check_update": str(self.check_update)
        }

        self.parser["MDSPLUS"] = {
            "host": self.host,
            "port": str(self.port),
            "tree": self.tree,
            "shot": str(self.shot),
            "auto_connect": str(self.auto_connect),
            "auto_open_tree": str(self.auto_open_tree),
            "timeout": str(self.timeout)
        }

        self.parser["UI"] = {
            "theme": self.theme,
            "show_statusbar": str(self.show_statusbar),
            "show_toolbar": str(self.show_toolbar),
            "show_tree": str(self.show_tree),
            "show_parameter_panel": str(
                self.show_parameter_panel
            ),
            "show_additional_parameter_panel": str(
                self.show_additional_parameter_panel
            ),
            "maximized": str(self.maximized),
            "font": self.font,
            "font_size": str(self.font_size)
        }

        self.parser["TREE"] = {
            "auto_expand": str(self.auto_expand),
            "double_click_open": str(self.double_click_open),
            "show_full_path": str(self.show_full_path)
        }

        self.parser["WAVEFORM"] = {
            "new_tab": str(self.new_tab),
            "background": self.background,
            "foreground": self.foreground,
            "antialias": str(self.antialias),
            "show_grid": str(self.show_grid),
            "wheel_zoom": str(self.wheel_zoom),
            "auto_range": str(self.auto_range),
            "show_crosshair": str(self.show_crosshair),
            "show_legend": str(self.show_legend),
            "panel_layout": self.panel_layout,
            "panel_rows": str(self.panel_rows),
            "panel_columns": str(self.panel_columns),
            "default_panel_count": str(self.default_panel_count),
            "downsample_enabled": str(
                self.downsample_enabled
            ),
            "max_points": str(self.max_points),
            "downsample_mode": self.downsample_mode
        }

        self.parser["SHOT_PARAMETERS"] = {
            "voltage_node": self.voltage_node,
            "set_voltage_node": self.set_voltage_node,
            "hv_status_node": self.hv_status_node,
            "beam_current_node": self.beam_current_node,
            "arc_current_node": self.arc_current_node,
            "filament_current_node": self.filament_current_node,
            "voltage_unit": self.voltage_unit,
            "set_voltage_unit": self.set_voltage_unit,
            "beam_current_unit": self.beam_current_unit,
            "arc_current_unit": self.arc_current_unit,
            "filament_current_unit": self.filament_current_unit
        }

        self.parser["REFRESH"] = {
            "auto_refresh": str(self.auto_refresh),
            "interval": str(self.interval)
        }

        self.parser["LOG"] = {
            "enable": str(self.log_enable),
            "level": self.log_level,
            "path": self.log_path,
            "max_size": str(self.max_size),
            "backup_count": str(self.backup_count)
        }

        self.parser["EXPORT"] = {
            "path": self.export_path,
            "image_format": self.image_format,
            "data_format": self.data_format,
            "image_width": str(self.export_image_width)
        }

        with open(self.ini_path, "w", encoding="utf-8") as f:
            self.parser.write(f)
