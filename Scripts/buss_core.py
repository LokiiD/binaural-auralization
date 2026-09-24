import numpy as np
import soundfile as sf
from scipy.signal import fftconvolve
import pysofaconventions

def get_hrir(sofa, azimuth, elevation):
    positions = sofa.getVariableValue('SourcePosition')
    azimuths = positions[:, 0]
    elevations = positions[:, 1]
    
    # Correzione matematica per la distanza sferica (es. tra 359° e 0°)
    diff_azimut = np.abs(azimuths - azimuth)
    diff_azimut = np.minimum(diff_azimut, 360 - diff_azimut)
    
    distances = np.sqrt(diff_azimut**2 + (elevations - elevation)**2)
    idx = np.argmin(distances)
    
    ir_data = sofa.getVariableValue('Data.IR')
    return ir_data[idx, 0, :], ir_data[idx, 1, :]

def main_dynamic():
    input_audio = '..\Media\traffic_dry.wav'
    sofa_file = '..\Media\FABIAN_HRIR_measured_HATO_0.sofa' # Verifica sempre il nome!
    output_audio = '..\Media\traffic_passby_dynamic.wav'
    
    durata_simulazione = 10.0  
    velocita_kmh = 50.0        
    velocita_ms = velocita_kmh / 3.6
    distanza_minima = 5.0      
    
    print("Caricamento risorse...")
    audio, sr = sf.read(input_audio)
    
    # Se audio è stereo, fa una media esatta dei canali per evitare asimmetrie
    if len(audio.shape) > 1:
        audio = (audio[:, 0] + audio[:, 1]) / 2.0
        
    # Taglio o loop per avere 10 secondi di audio
    campioni_necessari = int(durata_simulazione * sr)
    if len(audio) < campioni_necessari:
        ripetizioni = int(np.ceil(campioni_necessari / len(audio)))
        audio = np.tile(audio, ripetizioni)
    audio = audio[:campioni_necessari]
        
    sofa = pysofaconventions.SOFAFile(sofa_file, 'r')
    
    frame_size = 2048
    num_frames = len(audio) // frame_size
    
    binaural_left = np.zeros(len(audio) + frame_size * 2)
    binaural_right = np.zeros(len(audio) + frame_size * 2)
    
    print(f"Simulazione pass-by in corso ({durata_simulazione}s a {velocita_kmh} km/h)...")
    
    # Posizione di partenza per far incrociare il centro esattamente a 5 secondi
    posizione_x_iniziale = (velocita_ms * (durata_simulazione / 2)
    
    for i in range(num_frames):
        inizio = i * frame_size
        fine = inizio + frame_size
        frame_audio = audio[inizio:fine]
        
        tempo_corrente = i * (frame_size / sr)
        x_corrente = posizione_x_iniziale - (velocita_ms * tempo_corrente)
        
        angolo_rad = np.arctan2(x_corrente, distanza_minima)
        azimut = np.degrees(angolo_rad)
        if azimut < 0:
            azimut += 360
            
        hrir_sx, hrir_dx = get_hrir(sofa, azimut, elevation=0.0)
        
        # 1/r Attenuazione fisica
        distanza_reale = np.sqrt(x_corrente**2 + distanza_minima**2)
        fattore_attenuazione = distanza_minima / distanza_reale
        frame_audio_attenuato = frame_audio * fattore_attenuazione
        
        # Convoluzione
        frame_sx = fftconvolve(frame_audio_attenuato, hrir_sx, mode='full')
        frame_dx = fftconvolve(frame_audio_attenuato, hrir_dx, mode='full')
        
        binaural_left[inizio:inizio+len(frame_sx)] += frame_sx
        binaural_right[inizio:inizio+len(frame_dx)] += frame_dx
        
        if i % int(sr/frame_size) == 0:
            print(f"Tempo {tempo_corrente:.1f}s | Azimut: {azimut:.1f}° | Dist: {distanza_reale:.1f}m")

    print("Assemblaggio e normalizzazione in corso...")
    segnale_binaurale = np.vstack((binaural_left, binaural_right)).T
    
    picco_max = np.max(np.abs(segnale_binaurale))
    if picco_max > 0:
        segnale_binaurale /= picco_max
    
    sf.write(output_audio, segnale_binaurale, sr)
    print(f"Finito! Simulazione salvata come: {output_audio}")

if __name__ == "__main__":
    main_dynamic()