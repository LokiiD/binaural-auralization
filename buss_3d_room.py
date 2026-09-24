import numpy as np
import soundfile as sf
from scipy.signal import fftconvolve
import pysofaconventions
import pyroomacoustics as pra

def get_hrir(sofa, azimuth, elevation):
    """Estrae i filtri spaziali dal dataset SOFA per un dato angolo."""
    positions = sofa.getVariableValue('SourcePosition')
    azimuths = positions[:, 0]
    elevations = positions[:, 1]
    
    diff_azimut = np.abs(azimuths - azimuth)
    diff_azimut = np.minimum(diff_azimut, 360 - diff_azimut)
    distances = np.sqrt(diff_azimut**2 + (elevations - elevation)**2)
    idx = np.argmin(distances)
    
    ir_data = sofa.getVariableValue('Data.IR')
    return ir_data[idx, 0, :], ir_data[idx, 1, :]

def main_3d_room():
    # CONFIGURAZIONE FILE
    input_audio = 'voce_dry.wav'
    sofa_file = 'FABIAN_HRIR_measured_HATO_0.sofa'
    output_audio = 'voce_binaurale_stanza.wav'
    
    print("1. Caricamento audio...")
    audio, sr = sf.read(input_audio)
    if len(audio.shape) > 1: audio = (audio[:, 0] + audio[:, 1]) / 2.0
        
    # GEOMETRIA DELLA STANZA
    print("2. Costruzione della stanza virtuale...")
    room_dim = [8, 6, 3]
    source_pos = [6.0, 5.0, 1.5]  # Sorgente in un angolo
    mic_pos = np.array([[4.0], [3.0], [1.5]])  # Ascoltatore al centro
    
    # Calcolo dell'angolo per il database SOFA
    dx = source_pos[0] - mic_pos[0][0]
    dy = source_pos[1] - mic_pos[1][0]
    azimut_rad = np.arctan2(dy, dx)
    azimut_deg = np.degrees(azimut_rad)
    if azimut_deg < 0: azimut_deg += 360
    
    print(f"   -> Sorgente rilevata a {azimut_deg:.1f} gradi rispetto all'ascoltatore.")

    # SPAZIALIZZAZIONE HRTF (SUONO DIRETTO)
    print("3. Applicazione filtri HRTF (SOFA)...")
    sofa = pysofaconventions.SOFAFile(sofa_file, 'r')
    hrir_sx, hrir_dx = get_hrir(sofa, azimut_deg, elevation=0.0)
    
    audio_3d_sx = fftconvolve(audio, hrir_sx, mode='same')
    audio_3d_dx = fftconvolve(audio, hrir_dx, mode='same')

    # RIVERBERO ARCHITETTONICO (PYROOMACOUSTICS)
    print("4. Calcolo del riverbero della stanza...")
    materials = pra.make_materials(
        ceiling="acoustical_plaster_25mm",
        floor="carpet_cotton",
        east="gypsum_board", west="gypsum_board",
        north="glass_window", south="wooden_door"
    )
    
    stanza = pra.ShoeBox(room_dim, fs=sr, materials=materials, max_order=10)
    
    # Uso un impulso fittizio per estrarre la RIR 
    stanza.add_source(source_pos, signal=np.array([1.0])) 
    stanza.add_microphone_array(pra.MicrophoneArray(mic_pos, sr))
    stanza.compute_rir()
    
    # Estraiamo la RIR della stanza
    rir_stanza = stanza.rir[0][0]

    # CONVOLUZIONE BINAURALE + RIVERBERO
    print("5. Immersione dell'audio 3D nella stanza...")
    finale_sx = fftconvolve(audio_3d_sx, rir_stanza, mode='full')
    finale_dx = fftconvolve(audio_3d_dx, rir_stanza, mode='full')
    
    # Normalizzazione ed esportazione
    segnale_binaurale = np.vstack((finale_sx, finale_dx)).T
    segnale_binaurale /= np.max(np.abs(segnale_binaurale))
    
    sf.write(output_audio, segnale_binaurale, sr)
    print(f"Completato! File salvato come: {output_audio}")

if __name__ == "__main__":
    main_3d_room()