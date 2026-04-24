#!/usr/bin/env python3
"""
Generate graphs showing G1GC rates and CPU usage increasing sharply
in the minutes leading up to a JVM crash, typical of an Elasticsearch
node experiencing memory pressure and eventual OOM / circuit-breaker
exhaustion.

Usage:
    python3 gc_crash_analysis.py          # writes gc_crash_analysis.png
"""

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
from datetime import datetime, timedelta

np.random.seed(42)

# ---------------------------------------------------------------------------
# Simulated timeline: 30 minutes of data, crash at T+30 min
# ---------------------------------------------------------------------------
DURATION_MIN = 30
SAMPLE_HZ = 1  # one sample per second
n_samples = DURATION_MIN * 60 * SAMPLE_HZ
t_seconds = np.arange(n_samples)
t_minutes = t_seconds / 60.0

crash_time = datetime(2026, 4, 24, 14, 30, 0)
timestamps = [crash_time - timedelta(minutes=DURATION_MIN) + timedelta(seconds=int(s)) for s in t_seconds]

# ---------------------------------------------------------------------------
# G1GC young-gen pause rate (pauses/sec, smoothed to ~per-10s buckets)
# ---------------------------------------------------------------------------
gc_base = 0.05 + 0.02 * np.random.randn(n_samples)
gc_ramp = np.where(
    t_minutes < 20,
    0,
    np.exp((t_minutes - 20) / 3.0) * 0.04,
)
gc_rate = np.clip(gc_base + gc_ramp, 0, None)

bucket = 10
gc_rate_smooth = np.convolve(gc_rate, np.ones(bucket) / bucket, mode="same")

# ---------------------------------------------------------------------------
# G1GC old-gen (mixed / full) collection rate
# ---------------------------------------------------------------------------
old_gc_base = 0.002 * np.abs(np.random.randn(n_samples))
old_gc_ramp = np.where(
    t_minutes < 22,
    0,
    np.exp((t_minutes - 22) / 2.5) * 0.03,
)
old_gc_rate = np.clip(old_gc_base + old_gc_ramp, 0, None)
old_gc_rate_smooth = np.convolve(old_gc_rate, np.ones(bucket) / bucket, mode="same")

# ---------------------------------------------------------------------------
# Total GC pause time ratio (fraction of wall-clock spent in STW pauses)
# ---------------------------------------------------------------------------
pause_base = 0.01 + 0.005 * np.random.randn(n_samples)
pause_ramp = np.where(
    t_minutes < 20,
    0,
    np.exp((t_minutes - 20) / 2.8) * 0.02,
)
pause_ratio = np.clip(pause_base + pause_ramp, 0, 1)
pause_ratio_smooth = np.convolve(pause_ratio, np.ones(bucket) / bucket, mode="same")

# ---------------------------------------------------------------------------
# CPU usage (%)
# ---------------------------------------------------------------------------
cpu_base = 15 + 5 * np.sin(t_minutes / 4) + 3 * np.random.randn(n_samples)
cpu_ramp = np.where(
    t_minutes < 18,
    0,
    np.exp((t_minutes - 18) / 3.5) * 2.5,
)
cpu_usage = np.clip(cpu_base + cpu_ramp, 0, 100)
cpu_smooth = np.convolve(cpu_usage, np.ones(bucket) / bucket, mode="same")

# ---------------------------------------------------------------------------
# Heap occupancy (%)
# ---------------------------------------------------------------------------
heap_base = 45 + 5 * np.sin(t_minutes / 3) + 2 * np.random.randn(n_samples)
heap_ramp = np.where(
    t_minutes < 18,
    0,
    (t_minutes - 18) ** 2 * 0.35,
)
heap_usage = np.clip(heap_base + heap_ramp, 0, 100)
heap_smooth = np.convolve(heap_usage, np.ones(bucket) / bucket, mode="same")

# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------
fig, axes = plt.subplots(4, 1, figsize=(14, 16), sharex=True)
fig.patch.set_facecolor("#f8f8f8")

crash_min = DURATION_MIN
danger_start = 20  # approx where metrics begin ramping

colors = {
    "young_gc": "#2196F3",
    "old_gc": "#FF5722",
    "pause": "#9C27B0",
    "cpu": "#E91E63",
    "heap": "#4CAF50",
    "danger": "#FFF3E0",
    "crash": "#D32F2F",
}

for ax in axes:
    ax.set_facecolor("white")
    ax.axvspan(danger_start, crash_min, color=colors["danger"], alpha=0.35, zorder=0)
    ax.axvline(crash_min, color=colors["crash"], linewidth=2, linestyle="--", label="CRASH", zorder=5)
    ax.grid(True, alpha=0.3, linewidth=0.5)
    ax.tick_params(labelsize=10)

# --- Panel 1: Young-gen GC rate ---
ax1 = axes[0]
ax1.fill_between(t_minutes, gc_rate_smooth, alpha=0.15, color=colors["young_gc"])
ax1.plot(t_minutes, gc_rate_smooth, color=colors["young_gc"], linewidth=1.5, label="Young-gen pauses/sec")
ax1.set_ylabel("Young-Gen GC\nPauses / sec", fontsize=11, fontweight="bold")
ax1.legend(loc="upper left", fontsize=9)
ax1.set_title("G1GC Young-Generation Collection Rate", fontsize=12, fontweight="bold", pad=8)

# --- Panel 2: Old-gen / mixed GC rate ---
ax2 = axes[1]
ax2.fill_between(t_minutes, old_gc_rate_smooth, alpha=0.15, color=colors["old_gc"])
ax2.plot(t_minutes, old_gc_rate_smooth, color=colors["old_gc"], linewidth=1.5, label="Old-gen (mixed/full) pauses/sec")
ax2.set_ylabel("Old-Gen GC\nPauses / sec", fontsize=11, fontweight="bold")
ax2.legend(loc="upper left", fontsize=9)
ax2.set_title("G1GC Old-Generation / Full-GC Collection Rate", fontsize=12, fontweight="bold", pad=8)

# --- Panel 3: STW pause ratio ---
ax3 = axes[2]
ax3.fill_between(t_minutes, pause_ratio_smooth * 100, alpha=0.15, color=colors["pause"])
ax3.plot(t_minutes, pause_ratio_smooth * 100, color=colors["pause"], linewidth=1.5, label="% wall-clock in STW pauses")
ax3.set_ylabel("GC Pause\nTime %", fontsize=11, fontweight="bold")
ax3.legend(loc="upper left", fontsize=9)
ax3.set_title("Stop-The-World Pause Time Ratio", fontsize=12, fontweight="bold", pad=8)

# --- Panel 4: CPU & Heap ---
ax4 = axes[3]
ax4_heap = ax4.twinx()

ln1 = ax4.plot(t_minutes, cpu_smooth, color=colors["cpu"], linewidth=1.8, label="CPU %")
ax4.fill_between(t_minutes, cpu_smooth, alpha=0.10, color=colors["cpu"])

ln2 = ax4_heap.plot(t_minutes, heap_smooth, color=colors["heap"], linewidth=1.8, linestyle="-", label="Heap occupancy %")
ax4_heap.fill_between(t_minutes, heap_smooth, alpha=0.10, color=colors["heap"])

ax4.set_ylabel("CPU Usage %", fontsize=11, fontweight="bold", color=colors["cpu"])
ax4_heap.set_ylabel("Heap Occupancy %", fontsize=11, fontweight="bold", color=colors["heap"])
ax4.set_xlabel("Minutes before crash", fontsize=12, fontweight="bold")
ax4.set_title("CPU Usage & JVM Heap Occupancy", fontsize=12, fontweight="bold", pad=8)

lns = ln1 + ln2
labs = [l.get_label() for l in lns]
ax4.legend(lns, labs, loc="upper left", fontsize=9)

ax4.set_xlim(0, DURATION_MIN)
ax4.xaxis.set_major_locator(ticker.MultipleLocator(5))
ax4.xaxis.set_minor_locator(ticker.MultipleLocator(1))

ax4.set_xlabel("Time (minutes from T-30 to crash at T+0)", fontsize=12, fontweight="bold")
fixed_ticks = np.arange(0, DURATION_MIN + 1, 5)
ax4.set_xticks(fixed_ticks)
xtick_labels = [f"T-{DURATION_MIN - int(x)}" if x < DURATION_MIN else "CRASH" for x in fixed_ticks]
ax4.set_xticklabels(xtick_labels)

# ---------------------------------------------------------------------------
# Annotations
# ---------------------------------------------------------------------------
for ax in axes[:3]:
    ymin, ymax = ax.get_ylim()
    ax.annotate(
        "Danger zone\n(memory pressure)",
        xy=(25, ymax * 0.85),
        fontsize=9,
        color="#BF360C",
        fontstyle="italic",
        ha="center",
    )

ax4.annotate(
    "CRASH",
    xy=(crash_min, ax4.get_ylim()[1] * 0.92),
    fontsize=11,
    color=colors["crash"],
    fontweight="bold",
    ha="right",
)

fig.suptitle(
    "Elasticsearch Node — G1GC & CPU Metrics Leading Up to Crash",
    fontsize=15,
    fontweight="bold",
    y=0.995,
)

fig.tight_layout(rect=[0, 0, 1, 0.97])

out_path = "/opt/cursor/artifacts/screenshots/gc_crash_analysis.png"
import os
os.makedirs(os.path.dirname(out_path), exist_ok=True)
fig.savefig(out_path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
print(f"Saved to {out_path}")

local_path = "gc_crash_analysis.png"
fig.savefig(local_path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
print(f"Also saved to {local_path}")
