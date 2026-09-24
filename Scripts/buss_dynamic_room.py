import numpy as np
import soundfile as sf
from scipy.signal import fftconvolve
import pysofaconventions
import pyroomacoustics as pra

def get_hrir(sofa, azimuth, elevation):
    positions = sofa.getVariableValue('SourcePosition')
    azimuths = positions[:, 0]
    elevations = positions[:, 1]
    
    diff_azimut = np.abs(azimuths - azimuth)
    diff_azimut = np.minimum(diff_azimut, 360 - diff_azimut)
    distances = np.sqrt(diff_azimut**2 + (elevations - elevation)**2)
    idx = np.argmin(distances)
    
    ir_data = sofa.getVariableValue('Data.IR')
    return ir_data[idx, 0, :], ir_data[idx, 1, :]

def main_dynamic_room():
    input_audio = '..\Media\voce_dry.wav'
    sofa_file = '..\Media\FABIAN_HRIR_measured_HATO_0.sofa'
    output_audio = '..\Media\voce_dinamica_stanza.wav'
    
    print("1. Caricamento audio originale...")
    audio, sr = sf.read(input_audio)
    if len(audio.shape) > 1: audio = (audio[:, 0] + audio[:, 1]) / 2.0
    
    # Calcolo della velocità della sorgente
    durata_audio = len(audio) / sr
    x_iniziale = 1.0
    x_finale = 7.0
    spazio_totale = x_finale - x_iniziale
    velocita_ms = spazio_totale / durata_audio 
    
    print(f"   -> Durata file: {durata_audio:.1f} sec. La persona camminerà a {velocita_ms:.2f} m/s.")

    print("2. Spazializzazione HRTF dinamica...")
    sofa = pysofaconventions.SOFAFile(sofa_file, 'r')
    frame_size = 2048
    num_frames = len(audio) // frame_size

    binaural_left = np.zeros(len(audio) + frame_size * 2)
    binaural_right = np.zeros(len(audio) + frame_size * 2)

    mic_pos = np.array([4.0, 3.0, 1.5]) 
    y_sorgente = 5.0 
    
    for i in range(num_frames):
        inizio = i * frame_size
        fine = inizio + frame_size
        frame_audio = audio[inizio:fine]

        tempo = i * (frame_size / sr)
        x_corrente = x_iniziale + (velocita_ms * tempo)
        if x_corrente > x_finale: x_corrente = x_finale

        dx = x_corrente - mic_pos[0]
        dy = y_sorgente - mic_pos[1]
        distanza = np.sqrt(dx**2 + dy**2)

        # Trigonometria manichino SOFA
        azimut_rad = np.arctan2(-dx, dy)
        azimut_deg = np.degrees(azimut_rad)
        if azimut_deg < 0: azimut_deg += 360

        hrir_sx, hrir_dx = get_hrir(sofa, azimut_deg, elevation=0.0)
        
        attenuazione = 1.0 / max(distanza, 1.0)
        frame_attenuato = frame_audio * attenuazione

        frame_sx = fftconvolve(frame_attenuato, hrir_sx, mode='full')
        frame_dx = fftconvolve(frame_attenuato, hrir_dx, mode='full')

        binaural_left[inizio:inizio+len(frame_sx)] += frame_sx
        binaural_right[inizio:inizio+len(frame_dx)] += frame_dx
        
        if i % (int(sr/frame_size) * 2) == 0:
            print(f"   -> Tempo {tempo:.1f}s | X: {x_corrente:.1f}m | Azimut: {azimut_deg:.1f}°")

    print("3. Generazione del campo riverberante architettonico...")
    room_dim = [8, 6, 3]
    materials = pra.make_materials(
        ceiling="acoustical_plaster_25mm", floor="carpet_cotton",
        east="gypsum_board", west="gypsum_board",
        north="glass_window", south="wooden_door"
    )
    stanza = pra.ShoeBox(room_dim, fs=sr, materials=materials, max_order=10)

    stanza.add_source([4.0, 5.0, 1.5], signal=np.array([1.0]))
    stanza.add_microphone_array(pra.MicrophoneArray(np.array([[4.0], [3.0], [1.5]]), sr))
    stanza.compute_rir()
    rir_stanza = stanza.rir[0][0]

    print("4. Fusione del movimento con il riverbero...")
    finale_sx = fftconvolve(binaural_left, rir_stanza, mode='full')
    finale_dx = fftconvolve(binaural_right, rir_stanza, mode='full')

    segnale_binaurale = np.vstack((finale_sx, finale_dx)).T
    segnale_binaurale /= np.max(np.abs(segnale_binaurale))

    sf.write(output_audio, segnale_binaurale, sr)
    print(f"Completato! Audio salvato in: {output_audio}")

if __name__ == "__main__":
    main_dynamic_room()