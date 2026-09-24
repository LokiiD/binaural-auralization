\# Binaural Auralization (Outdoot \& Indoor)



A Python-based framework for 3D spatial audio rendering, designed to simulate both outdoor dynamic events (e.g., microscopic vehicle pass-by) and indoor architectural acoustics. 



This project leverages \*\*HRTF (Head-Related Transfer Functions)\*\* via the SOFA standard and \*\*Hybrid Room Acoustics\*\* (Image-Source Method + Ray Tracing) to generate highly realistic, perceptually accurate binaural audio for soundscape evaluation and acoustic research.



\## Features

\- \*\*Outdoor Pass-by Simulation:\*\* Dynamic 3D trajectory mapping of a moving point source, including $1/r$ geometric attenuation.

\- \*\*Indoor Architectural Acoustics:\*\* Shoebox room modeling with frequency-dependent material absorption coefficients.

\- \*\*Hybrid Binaural Rendering:\*\* Seamless integration of directional HRIR spatialization with calculated Room Impulse Responses (BRIR synthesis).

\- \*\*Overlap-Add Convolution:\*\* Efficient block-based signal processing for moving sources in real-time length.



\## Repository Structure

The project is modular, allowing for isolated testing of spatial and architectural parameters:



\* `buss\_core.py`: Simulates a dynamic outdoor pass-by event (e.g., a single vehicle traversing the listening point).

\* `buss\_indoor.py`: Generates the RIR (Room Impulse Response) of a custom shoebox room based on material absorption.

\* `buss\_3d\_room.py`: Combines SOFA HRTF spatialization (static source) with the computed room reverberation.

\* `buss\_dynamic\_room.py`: The complete hybrid engine. A moving sound source traverses a defined 3D trajectory within a reverberant room, combining dynamic HRTF convolution with the architectural RIR.



\## Prerequisites \& Installation

This project requires Python 3.2 and the following scientific libraries:



```bash



pip install -r requirements.txt



```bash



\*(Main dependencies: `numpy`, `scipy`, `soundfile`, `pysofaconventions`, `pyroomacoustics`)\*



\### Datasets Required (Not included in repo)

To run the scripts, you must place the following files in the root directory:

1\. \*\*SOFA File:\*\* A valid HRTF dataset (e.g., `FABIAN\_HRIR\_measured\_HATO\_0.sofa` from TU Berlin).

2\. \*\*Dry Audio:\*\* Anechoic or completely dry mono `.wav` files (e.g., `traffic\_dry.wav`, `voce\_dry.wav`).



\## Methodology

The spatialization engine calculates the instantaneous Euclidean distance and azimuth for a moving source. The signal is framed and convolved with the nearest measured HRIR from the SOFA dataset. For indoor environments, `pyroomacoustics` simulates the early reflections and late reverberation tail based on specified surface properties, which is then convolved with the HRTF-processed direct sound.

