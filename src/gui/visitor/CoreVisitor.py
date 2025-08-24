import tkinter as tk

from src.core.TextResource import tr
from src.core.holders import prop
from src.gui.gui import GUI
from src.gui.visitor.Visitor import Visitor
from src.util.date import extract_date
from datetime import date


class CoreVisitor(Visitor):

    def visit(self, gui: GUI):
        self.__add_last_save_info(gui)
        self.__add_buttons_internal(gui)
        self.__add_copyright_and_version(gui)

    def is_enabled(self):
        return True

    @staticmethod
    def __add_last_save_info(gui):
        info_frame = tk.Frame(gui.body_frame)
        last_save_meta = gui.last_save_func()
        last_save_info_label = ""

        if last_save_meta is not None:
            date_info = extract_date(last_save_meta["createdTime"])
            last_save_info_label = tr(
                "info_NewestSaveOnCloudInformation",
                date_info["date"],
                date_info["time"],
                last_save_meta["owner"]
            )

        gui.save_status = tk.Label(
            info_frame,
            text=gui.get_last_download_version_text(last_save_meta),
            fg=prop("primaryColor"),
            font=("Helvetica", 25)
        )

        gui.last_save_info = tk.Label(
            info_frame,
            text=last_save_info_label,
            fg=prop("secondaryColor"),
            font=("Helvetica", 11, 'bold')
        )

        gui.save_status.grid(row=0, column=0, pady=5)
        gui.last_save_info.grid(row=1, column=0, pady=5)

        info_frame.grid(row=0, column=0, pady=150)

    @staticmethod
    def __add_buttons_internal(gui):

        btn_property_list = [prop("primaryButton"), prop("secondaryButton")]

        def on_button_leave(e):
            color_mapping = {btn["colorHover"]: btn["colorStatic"] for btn in btn_property_list}
            e.widget['bg'] = color_mapping[e.widget['bg']]

        def on_button_enter(e):
            color_mapping = {btn["colorStatic"]: btn["colorHover"] for btn in btn_property_list}
            e.widget['bg'] = color_mapping[e.widget['bg']]

        button_frame = tk.Frame(gui.body_frame)

        for idx, button in enumerate(gui.buttons):
            tk_button = tk.Button(
                button_frame,
                width=button["properties"]["width"],
                text=button["name"],
                command=button["callback"]
            )

            tk_button.grid(row=0, column=idx, padx=5)
            tk_button.config(
                fg=prop("primaryColor"),
                bg=button["properties"]["colorStatic"],
                borderwidth=0,
                relief=tk.SOLID,
                pady=15,
                padx=15,
                font=40
            )

            tk_button.bind('<Enter>', on_button_enter)
            tk_button.bind('<Leave>', on_button_leave)

        button_frame.grid(row=1, column=0)

    @staticmethod
    def __add_copyright_and_version(gui):

        horizontal_frame = tk.Frame(gui.window, pady=-4)

        version_label = tk.Label(horizontal_frame, text=f"v{prop("version")}")
        version_label.grid(row=0, column=0, padx=5)

        copy = f"© 2023{'' if date.today().year == 2023 else f'-{date.today().year}'}"
        copyright_label = tk.Label(horizontal_frame, text=tr("window_Signature", copy))
        copyright_label.grid(row=0, column=1)

        horizontal_frame.place(relx=.5, rely=.9, anchor=tk.N)
