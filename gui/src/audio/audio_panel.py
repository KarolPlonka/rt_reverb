import tkinter as tk
import customtkinter as ctk
import numpy as np
from PIL import Image

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import audio.audio_processing as AudioProcessor
from styles import (
    COLOR_PALETTE,
    BUTTON_STYLE,
    BUTTON_STYLE_DISABLED,
    ACTION_BUTTON_STYLE,
    SLIDER_STYLE,
    SLIDER_STYLE_DISABLED,
    PROGRESS_BAR_STYLE,
    PLACEHOLDER_BUTTON_STYLE,
)

class AudioPanel(ctk.CTkFrame):
    BACKGROUND_COLOR = COLOR_PALETTE["secondary"]
    ICON_SIZE = (16, 16)
    ICONS_PATH = 'assets/icons/'

    REVERB_SIGNAL_COLOR = COLOR_PALETTE["accent"]
    INPUT_SIGNAL_COLOR = COLOR_PALETTE["primary"]

    def __init__(self, master, is_audio_file_loaded, is_baked, *args, **kwargs):
        super().__init__( 
            master=master,
            fg_color=self.BACKGROUND_COLOR,
            *args, **kwargs
        )

        self.is_audio_file_loaded = is_audio_file_loaded
        self.is_audio_file_loaded.trace_add("write", self.refresh_apply_reverb_state)

        self.is_baked = is_baked
        self.is_baked.trace_add("write", self.refresh_apply_reverb_state)

        self.audio_file = None

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=3)

        self.load_controls()

        self.audio_figure, self.ax = self.load_plot_waveform()

        self.audio_file_frame, self.audio_file_frame_widget, self.audio_file_frame_placeholder = self.load_audio_frame()

        self.caught_rays = None

        self.audio_with_reverb = None

        self.is_reverb_applied = tk.BooleanVar(value=False)
        self.is_reverb_applied.trace_add("write", self.on_is_reverb_applied_change)

        self.applying_reverb_progress = tk.DoubleVar(value=0)
        self.applying_reverb_progress.set(0)
        self.applying_reverb_progress_bar = ctk.CTkProgressBar(
            self,
            mode='determinate',
            variable=self.applying_reverb_progress,
            orientation=tk.VERTICAL,
            height=120,
            **PROGRESS_BAR_STYLE
        )


    def load_controls(self):
        self.buttons_frame = tk.Frame(self, background=self.BACKGROUND_COLOR)
        self.buttons_frame.pack(side=tk.LEFT, padx=10)

        self.apply_reverb_button = ctk.CTkButton(
            self.buttons_frame,
            text="Apply reverb",
            command=self.apply_reverb_on_click,
            state=tk.DISABLED
        )
        self.apply_reverb_button.configure(**BUTTON_STYLE_DISABLED)
        self.apply_reverb_button.grid(column=0, row=0, columnspan=2, pady=10)

        self.play_button = ctk.CTkButton(self.buttons_frame,
            image=ctk.CTkImage(Image.open(self.ICONS_PATH + 'play.png'), size=self.ICON_SIZE),
            text=None,
            command=self.play_audio_on_click,
            state=tk.DISABLED
        )
        self.play_button.configure(**BUTTON_STYLE_DISABLED, width=30, height=30)
        self.play_button.grid(column=0, row=1)

        self.stop_button = ctk.CTkButton(self.buttons_frame,
            image=ctk.CTkImage(Image.open(self.ICONS_PATH + 'stop.png'), size=self.ICON_SIZE),
            text=None,
            command=self.stop_audio_on_click,
            state=tk.DISABLED
        )
        self.stop_button.configure(**BUTTON_STYLE_DISABLED, width=30, height=30)
        self.stop_button.grid(column=1, row=1)


        self.audio_gain = tk.DoubleVar(value=0)
        self.audio_gain.trace_add("write", self.on_apply_gain_change)
        self.audio_gain_slider = ctk.CTkSlider(
            self,
            from_=0,
            to=24,
            number_of_steps=24,
            orientation=tk.VERTICAL,
            variable=self.audio_gain,
            state=tk.DISABLED,
        )
        self.audio_gain_slider.configure(height=100, **SLIDER_STYLE_DISABLED)
        self.audio_gain_slider.pack(side=tk.LEFT, pady=10)


    def load_audio_frame(self):
        audio_file_frame = FigureCanvasTkAgg(self.audio_figure, self)

        audio_file_frame_widget = audio_file_frame.get_tk_widget()
        audio_file_frame_widget.config(cursor="hand2")
        audio_file_frame_widget.bind("<ButtonPress-1>", self.load_audio_file)

        audio_file_frame_placeholder = ctk.CTkButton(self, text="Load audio file", command=self.load_audio_file, **PLACEHOLDER_BUTTON_STYLE)
        audio_file_frame_placeholder.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20)

        return audio_file_frame, audio_file_frame_widget, audio_file_frame_placeholder


    def export_with_reverb(self, export_path, caught_rays):
        self.show_progress_bar()

        signal, fs = AudioProcessor.get_stereo_reverb(self.audio_file, caught_rays, self.applying_reverb_progress)

        self.hide_progress_bar()

        AudioProcessor.export_wave_file(signal, fs, export_path)

        self.audio_with_reverb = {'signal': signal, 'signal_with_gain': signal, 'fs': fs}

        self.is_reverb_applied.set(True)


    @AudioProcessor.run_in_new_thread
    def apply_reverb_on_click(self):
        self.apply_reverb_button.configure(state = tk.DISABLED, **BUTTON_STYLE_DISABLED)
        
        self.show_progress_bar()

        signal, fs = AudioProcessor.get_stereo_reverb(self.audio_file, self.caught_rays, self.applying_reverb_progress)

        self.hide_progress_bar()

        self.audio_with_reverb = {'signal': signal, 'signal_with_gain': signal, 'fs': fs}

        self.is_reverb_applied.set(True)

        self.add_to_plot(
            signal,
            np.linspace(0, len(signal) / fs, num=len(signal)),
            self.REVERB_SIGNAL_COLOR
        )


    def play_audio_on_click(self):
        AudioProcessor.play_audio(self.audio_with_reverb['signal_with_gain'])


    def stop_audio_on_click(self):
        AudioProcessor.stop_audio()


    def set_audio_file(self, audio_file):
        self.audio_file_frame_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20)
        self.audio_file_frame_placeholder.pack_forget()

        self.audio_file = audio_file
        self.is_audio_file_loaded.set(True)

        self.clear_plot()
        self.add_to_plot(
            audio_file['signal'],
            audio_file['time'],
            self.INPUT_SIGNAL_COLOR,
        )

    
    def load_audio_file(self, *args):
        file_path = tk.filedialog.askopenfilename(filetypes=[("Wave files", "*.wav")])
        if file_path:
            audio_file = AudioProcessor.load_wave_file(file_path)
            self.set_audio_file(audio_file)

        self.is_reverb_applied.set(False)


    def load_plot_waveform(self):
        audio_figure = Figure(figsize=(8, 1), facecolor=self.BACKGROUND_COLOR)
        audio_figure.subplots_adjust(left=0, right=1, bottom=0, top=1)

        ax = audio_figure.add_subplot(111)
        ax.axis('off')

        return audio_figure, ax
    

    def add_to_plot(self, signal, time, color):
        if self.audio_file and self.ax:
            self.ax.plot(time, signal, color=color, linewidth=1, zorder=1)
            self.ax.set_xbound(lower=0, upper=time.max())
            self.ax.set_facecolor(self.BACKGROUND_COLOR)
            self.ax.axis('off')

            self.audio_file_frame.draw()


    def clear_plot(self):
        self.ax.clear()


    def set_caught_rays(self, caught_rays):
        self.caught_rays = caught_rays

        self.audio_with_reverb = None

        self.is_reverb_applied.set(False)

        if self.is_audio_file_loaded.get():
            self.clear_plot()
            self.add_to_plot(
                self.audio_file['signal'],
                self.audio_file['time'],
                self.INPUT_SIGNAL_COLOR,
            )


        




    def refresh_apply_reverb_state(self, *args):
        if self.is_audio_file_loaded.get() and self.is_baked.get():
            self.apply_reverb_button.configure(state = tk.NORMAL, **ACTION_BUTTON_STYLE)
        else:
            self.apply_reverb_button.configure(state = tk.DISABLED, **BUTTON_STYLE_DISABLED)


    def on_is_reverb_applied_change(self, *args):
        if self.is_reverb_applied.get():
            self.play_button.configure(state = tk.NORMAL, **BUTTON_STYLE)
            self.stop_button.configure(state = tk.NORMAL, **BUTTON_STYLE)
            self.audio_gain_slider.configure(state = tk.NORMAL, **SLIDER_STYLE)
        else:
            self.play_button.configure(state = tk.DISABLED, **BUTTON_STYLE_DISABLED)
            self.stop_button.configure(state = tk.DISABLED, **BUTTON_STYLE_DISABLED)
            self.audio_gain_slider.configure(state = tk.DISABLED, **SLIDER_STYLE_DISABLED)


    def on_apply_gain_change(self, *args):
        if not self.is_reverb_applied.get():
            return
        
        fs = self.audio_with_reverb['fs']

        gain = self.audio_gain.get()

        self.audio_with_reverb['signal_with_gain'] = self.audio_with_reverb['signal'] * (10 ** (gain / 20))
        self.audio_with_reverb['signal_with_gain'] = self.audio_with_reverb['signal_with_gain'].astype(np.int16)

        self.clear_plot()

        self.add_to_plot(
            self.audio_file['signal'], 
            self.audio_file['time'],
            self.INPUT_SIGNAL_COLOR
        )

        self.add_to_plot(
            self.audio_with_reverb['signal_with_gain'],
            np.linspace(
                start = 0,
                stop = len(self.audio_with_reverb['signal_with_gain']) / fs,
                num = len(self.audio_with_reverb['signal_with_gain'])
            ),
            self.REVERB_SIGNAL_COLOR
        )


    def show_progress_bar(self):
        self.applying_reverb_progress_bar.pack(side=tk.RIGHT)


    def hide_progress_bar(self):
        self.applying_reverb_progress_bar.pack_forget()
    




