import numpy as np
import soundfile as sf
import pyroomacoustics as pra
import os

def main_indoor():
    # CONFIGURAZIONE AUDIO E STANZA
    audio_input = '..\Media\voce_dry.wav'  
    audio_output = '..\Media\indoor_auralization.wav'
    
    # File audio e la stanza devono avere lo stesso Sampling Rate
    audio_segnale, sr = sf.read(audio_input)
    if len(audio_segnale.shape) > 1:
        audio_segnale = (audio_segnale[:, 0] + audio_segnale[:, 1]) / 2.0
        
    print("Creazione della geometria della stanza...")
    
    # [Lunghezza(X), Larghezza(Y), Altezza(Z)] in metri
    room_dim = [8, 6, 3] 
    
    # Definizione dei materiali
    materials = pra.make_materials(
        ceiling="acoustical_plaster_25mm",
        floor="carpet_cotton",
        east="gypsum_board",
        west="gypsum_board",
        north="glass_window",
        south="wooden_door"
    )
    
    # MODELLO ---
    max_order = 10
    
    stanza = pra.ShoeBox(
        room_dim, 
        fs=sr, 
        materials=materials, 
        max_order=max_order,
        ray_tracing=True,
        air_absorption=True
    )
    
    # POSIZIONAMENTO
    # Sorgente sonora (es. a 2 metri dal muro X, al centro della stanza, altezza 1.5m)
    source_pos = [2.0, 3.0, 1.5]
    stanza.add_source(source_pos, signal=audio_segnale)
    
    # Ascoltatore (es. a 6 metri dal muro X)
    mic_pos = np.array([[6.0], [3.0], [1.7]])
    
    print("Posizionamento del microfono binaurale (simulazione HRTF interna)...")
    # Microfono direzionale binaurale (KEMAR integrato in PRA) puntato verso la sorgente
    # Calcolo il vettore di direzione verso la sorgente 
    direzione = source_pos - mic_pos.flatten()
    direzione_orizzontale = np.array([direzione[0], direzione[1]])
    azimut_testa = np.degrees(np.arctan2(direzione_orizzontale[1], direzione_orizzontale[0]))
    
    binaural_mic = pra.MicrophoneArray(mic_pos, stanza.fs)
    
    stanza.add_microphone_array(binaural_mic)
    
    # Calcolo della risposta e convoluzione
    print("Calcolo della risposta all'impulso della stanza e convoluzione...")
    
    # Calcola le riflessioni tramite ISM
    stanza.image_source_model()
    
    # Calcola la coda del riverbero con Ray Tracing
    stanza.ray_tracing()
    
    # Calcola la Risposta all'Impulso totale (RIR)
    stanza.compute_rir()
    
    # Convolve l'audio di input con la stanza creata
    stanza.simulate()
    
    print("Esportazione audio...")
    audio_risultante = stanza.mic_array.signals.T # Trasponiamo per avere il formato atteso
    
    # Normalizzazione
    audio_risultante /= np.max(np.abs(audio_risultante))
    
    sf.write(audio_output, audio_risultante, sr)
    print(f"Finito! Ascolta l'audio auralizzato in: {audio_output}")

if __name__ == "__main__":
    main_indoor()