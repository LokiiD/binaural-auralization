import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import soundfile as sf
import os

FIG_SIZE = (10, 5.625)
DPI = 300

def plot_mono_dry():
    plt.figure(figsize=FIG_SIZE)
    if os.path.exists('voce_dry.wav'):
        audio, sr = sf.read('voce_dry.wav')
        if len(audio.shape) > 1: audio = audio[:, 0]
        time = np.linspace(0, len(audio)/sr, num=len(audio))
    else:
        time = np.linspace(0, 5, 1000)
        audio = np.sin(2 * np.pi * 5 * time) * np.exp(-time)
        
    plt.plot(time, audio, color='#555555', linewidth=0.5, alpha=0.8)
    plt.title("Dry Mono Audio Signal", fontsize=18, fontweight='bold', color='#333333')
    plt.xlabel("Time (s)", fontsize=12)
    plt.ylabel("Amplitude", fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.4)
    plt.tight_layout()
    plt.savefig('bg_1_mono.png', dpi=DPI, facecolor='white')
    plt.close()

def plot_outdoor():
    plt.figure(figsize=FIG_SIZE)
    plt.scatter(0, 0, color='#1f77b4', s=300, label='Listener', zorder=5)
    
    plt.plot([-15, 15], [5, 5], color='#d62728', linestyle='--', linewidth=2.5, label='Source Trajectory')
    plt.arrow(-8, 5, 4, 0, head_width=1.2, head_length=1.5, fc='#d62728', ec='#d62728', zorder=4)
    plt.arrow(4, 5, 4, 0, head_width=1.2, head_length=1.5, fc='#d62728', ec='#d62728', zorder=4)
    
    plt.title("Outdoor Auralization: Dynamic Pass-by", fontsize=18, fontweight='bold', color='#333333')
    plt.xlabel("X-axis (m)", fontsize=12)
    plt.ylabel("Y-axis (m)", fontsize=12)
    plt.xlim(-20, 20)
    plt.ylim(-5, 15)
    plt.grid(True, linestyle='--', alpha=0.4)
    plt.legend(fontsize=12)
    plt.tight_layout()
    plt.savefig('bg_2_outdoor.png', dpi=DPI, facecolor='white')
    plt.close()

def plot_indoor_static():
    fig, ax = plt.subplots(figsize=FIG_SIZE)
    room = patches.Rectangle((0, 0), 8, 6, linewidth=3, edgecolor='#333333', facecolor='#f9f9f9', label='Shoebox Room (8x6m)')
    ax.add_patch(room)
    
    plt.scatter(4, 3, color='#1f77b4', s=300, label='Listener', zorder=5)
    plt.scatter(2, 5, color='#ff7f0e', s=300, label='Static Source', zorder=5)
    
    plt.plot([2, 4], [5, 3], color='#ff7f0e', linestyle='-', linewidth=2, alpha=0.8, label='Direct Sound')
    plt.plot([2, 2, 4], [5, 6, 3], color='#2ca02c', linestyle=':', linewidth=2, alpha=0.7, label='Early Reflections')
    plt.plot([2, 0, 4], [5, 4.5, 3], color='#2ca02c', linestyle=':', linewidth=2, alpha=0.7)

    plt.title("Indoor Auralization: Static Position & Room Acoustics", fontsize=18, fontweight='bold', color='#333333')
    plt.xlabel("X-axis (m)", fontsize=12)
    plt.ylabel("Y-axis (m)", fontsize=12)
    plt.xlim(-1, 9)
    plt.ylim(-1, 7)
    plt.grid(True, linestyle='--', alpha=0.4)
    plt.legend(loc='upper right', fontsize=12)
    plt.tight_layout()
    plt.savefig('bg_3_indoor_static.png', dpi=DPI, facecolor='white')
    plt.close()

def plot_indoor_dynamic():
    fig, ax = plt.subplots(figsize=FIG_SIZE)
    room = patches.Rectangle((0, 0), 8, 6, linewidth=3, edgecolor='#333333', facecolor='#f9f9f9', label='Shoebox Room (8x6m)')
    ax.add_patch(room)
    
    plt.scatter(4, 3, color='#1f77b4', s=300, label='Listener', zorder=5)
    
    plt.plot([1, 7], [5, 5], color='#d62728', linestyle='--', linewidth=2.5, label='Dynamic Trajectory')
    plt.scatter(1, 5, color='#d62728', s=150, zorder=5)
    plt.arrow(2.5, 5, 1.5, 0, head_width=0.4, head_length=0.6, fc='#d62728', ec='#d62728', zorder=4)
    plt.arrow(5.5, 5, 1.5, 0, head_width=0.4, head_length=0.6, fc='#d62728', ec='#d62728', zorder=4)
    
    plt.title("Indoor Auralization: Moving Source", fontsize=18, fontweight='bold', color='#333333')
    plt.xlabel("X-axis (m)", fontsize=12)
    plt.ylabel("Y-axis (m)", fontsize=12)
    plt.xlim(-1, 9)
    plt.ylim(-1, 7)
    plt.grid(True, linestyle='--', alpha=0.4)
    plt.legend(loc='upper right', fontsize=12)
    plt.tight_layout()
    plt.savefig('bg_4_indoor_dynamic.png', dpi=DPI, facecolor='white')
    plt.close()

if __name__ == '__main__':
    print("Generating 16:9 backgrounds...")
    plot_mono_dry()
    plot_outdoor()
    plot_indoor_static()
    plot_indoor_dynamic()
    print("All plots generated successfully!")