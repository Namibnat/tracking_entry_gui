import datetime
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from db import write_new_tracking_type, add_record, get_tracking_types

CREATOR_METHOD = 0
CREATOR_TITLE = 1
WORK_GRID_ROWS = 7


def display_message(title, message, is_error=True):
    """Message Modal
    """
    if is_error:
        messagebox.showerror(
            title=title,
            message=message
        )
    else:
        messagebox.showinfo(
            title=title,
            message=message
        )


class AddItemDialog(tk.Toplevel):
    """
    Modal dialog for adding a new item.
    """
    def __init__(self, parent: tk.Tk):
        super().__init__(parent)
        self.result = False
        self.title("Add Item")
        self.resizable(width=False, height=False)
        self.next_dropdown_row = 0
        self.notes_base_row = self.next_dropdown_row + 2
        self.drop_down_entry_counter = 0
        self.notes_selected = tk.BooleanVar(value=False)
        self.notes_frame = None
        self.add_another_field = None
        self.drop_down_str_values = list()
        self.new_field_values = {
            'title': str(),
            'drop-down': list(),
            'note': False
        }

        frm = ttk.Frame(master=self, padding=12)
        frm.grid(sticky="nsew")
        self.columnconfigure(index=0, weight=1)
        self.rowconfigure(index=00, weight=1)

        self.input_section = ttk.Frame(frm, padding=12)

        # title (required)
        self.title_value = tk.StringVar()
        title_prompt_label = ttk.Label(master=self.input_section, text="Provide a Title")
        title_label = ttk.Label(master=self.input_section, text="Title")
        title_input = ttk.Entry(master=self.input_section, textvariable=self.title_value)
        warning_label_style = ttk.Style()
        warning_label_style.configure(
            style="TW.Label",
            foreground="red",
            font=('Helvetica', 12, 'bold')
        )
        self.need_title_warning = ttk.Label(
            master=self.input_section,
            text="Title required",
            style="TW.Label"
        )

        title_prompt_label.grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="e",
            pady=(4, 12),
            padx=(4, 4)
        )
        title_label.grid(row=1, column=0, sticky="e", pady=(0, 20))
        title_input.grid(row=1, column=1, sticky="e", pady=(0, 20))

        self._add_dropdown()

        self.input_section.grid(row=1, column=0, sticky="w", rowspan=10)

        self.base_style = ttk.Style()
        btns = ttk.Frame(frm)

        cancel_button = ttk.Button(master=btns, text="Cancel", command=self._on_cancel)
        add_button = ttk.Button(btns, text="Add", command=self._on_add)
        cancel_button.grid(row=self.notes_base_row + 2, column=0, padx=(0, 6))
        add_button.grid(row=self.notes_base_row + 2, column=1, padx=(0, 6))

        btns.grid(row=11, column=0, sticky="e")

        # Make Enter/Esc work nicely
        self.bind("<Return>", lambda e: self._on_add())
        self.bind("<Escape>", lambda e: self._on_cancel())

        # Center relative to parent
        self.transient(parent)
        self.grab_set()

    def _add_dropdown(self):
        """Inputs that will fill drop-downs on daily recording"""
        self.next_dropdown_row += 2
        if self.drop_down_entry_counter == 0:
            drop_down_prompt_label = ttk.Label(
                master=self.input_section,
                text="Add items to drop-down selector"
            )
            drop_down_prompt_label.grid(
                row=self.next_dropdown_row,
                column=0,
                columnspan=2,
                sticky="e",
                pady=(4, 12),
                padx=(4, 4)
            )
        else:
            self.add_another_field.destroy()
        self.drop_down_str_values.append(tk.StringVar())
        drop_down_label = ttk.Label(master=self.input_section, text="Drop Down")
        drop_down_input = ttk.Entry(
            master=self.input_section,
            textvariable=self.drop_down_str_values[self.drop_down_entry_counter]
        )
        self.add_another_field = ttk.Button(
            master=self.input_section,
            text="+",
            command=self._add_dropdown
        )

        # Packing the drop-down
        drop_down_label.grid(
            row=self.next_dropdown_row + 1,
            column=0,
            sticky="e",
            pady=(4, 12),
            padx=(4, 4)
        )
        drop_down_input.grid(
            row=self.next_dropdown_row + 1,
            column=1,
            sticky="e",
            pady=(4, 12),
            padx=(4, 4)
        )
        self.add_another_field.grid(
            row=self.next_dropdown_row + 1,
            column=2,
            sticky="e",
            pady=(4, 12),
            padx=(4, 4)
        )
        self._add_notes_rows()
        self.drop_down_entry_counter += 1

    def _add_notes_rows(self):
        """Notes section, just boolean - have on or not."""
        self.notes_base_row = self.next_dropdown_row + 2
        if self.notes_frame:
            self.notes_frame.destroy()
        self.notes_frame = ttk.Frame(self.input_section)

        notes_prompt_label = ttk.Label(
            master=self.notes_frame,
            text="Include Notes Section?"
        )
        notes_selection_yes = ttk.Radiobutton(
            master=self.notes_frame,
            text='Yes',
            value=True,
            variable=self.notes_selected,
            style='Toolbutton'
        )
        notes_selection_no = ttk.Radiobutton(
            master=self.notes_frame,
            text='No',
            value=False,
            variable=self.notes_selected,
            style='Toolbutton'
        )
        notes_prompt_label.grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="e",
            pady=(4, 12),
            padx=(4, 4)
        )
        notes_selection_yes.grid(row=1, column=0, sticky="nsew")
        notes_selection_no.grid(row=1, column=1, sticky="nsew")
        self.notes_frame.grid(row=self.notes_base_row, column=1)

    def _on_cancel(self):
        self.destroy()

    def _on_add(self):
        title = self.title_value.get()
        if not title:
            self.need_title_warning.grid(row=1, column=2, sticky="e", pady=(0, 20))
            return
        self.new_field_values['title'] = title
        drop_down_values = [v.get() for v in self.drop_down_str_values if v]
        self.new_field_values['drop-down'] = drop_down_values
        self.new_field_values['note'] = self.notes_selected.get()
        success = write_new_tracking_type(self.new_field_values)
        if not success:
            display_message(title="Error", message="Record could not be saved")
            return
        self.result = True
        self.destroy()


class MainView(ttk.Frame):
    """Main screen"""
    def __init__(self, parent, controller: "App"):
        super().__init__(master=parent, padding=12, style="DarkMain.TFrame")
        self.controller = controller
        self.panel_frame = ttk.Frame(self)
        self.tracking_tasks = dict()
        self.tracking_tasks = get_tracking_types()

        # Selection Section
        selection_grid_style = ttk.Style()
        selection_grid_style.configure(
            style="SG.TFrame",
            borderwidth=1,
            relief='solid'
        )
        self.selection_frame = ttk.Frame(self, width=250)
        self.selection_frame.grid(
            row=0,
            column=0,
            sticky="nsew",
            ipady=12,
            ipadx=12,
            padx=12,
            pady=12
        )

        # Selection Section
        self._build_listbox()

        # Work Section
        self._fill_panel_frame()

        # Footer
        footer = ttk.Frame(self)
        add_item_button = ttk.Button(
            footer,
            text="Add Item…",
            command=self.controller.add_item_dialog
        )
        add_item_button.grid(row=0, column=0)

        footer.grid(row=1, column=0, columnspan=2, sticky="e", pady=(12, 0))
        
    def _build_listbox(self):
        self.track_tasks = list(self.tracking_tasks.keys())
        self.selection = self.track_tasks[0]
        self.listbox = tk.Listbox(
            self.selection_frame,
            height=12,
            selectmode="browse",
            exportselection=False
        )
        scrollbar = ttk.Scrollbar(
            master=self.selection_frame,
            orient="vertical",
            command=self.listbox.yview
        )
        self.listbox.config(yscrollcommand=scrollbar.set)

        def on_select(event):
            self.panel_frame.destroy()
            self.selection = self.listbox.get(self.listbox.curselection())
            self._fill_panel_frame()

        self.listbox.bind("<<ListboxSelect>>", on_select)

        self.listbox.grid(row=0, column=0, sticky="ns")
        scrollbar.grid(row=0, column=1, sticky="ns")

        for task in self.track_tasks:
            self.listbox.insert("end", task)

    @staticmethod
    def _get_date_range(today, day):
        return datetime.datetime(today.year, today.month, day)

    @staticmethod
    def _date_labels(master, date):
        return ttk.Label(master=master, text=f"{date:%d/%m/%Y}", width=25)

    @staticmethod
    def _drop_down_maker(master, the_options_that_should_be_packed=None):
        cb = ttk.Combobox(master=master, width=25)
        cb['state'] = 'readonly'
        cb.set('option 1')
        cb['values'] = 'option 1', 'option 2', 'option 3'
        return cb

    @staticmethod
    def _notebook_maker(master, other_stuff=None):
        return ttk.Entry(master, width=25)

    def _save_records(self):
        # Get the records to save
        new_record = {
            'date': datetime.datetime.now(),
            'entry_title': "Study X",
            'drop-down': "Great",
            'notes': "Good study session, and stuff"
        }
        success = add_record(new_record)
        if success:
            display_message(
                title="Saved",
                message="Record saved successfully"
            )
            print("Good save")
        else:
            print("Not good")

    def _get_fields(self):
        fields = get_tracking_types()
        # todo: pick up here....

        today = datetime.datetime.now()
        day_range = range(today.day, today.day-WORK_GRID_ROWS, -1)
        past_week_date_strs = (self._get_date_range(today, day) for day in day_range)
        # TODO: fills to be updated from DB
        fills = {
            'date': [date for date in past_week_date_strs],
            'drop-down': ['drop-down thingi'] * WORK_GRID_ROWS,
            'notes': ['notes']*WORK_GRID_ROWS
        }
        creators = (
            (self._date_labels, 'date'),
            (self._drop_down_maker, 'drop-down'),
            (self._notebook_maker, 'notes')
        )
        return fills, creators

    def _fill_panel_frame(self):
        self.panel_frame_style = ttk.Style()
        self.panel_frame_style.configure(
            style="PA.TFrame",
            borderwidth=1,
            relief='solid'
        )
        self.panel_frame = ttk.Frame(self)
        self.panel_frame.grid(
            row=0,
            column=1,
            sticky="nsew",
        )

        panel_title = ttk.Label(master=self.panel_frame, text=self.selection)
        panel_title.grid(
            row=0,
            column=0,
            columnspan=3,
            pady=12
        )
        gird_titles = ttk.Frame(
            master=self.panel_frame
        )
        for column, title in enumerate(['Date', 'Selection', 'Notes']):
            title_label = ttk.Label(
                master=gird_titles,
                text=title,
                width=25,
            )
            title_label.grid(
                row=0,
                column=column,
                padx=0,
                pady=0,
                ipadx=2,
                ipady=2,
                sticky="ew"
            )
        gird_titles.grid(row=1, column=0, sticky="nsew")

        work_grid = ttk.Frame(self.panel_frame)
        fills, creators = self._get_fields()

        for row in range(WORK_GRID_ROWS):
            for column, creator in enumerate(creators):
                box = ttk.Frame(master=work_grid, width=182)
                box.grid(
                    row=row,
                    column=column,
                    padx=0,
                    pady=0,
                    ipadx=2,
                    ipady=2,
                    sticky="nsew"
                )
                title = creator[CREATOR_TITLE]
                placer = creator[CREATOR_METHOD](box, fills[title][row])
                placer.grid(
                    row=0,
                    column=0,
                    padx=2,
                    pady=2,
                    ipadx=2,
                    ipady=2,
                    sticky="e"
                )
        work_grid.grid(row=3, column=0, sticky="nsew")
        panel_button_style = ttk.Style()
        panel_button_style.configure(
            style="PA.TButton",
            font=('Helvetica', 16)
        )
        save_button = ttk.Button(
            self.panel_frame,
            text="Save",
            padding=16,
            style="PA.TButton",
            command=self._save_records
        )
        save_button.grid(
            row=4,
            column=0,
            sticky="e"
        )
        quit_button = ttk.Button(
            self.panel_frame,
            text="Quit",
            padding=16,
            style="PA.TButton",
            command=self.controller.destroy
        )
        quit_button.grid(
            row=4,
            column=1,
            sticky="e",
            padx=(12, 0)
        )

    def refresh(self):
        self.tracking_tasks = get_tracking_types()
        self.listbox.destroy()
        self._build_listbox()



class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Tracking Entry")

        # Menu
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        file_menu = tk.Menu(menubar, tearoff=False)
        file_menu.add_command(label="Add Item…", command=self.add_item_dialog)
        file_menu.add_separator()
        file_menu.add_command(label="Quit", command=self.destroy)
        menubar.add_cascade(label="File", menu=file_menu)

        # Main view
        style = ttk.Style()
        style.configure(style="TFrame", background="#1f1f1f")
        self.view = MainView(self, controller=self)
        self.view.grid(sticky="nsew")
        self.grid_rowconfigure(index=0, weight=1)
        self.grid_columnconfigure(index=0, weight=1)

    def add_item_dialog(self):
        add_item_dialog = AddItemDialog(self)
        self.wait_window(add_item_dialog)
        if add_item_dialog.result:
            self.view.refresh()


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
