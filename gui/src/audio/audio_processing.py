import wave
import numpy as np
import sounddevice as sd
from time import perf_counter
import threading as th
from scipy.io import wavfile

import tkinter as tk

DIFFUSION_COEFFICIENT = 0.3 # 1/s


def load_wave_file(path):
    framerate, signal = wavfile.read(path)

    #Convert stereo to mono
    if signal.ndim == 2:
        signal = signal.mean(axis=1)

    time = np.linspace(0, len(signal) / framerate, num=len(signal))

    return {'signal': signal, 'time': time, 'frame_rate': framerate}


def get_channel_reverb(wave_file, channel_caught_rays, channel_progress):
    data = wave_file['signal']
    fs = wave_file['frame_rate']
    print(fs)

    rays_amount = len(channel_caught_rays)

    maxTime = max([ray["time"] for ray in channel_caught_rays])

    first_ray = min(channel_caught_rays, key=lambda ray: ray["time"])
    minTime = first_ray["time"]

    output = np.zeros(int(maxTime * fs) + len(data))

    # first_ray_index = int(first_ray["time"] * fs)
    # output[first_ray_index:first_ray_index + len(data)] = data * first_ray["energy"]
    
    for i, ray in enumerate(channel_caught_rays):
        channel_progress.set(i / rays_amount)

        index = int(ray["time"] * fs)

        # diffusion = np.exp(-((ray["time"] - minTime) / DIFFUSION_COEFFICIENT))
        diffusion = np.exp(-((ray["time"]) / DIFFUSION_COEFFICIENT))
        # diffusion = 1
        # print("Time: ", ray["time"], "Diffusion: ", diffusion)

        output[index:index + len(data)] += data * ray["energy"] * diffusion

    return output.astype(np.int16), fs


def get_stereo_reverb(wave_file, caught_rays, progress):
    def on_channel_progress_change(*args):
        progress.set((left_channel_progress.get() + right_channel_progress.get()) / 2)

    left_channel_progress = tk.DoubleVar(value = 0)
    right_channel_progress = tk.DoubleVar(value = 0)
    left_channel_progress.trace("w", on_channel_progress_change)
    right_channel_progress.trace("w", on_channel_progress_change)

    left_channel_signal, fs = get_channel_reverb(wave_file, caught_rays['left'], left_channel_progress)
    right_channel_signal, fs = get_channel_reverb(wave_file, caught_rays['right'], right_channel_progress)

    if left_channel_signal.shape[0] < right_channel_signal.shape[0]:
        left_channel_signal = np.pad(left_channel_signal, (0, right_channel_signal.shape[0] - left_channel_signal.shape[0]), 'constant')
    elif left_channel_signal.shape[0] > right_channel_signal.shape[0]:
        right_channel_signal = np.pad(right_channel_signal, (0, left_channel_signal.shape[0] - right_channel_signal.shape[0]), 'constant')

    stereo_signal = np.stack((left_channel_signal, right_channel_signal), axis=1)

    return stereo_signal, fs


def export_wave_file(audio_file, fs, export_path):
    with wave.open(export_path, 'wb') as output_wav:
        output_wav.setparams((2, 2, fs, len(audio_file), 'NONE', 'not compressed'))
        output_wav.writeframes(audio_file.astype(np.int16))


def play_audio(audio_file):
    sd.play(audio_file)


def stop_audio():
    sd.stop()


def run_in_new_thread(func):
    def wrapper(*args, **kwargs):
        thread = th.Thread(target=func, args=args, kwargs=kwargs)
        thread.start()
        return thread
    return wrapper

