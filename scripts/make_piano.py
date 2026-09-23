#!/usr/bin/env python3
"""Halloween-ish suspense piano bed: A-minor, slow bass + sparse eerie melody."""
import numpy as np, wave, struct

SR = 44100
BAR = 4.0
BARS = 14
DUR = BAR * BARS  # 56 s

def midi(m):
    return 440.0 * 2 ** ((m - 69) / 12.0)

def piano_note(t0, freq, dur, tau, amp, B=0.0002, sr=SR):
    n = int(dur * sr)
    t = np.arange(n) / sr
    sig = np.zeros(n)
    for k in range(1, 7):
        fk = k * freq * np.sqrt(1 + B * k * k)
        sig += (1.0 / (k ** 1.6)) * np.sin(2 * np.pi * fk * t)
    sig *= np.exp(-t / tau)
    # hammer tick
    tick = int(0.008 * sr)
    sig[:tick] += 0.25 * np.random.randn(tick) * np.exp(-np.arange(tick) / (0.003 * sr))
    env = np.minimum(1.0, t / 0.005)  # 5 ms attack
    return t0, amp * sig * env

# chord roots per bar (midi): Am Am F F Dm Dm E E Am Am F E Am Am
roots = [33, 33, 29, 29, 38, 38, 40, 40, 33, 33, 29, 40, 33, 33]
# sparse melody (midi, None = rest)
melody = [76, None, 72, None, 74, 77, 75, None, 76, 69, 72, 71, 69, 76]

mix = np.zeros(int(DUR * SR) + SR)

def add(t0, freq, dur, tau, amp):
    _, sig = piano_note(t0, freq, dur, tau, amp)
    i = int(t0 * SR)
    j = min(len(mix), i + len(sig))
    mix[i:j] += sig[: j - i]

for i, r in enumerate(roots):
    t = i * BAR
    f = midi(r)
    add(t, f, 3.8, 2.6, 0.50)          # bass root
    add(t + 2.0, f * 2 ** (7 / 12), 2.0, 2.2, 0.30)  # fifth, beat 3
    add(t, f / 2, 3.8, 3.0, 0.16)      # sub dread
    m = melody[i]
    if m:
        add(t + 0.5, midi(m), 3.5, 3.2, 0.34)  # eerie high line

# fades
n = len(mix)
fi = int(2 * SR); fo = int(4 * SR)
mix[:fi] *= np.linspace(0, 1, fi)
mix[-fo:] *= np.linspace(1, 0, fo)
mix /= max(1e-6, np.abs(mix).max())
mix *= 0.75

# stereo: slight Haas delay on right
d = int(0.012 * SR)
st = np.stack([mix, np.concatenate([np.zeros(d), mix])[:n] * 0.85], axis=1)
pcm = (np.clip(st, -1, 1) * 32767).astype(np.int16)
with wave.open('/home/hatch/workspace/your_files/phantom-shorts/halloween-piano-dry.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print("WROTE dry wav", n / SR, "s")
