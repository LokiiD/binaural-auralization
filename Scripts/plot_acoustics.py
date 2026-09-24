import pyroomacoustics as pra
import matplotlib.pyplot as plt

def genera_grafici():
    print("Calcolo del modello acustico...")
    room_dim = [8, 6, 3]
    
    # Stessi materiali del progetto "stanza"
    materials = pra.make_materials(
        ceiling="acoustical_plaster_25mm", floor="carpet_cotton",
        east="gypsum_board", west="gypsum_board",
        north="glass_window", south="wooden_door"
    )
    
    stanza = pra.ShoeBox(room_dim, fs=44100, materials=materials, max_order=15)
    stanza.add_source([6.0, 5.0, 1.5])
    stanza.add_microphone_array(pra.MicrophoneArray([[4.0], [3.0], [1.5]], stanza.fs))
    stanza.compute_rir()

    rir = stanza.rir[0][0]

    plt.figure(figsize=(10, 4))
    plt.plot(rir, color='#1f77b4', linewidth=0.8)
    
    plt.title("Room Impulse Response (RIR) - Stanza ", fontsize=14, fontweight='bold')
    plt.xlabel("Campioni", fontsize=11)
    plt.ylabel("Ampiezza", fontsize=11)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    
    file_output = '..\Media\rir_plot.png'
    plt.savefig(file_output, dpi=300)
    print(f"Grafico generato con successo: {file_output}")

if __name__ == "__main__":
    genera_grafici()