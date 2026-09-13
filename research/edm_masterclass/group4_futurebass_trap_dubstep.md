# Billboard EDM Masterclass: Group 4 — Future Bass, Melodic Bass, Dubstep & Trap

> **Authoritative Musicological Reference & Algorithmic Sound Design Blueprint**  
> **Specialist Domain**: Music Scholar 4 — Future Bass, Melodic Bass, Brostep, Wonky Dubstep, Drum & Bass, and Festival Trap  
> **Coverage**: Artists 61 through 80 (Flume, Illenium, San Holo, Skrillex, Diplo, DJ Snake, REZZ, Subtronics, Excision, Knife Party, Pendulum, Chase & Status, Sub Focus, Marshmello, RL Grime, Alison Wonderland, NGHTMRE, SLANDER, Seven Lions, Said The Sky)  
> **Integration**: Programmatic MIDI Generation Engines, Serum/Vital Wavetable Synthesizers, Dynamic Interlocking Bass Architectures

---

## 1. Executive Summary & Category Taxonomy

Group 4 represents the pinnacle of modern electronic music's emotional and physical dynamic range: from the tear-jerking, soaring supersaws of **Melodic Bass** and **Future Bass** (Illenium, SLANDER, Seven Lions, San Holo, Said The Sky, Flume, Marshmello) to the seismic sub-frequency kinetics of **Dubstep, Midtempo & Festival Trap** (Skrillex, Excision, Subtronics, REZZ, RL Grime, NGHTMRE, Alison Wonderland, DJ Snake, Knife Party) and the breakneck polyrhythmic speed of **Drum & Bass** (Pendulum, Chase & Status, Sub Focus).

Across the Billboard Hot 100 and Hot Dance/Electronic Songs charts, these 20 artists established definitive compositional formulas:
1. **Harmonic Architecture**: Extensive deployment of diatonic 7ths (`maj7`, `min7`), 9ths (`add9`, `maj9`, `min9`), suspended tonics (`sus2`, `sus4`), and rootless slash chords (`IV/V`, `V6`) to prevent premature emotional closure.
2. **Topline Vocal Chops & Pitch-Bent Leads**: Vocal chops transformed into monophonic lead synths via granular re-synthesis, formant shifting (+2 to +5 semitones), and aggressive portamento glides (60–120 ms).
3. **Sub-Frequency Dynamics & 808 Architecture**: Separation of clean, monophonic sine sub-bass (30–65 Hz) from heavily saturated, stereo-widened mid-frequency Reese basses and growls (150–1200 Hz), locked into half-time drum pockets (70–75 BPM feel at 140–150 BPM).
4. **Timbral Supersaw Stacks & Aggressive Sidechaining**: Detuned multi-voice supersaws (7–16 unison voices per oscillator, detuned 15–35 cents) subjected to extreme multi-band upward/downward compression (OTT at 40–80% depth) and volume-ducking envelopes (LFO Tool, VolumeShaper, Cableguys Curve) synced to quarter-note or eighth-note transients.
5. **Structural Contrast & Zero-Drop Silences**: The quintessential "Beat 4 Zero-Drop Silence"—a 500 ms vacuum of pure acoustic silence or isolated dry vocal breath immediately preceding the explosive drop downbeat.

---

## 2. Exhaustive Artist Analyses (Artists 61–80)

---

### 61. Flume

#### Top Billboard Chart Achievements
- **"Never Be Like You" (feat. Kai)**: Peak #20 Billboard Hot 100, #3 Hot Dance/Electronic Songs, RIAA 2x Platinum, APRA Song of the Year.
- **"Say It" (feat. Tove Lo)**: Peak #60 Billboard Hot 100, #5 Hot Dance/Electronic Songs, RIAA Platinum.
- **"Sleepless" (feat. Jezzabell Doran)**: Global breakthrough wonky future bass anthem; #1 on Hype Machine.
- **"The Difference" (with Toro y Moi)**: Grammy Nominee for Best Dance Recording, Billboard Dance/Electronic charting hit.

#### Harmonic Progression & Voicing
- **Signature Progression ("Never Be Like You")**: Key of Bb Major / G minor (Aeolian / Major modal mixture).
  $$	ext{Ebmaj9} \longrightarrow 	ext{Fsus4} \longrightarrow 	ext{Gm7} \longrightarrow 	ext{Bb/D}$$
  - **Roman Numerals**: $	ext{IVmaj9} - 	ext{V7sus4} - 	ext{vi7} - 	ext{I}^6$
  - **Voicing Architecture**: Open Drop-2 voicing `[Eb2, G3, D4, F4]` across bars 1–2. The major ninth ($F4$, MIDI 65) creates a tender harmonic friction against the major seventh ($D4$, MIDI 62). In Fsus4 (`[F2, Bb3, C4, F4]`), the suspended fourth holds emotional tension before dropping into Gm7 (`[G2, Bb3, D4, F4]`), evading standard V-I cadential finality.
- **Detuning & Micro-Pitch Modulations**: Flume employs dynamic pitch-envelope modulations on chord attacks (shifting +/- 15–30 cents), simulating unstable analog cassette wow-and-flutter.

#### Topline Melodic Hook & Vocal Chops
- **Granular Vocal Re-synthesis**: Vocal takes from Kai and Tove Lo are fragmented into 40–90 ms micro-grains, re-pitched over a 2-octave span, and processed through Max for Live granular delay buffers.
- **Asymmetrical Off-Grid Leads**: Leads intentionally bypass 16th-note quantization, utilizing 7-tuplet swings and unquantized pickup notes. In "Say It", the lead synth hook utilizes an automated pitch bend wheel dipping $-2$ semitones before scooping $+5$ semitones into phrase downbeats.

#### Bass Groove & Sub Dynamics
- **Wonky Off-Beat Sub**: Sine wave sub (38–52 Hz) reinforced with second harmonics through tape emulation (FabFilter Saturn, Warm Tube at 28%).
- **Drum Interlocking**: The kick drum is delayed by 18–25 ms behind the beat, yielding a signature drunken, lazy hip-hop pocket. The sub bass ducks completely beneath off-beat claps and snaps via an exponential sidechain curve with 190 ms release.

#### Timbral Profile & Synthesis
- **Wavetables & Processing**: Synplant seeds layered with Serum custom wavetables derived from vintage Prophet-5 brass.
- **OTT & Saturation**: Subtle upward compression (25% depth) paired with Soundtoys Decapitator (Style A) to preserve warm midrange dynamics without abrasive high-frequency sizzle.
- **Stereo Imaging**: Sub (<110 Hz) strictly monophonic; high percussion and granular vocal delay trails panned 100% stereo wide using Haas micro-delays (11 ms offset).

#### Structural Dynamics
- **Macro Form**: Ambient organic intro $ightarrow$ off-kilter half-time verse $ightarrow$ accelerating pitch-shifted vocal pre-chorus $ightarrow$ Beat 4.5 abrupt mute $ightarrow$ staggered drop where supersaws and wonky drums trigger asynchronously.

---

### 62. Illenium

#### Top Billboard Chart Achievements
- **"Good Things Fall Apart" (with Jon Bellion)**: #3 Hot Dance/Electronic Songs, #1 Billboard Dance/Mix Show Airplay, RIAA 2x Platinum, 43 weeks on Hot Dance chart.
- **"Takeaway" (with The Chainsmokers & Lennon Stella)**: #69 Billboard Hot 100, #3 Hot Dance/Electronic Songs, RIAA Platinum.
- **"Crashing" (feat. Bahari)**: #20 Hot Dance/Electronic Songs.
- **"Feel Something" (with Excision & I Prevail)**: #8 Hot Dance/Electronic Songs.

#### Harmonic Progression & Voicing
- **Signature Progression ("Good Things Fall Apart")**: Key of D Major.
  $$	ext{D} \longrightarrow 	ext{A} \longrightarrow 	ext{Bm7} \longrightarrow 	ext{G}$$
  - **Extended Melodic Bass Variant**: $	ext{Dadd9} \longrightarrow 	ext{Asus4} \longrightarrow 	ext{Bm7} \longrightarrow 	ext{Gmaj7}$
  - **Roman Numerals**: $	ext{I} - 	ext{V} - 	ext{vi7} - 	ext{IV}$
  - **Soprano Pedal Point**: High $F\#5$ (MIDI 78) is anchored across all four chords as a soaring, emotional common tone while bass roots move beneath (`D2 -> A2 -> B2 -> G2`).
- **Dramatic Transitions**: In "Feel Something" (Ab minor: $	ext{Abm} - 	ext{E} - 	ext{B} - 	ext{F\#}$, $	ext{i} - 	ext{VI} - 	ext{III} - 	ext{VII}$), Illenium switches abruptly from minor verse melancholy into towering major tonic lifts.

#### Topline Melodic Hook & Vocal Chops
- **Drop Vocal Lead**: Sliced vocal phrases transformed into the drop's primary melodic hook. Formant-shifted up $+3$ semitones, pitch-bent with 75 ms portamento glide, and layered directly in unison with the center supersaw layer.
- **Emotional High-Register Belt**: Topline climaxes in pre-chorus on high $A4$ / $B4$, delivered with dual chest and falsetto tracking to maximize emotional vulnerability.

#### Bass Groove & Sub Dynamics
- **Separated Sub & Reese**: Pure sine wave sub oscillator (36–52 Hz) carrying 100% of the sub energy. Layered with a stereo mid-Reese bass (saw waves detuned 16 cents, band-passed 120–750 Hz) providing warm, saturated glue beneath supersaws.
- **Drum Programming**: 140 BPM half-time dubstep/future bass beat (Kick on beat 1, acoustic-layered snare on beat 3).

#### Timbral Profile & Synthesis
- **4-Layer Supersaw Stack**:
  1. *High Air Saw*: 16 voices, detune 0.28, high-pass at 1.2 kHz, 140% stereo width.
  2. *Mid Body Saw*: 7 voices, detune 0.16, 250 Hz – 4 kHz bandpass, OTT upward compression at 55% depth.
  3. *Warmth Foundation*: Square-saw hybrid, centered mono, driven with tape saturation.
  4. *Acoustic Realism*: Strummed live acoustic guitars and felt piano layered into the chord transients.

#### Structural Dynamics
- **The Iconic 500 ms Beat 4 Vacuum**: Pre-drop builds with accelerating 16th-note snare rolls and rising pitch risers. On Beat 4.0, complete absolute silence (500 ms) except for an isolated dry vocal breath or acoustic guitar pick click. Downbeat of Beat 1 unleashes full supersaw detonation.

---

### 63. San Holo

#### Top Billboard Chart Achievements
- **"Light"**: #13 Billboard Hot Dance/Electronic Songs, RIAA Gold, over 220M Spotify streams.
- **"We Rise"**: Global breakthrough bass hit, over 160M streams, defining early future bass.
- **"One Thing"**: #27 Hot Dance/Electronic Songs.
- **"Lift Me From The Ground"**: #16 Hot Dance/Electronic Songs; album *album1* debuted at #7 Billboard Dance/Electronic Albums.

#### Harmonic Progression & Voicing
- **Signature Progression ("Light")**: Key of Db Major / Bb minor.
  $$	ext{Ebm7} \longrightarrow 	ext{Fm7} \longrightarrow 	ext{Gbmaj7} \longrightarrow 	ext{Abadd9}$$
  - **Roman Numerals**: $	ext{ii7} - 	ext{iii7} - 	ext{IVmaj7} - 	ext{Vadd9}$
  - **Harmonic Significance**: By entirely evading the tonic $	ext{I}$ chord (Db Major), the progression creates an infinite, floating yearning sensation that never resolves down to Earth.

#### Topline Melodic Hook & Vocal Chops
- **High-Octave Vocal Chops**: Formant-shifted up $+12$ semitones (one full octave) via Soundtoys Little AlterBoy, glided with an 85 ms portamento setting to swoop expressively between chord intervals.
- **Stratocaster Arpeggios**: Clean Fender Stratocaster recorded via analog direct box, processed through lush analog chorus and vintage spring reverb, performing rapid 8th-note ostinatos.

#### Bass Groove & Sub Dynamics
- **808 Slide Architecture**: Saturated 808 sub bass executing octave-up pitch glides (+12 semitones) on syncopated 16th-note offbeats.
- **Percussive Dynamics**: Snappy future trap snares layered with organic finger snaps; 32nd-note hi-hat triplet flurries with automated stereo panning.

#### Timbral Profile & Synthesis
- **The "Bitbird" Aesthetic**: Bright, shimmering acoustic-electronic fusion. Supersaws treated with analog cassette saturation (XLN Audio RC-20 Retro Color, "Magnetic" and "Wobble" modulations engaged).
- **Organic Sidechain Curves**: Volume ducking envelope utilizes a soft, rounded ramp curve rather than a harsh EDM pump, providing natural breathing space.

#### Structural Dynamics
- **Dynamic Arc**: Delicate solo electric guitar intro $ightarrow$ intimate vocal verse $ightarrow$ ascending snare roll build $ightarrow$ iconic pre-drop stutter ("I lose my mind...") $ightarrow$ shimmering melodic drop bursting with guitar and supersaw unison.

---

### 64. Skrillex

#### Top Billboard Chart Achievements
- **"Where Are Ü Now" (with Diplo & Justin Bieber)**: #8 Billboard Hot 100, #1 Hot Dance/Electronic Songs, Grammy Award for Best Dance Recording, RIAA 6x Platinum.
- **"Bangarang" (feat. Sirah)**: #72 Billboard Hot 100, #3 Hot Dance/Electronic Songs, Grammy Award Winner, RIAA 3x Platinum.
- **"Scary Monsters and Nice Sprites"**: #69 Billboard Hot 100, RIAA 2x Platinum, defined the worldwide 2010s dubstep boom.
- **"In da Ghetto" (with J Balvin)**: #2 Hot Dance/Electronic Songs.

#### Harmonic Progression & Voicing
- **"Where Are Ü Now" Pop-Trap Harmony**: Key of F# minor / A Major.
  $$	ext{F\#m} \longrightarrow 	ext{D} \longrightarrow 	ext{A} \longrightarrow 	ext{E}$$
  - **Extended Pop Voicing**: $	ext{F\#m9} - 	ext{Dmaj7} - 	ext{Aadd9} - 	ext{Esus4}$
  - **Roman Numerals**: $	ext{i} - 	ext{VI} - 	ext{III} - 	ext{VII}$
- **Aggressive Brostep Chords ("Scary Monsters")**: Key of Eb minor. Crushing power-chords alternating with half-step chromatic shifts ($	ext{Ebm} - 	ext{B} - 	ext{F\#} - 	ext{C\#}$).

#### Topline Melodic Hook & Vocal Chops
- **The "Dolphin" Vocal Lead ("Where Are Ü Now")**: Justin Bieber's dry vocal stem pitched up two full octaves (+24 semitones), processed through extreme notch EQ at 3.2 kHz, distortion, comb filtering, and stereo slap delay.
- **Vowel Formant Growls**: In "Bangarang", vocal samples ("Shout to all my lost boys!") interlock with screaming FM bass growls that sweep through vowel formants (`A - E - I - O - U`).

#### Bass Groove & Sub Dynamics
- **FM Synthesis Growls**: Native Instruments Massive / Xfer Serum FM architecture. Modulating a pure sine carrier by a wavetable at audio rate.
- **Drum Programming**: Relentless half-time 140 BPM rhythm. Kick transient equalized with high-frequency click at 4.2 kHz and sub weight at 55 Hz; snare tuned to a piercing 200 Hz fundamental with explosive white noise tail.

#### Timbral Profile & Synthesis
- **Multiband Frequency Splitting**:
  - *Sub (<100 Hz)*: Monophonic sine, brickwall limited.
  - *Mid (100 Hz – 2.5 kHz)*: Crushed via Ohmicide / FabFilter Saturn / OTT, modulated with sharp LFO notch filters.
  - *High (>2.5 kHz)*: Stereo Haas widening, dimension expander, and high-frequency exciter.

#### Structural Dynamics
- **Drop Architecture**: 8-bar build-up $ightarrow$ iconic vocal punchline sample ("Oh my God!", "Call 911 now!") on Beat 4 $ightarrow$ explosive drop downbeat with rapid 2-bar call-and-response switchbacks between FM growls and punchy acoustic drum fills.

---

### 65. Diplo

#### Top Billboard Chart Achievements
- **"Lean On" (Major Lazer & DJ Snake feat. MØ)**: #4 Billboard Hot 100, #1 Hot Dance/Electronic Songs (historic 23 weeks at #1), RIAA 4x Platinum.
- **"Where Are Ü Now" (Jack Ü)**: #8 Billboard Hot 100, Grammy Winner.
- **"Cold Water" (Major Lazer feat. Justin Bieber & MØ)**: #2 Billboard Hot 100, #1 Hot Dance/Electronic Songs.
- **"Heartless" (feat. Morgan Wallen)**: #18 Billboard Hot 100, #10 Hot Dance/Electronic Songs, RIAA 3x Platinum.

#### Harmonic Progression & Voicing
- **Core Progression ("Lean On")**: Key of G minor.
  $$	ext{Gm} \longrightarrow 	ext{Eb} \longrightarrow 	ext{Bb} \longrightarrow 	ext{F}$$
  - **Roman Numerals**: $	ext{i} - 	ext{VI} - 	ext{III} - 	ext{VII}$
- **Country-Trap Hybrid ("Heartless")**: Key of F# minor ($	ext{F\#m} - 	ext{D} - 	ext{A} - 	ext{E}$), layering Nashville acoustic guitar strums over Roland TR-808 sub basslines.

#### Topline Melodic Hook & Vocal Chops
- **"Lean On" Pitch-Bent Vocal Synth**: Sliced vocal sample converted to a sampler instrument, played with 110 ms portamento glide and rapid pitch vibrato on sustained notes.
- **Acoustic-Synthetic Earworms**: Layering organic whistling hooks, marimbas, and steel pans with bright synthetic pluck transients.

#### Bass Groove & Sub Dynamics
- **Moombahton / Dembow Trap Fusion**: 100–110 BPM groove. Kick hits on quarter notes (1, 2, 3, 4) with syncopated off-beat rimshots and snare hits (dotted-eighth and sixteenth notes).
- **Sub Dynamics**: Deep 808 sub kick sustaining across measure downbeats, ducked transparently beneath vocal formants.

#### Timbral Profile & Synthesis
- **World Percussion Textures**: Real timbales, congas, and Brazilian cuícas processed through analog tape emulation.
- **Warm Saturation**: Neve preamp and tape saturation applied to drum busses to deliver radio punch without aggressive digital clipping.

#### Structural Dynamics
- **Pop-EDM Crossover Form**: Verse $ightarrow$ Pre-Chorus $ightarrow$ Vocal Chorus $ightarrow$ Post-Chorus Instrumental Dance Drop $ightarrow$ Stripped-down Outro.

---

### 66. DJ Snake

#### Top Billboard Chart Achievements
- **"Turn Down for What" (with Lil Jon)**: #4 Billboard Hot 100, #1 Hot Dance/Electronic Songs, RIAA 6x Platinum, Billboard Music Award Winner.
- **"Let Me Love You" (feat. Justin Bieber)**: #4 Billboard Hot 100, #2 Hot Dance/Electronic Songs, RIAA 5x Platinum.
- **"Middle" (feat. Bipolar Sunshine)**: #20 Billboard Hot 100, #3 Hot Dance/Electronic Songs, RIAA 3x Platinum.

#### Harmonic Progression & Voicing
- **"Middle" Bittersweet Progression**: Key of A Major.
  $$	ext{Dmaj7} \longrightarrow 	ext{E} \longrightarrow 	ext{F\#m7} \longrightarrow 	ext{C\#m7}$$
  - **Roman Numerals**: $	ext{IVmaj7} - 	ext{V} - 	ext{vi7} - 	ext{iii7}$
  - **Voice Leading**: Starting on the major seventh subdominant ($	ext{Dmaj7}$) introduces an immediate feeling of nostalgic elevation, resolving smoothly downward through diatonic bass steps.
- **"Turn Down for What" Trap Riff**: Monophonic Eb minor pentatonic scream riff over sub drone.

#### Topline Melodic Hook & Vocal Chops
- **Formant-Shifted Cascade ("Middle")**: Male vocal chop shifted $+4$ semitones in pitch, descending the pentatonic scale ($	ext{C\#5} - 	ext{B4} - 	ext{A4} - 	ext{F\#4} - 	ext{E4}$) with tape slap delay.
- **Distorted Trap Brass ("Turn Down for What")**: Massive multi-sampled brass stabs pitch-bent $+2$ semitones into downbeats.

#### Bass Groove & Sub Dynamics
- **Mammoth 808 Sub Saturation**: In trap mode, 40–58 Hz 808 sub kicks driven through hard clippers (Sausage Fattener at 45%).
- **Smooth Reese Bass**: In "Middle", warm low-passed Reese bass (cutoff at 240 Hz) gliding smoothly between chord roots.

#### Timbral Profile & Synthesis
- **Stereo White Noise Bursts**: Snares and claps layered with wide stereo white noise. Supersaws compressed heavily with fast attack and medium release to produce a solid wall of sound.

#### Structural Dynamics
- **Pre-Drop Tension**: Sudden total silence on beat 4, accompanied only by an iconic hype shout ("Fire!", "Turn down for what!") before dropping into full sonic detonation.

---

### 67. REZZ

#### Top Billboard Chart Achievements
- **"Someone Else" (with Grabbitz)**: #16 Hot Dance/Electronic Songs, #1 US Alternative Airplay chart, RIAA certified.
- **"Sacrificial" (feat. PVRIS)**: Hot Dance/Electronic Songs chart entry, alternative radio crossover.
- **"Edge"**: Genre-defining dark midtempo bass anthem (over 80M streams).

#### Harmonic Progression & Voicing
- **Dark Phrygian Drones ("Edge")**: Key of F minor / F Phrygian.
  $$	ext{Fm} \longrightarrow 	ext{Gb} \longrightarrow 	ext{Fm}$$
  - **Roman Numerals**: $	ext{i} - lat	ext{II} - 	ext{i}$
  - **Phrygian Crunch**: The half-step $lat	ext{II}$ relationship produces an ominous, industrial tension devoid of traditional pop resolution.
- **Alternative Rock Balladry ("Someone Else")**: Key of E minor ($	ext{Em} - 	ext{C} - 	ext{G} - 	ext{D}$, $	ext{i} - 	ext{VI} - 	ext{III} - 	ext{VII}$).

#### Topline Melodic Hook & Vocal Chops
- **Clockwork Industrial Arpeggios**: 16th-note analog clockwork arpeggiations with heavy resonant low-pass filter modulation.
- **Whispered Rock Vocals**: Layering alternative rock vocalists (Grabbitz, PVRIS) with low-octave doubled whispering vocal tracks.

#### Bass Groove & Sub Dynamics
- **Midtempo 100–105 BPM Groove**: Four-on-the-floor industrial kick drum colliding with syncopated half-time mid-bass stabs.
- **Distorted Reese Growls**: Sub bass hitting 30–45 Hz paired with heavily distorted mid-frequency Reese saws (modulated notch filters, aggressive bitcrushing, and guitar amp simulation).

#### Timbral Profile & Synthesis
- **Dark Industrial Textures**: Analog synthesizer emulation (Arturia Mini V, Serum wavetables with sync modulation). Zero high-end shimmer—focus is placed entirely on gritty 200–900 Hz midrange pressure.

#### Structural Dynamics
- **Slow, Menacing Builds**: Tension built through hypnotic, ticking hi-hats and slowly opening low-pass filters $ightarrow$ beat 4 tape-stop stutter $ightarrow$ crushing midtempo drop with expansive pauses between bass impacts.

---

### 68. Subtronics

#### Top Billboard Chart Achievements
- **"GRIZTRONICS" (with GRiZ)**: #9 Hot Dance/Electronic Songs, viral festival anthem.
- **"Black Out Days" (Subtronics Remix)**: Viral Billboard Dance crossover hit, over 100M streams.
- **"Into Pieces" (with Grabbitz)**: Hot Dance/Electronic Songs chart topper.

#### Harmonic Progression & Voicing
- **Wonky Riddim Dissonance**: Tritone and chromatic intervals. Sequences shifting from root tonic to augmented 4th ($	ext{F} ightarrow 	ext{B}$), creating jarring harmonic tension.
- **Melodic Bridges ("Into Pieces")**: Emotional B minor diatonic chord sequences ($	ext{Bm} - 	ext{G} - 	ext{D} - 	ext{A}$) providing contrast against dissonant riddim drops.

#### Topline Melodic Hook & Vocal Chops
- **Viral Pre-Drop Vocal Memes**: Humorous, quirky samples ("Ooh, that's nasty!", "Hit 'em with the wonk") immediately preceding the drop downbeat.
- **High-Pitched Laser Synths**: Squelching pitch-bent leads sweeping rapidly across 3 octaves using random LFO modulators.

#### Bass Groove & Sub Dynamics
- **Riddim Half-Time Groove**: 140–145 BPM half-time beat (kick on beat 1, heavy clap/snare on beat 3). Heavy triplet swing applied to offbeat bass stabs.
- **Sub Bass Sine**: Pure 32–45 Hz sub sine wave reinforced with phase-aligned upper harmonics.

#### Timbral Profile & Synthesis
- **The "Wonk" Sound**: Serum wavetable FM modulation (FM from Osc B). Modulating wavetable position with chaotic LFO shapes, routed through comb filters, hyper-flangers, and aggressive OTT compression.

#### Structural Dynamics
- **Fakeout Drops**: Build-up accelerates into a simulated drop, cuts abruptly to dead silence or a comedic voice sample, then drops into an entirely different, unexpected bass patch. Switch-ups occur every 4 bars.

---

### 69. Excision

#### Top Billboard Chart Achievements
- **"Feel Something" (with Illenium & I Prevail)**: #8 Hot Dance/Electronic Songs.
- **"Throwin' Elbows" (with Space Laces)**: Global dubstep festival anthem.
- **"Gold (Stupid Love)" (with Illenium)**: #8 Hot Dance/Electronic Songs.
- **"Oxygen" (with Wooli & Trivecta)**: Hot Dance/Electronic hit.

#### Harmonic Progression & Voicing
- **Metalcore / Melodic Dubstep Hybrid ("Feel Something")**: Key of Ab minor.
  $$	ext{Abm} \longrightarrow 	ext{E} \longrightarrow 	ext{B} \longrightarrow 	ext{F\#}$$
  - **Roman Numerals**: $	ext{i} - 	ext{VI} - 	ext{III} - 	ext{VII}$
- **Brutal Chromaticism ("Throwin' Elbows")**: Key of F minor. Dissonant diminished and chromatic riffs revolving around the low F root.

#### Topline Melodic Hook & Vocal Chops
- **Metalcore Screams to Anthemic Clean Vocals**: Harsh screamed metal vocals during builds transitioning into soaring clean melodic choruses.
- **Metallic Screech Leads**: FM synthesis modulated at audio rate, creating harsh metallic shrieks that pierce through festival PA systems.

#### Bass Groove & Sub Dynamics
- **500,000-Watt Sub Tuning**: Sub bass calibrated for massive festival PK Sound systems (30–50 Hz sine waves hitting peak acoustic pressure).
- **Drum Programming**: 145–150 BPM half-time dubstep drums. Kick drum transient heavily clipped with soft-clipper; snare reinforced with acoustic rimshots and white noise.

#### Timbral Profile & Synthesis
- **Aggressive Distortion Chains**: FabFilter Saturn (Heavy Tube drive), iZotope Trash 2 multiband waveshaping, multi-stage OTT upward compression.

#### Structural Dynamics
- **Prehistoric Impact**: Builds featuring marching military snare rolls and sirens $ightarrow$ beat 4 zero-drop silence with vocal shout ("Throwin' elbows!") $ightarrow$ cataclysmic drop impact with alternating melodic and heavy tearout drops.

---

### 70. Knife Party

#### Top Billboard Chart Achievements
- **"Internet Friends"**: Iconic global EDM anthem.
- **"Bonfire"**: UK Top 45, Billboard Dance/Electronic digital chart topper.
- **"Antidote" (with Swedish House Mafia)**: #3 UK Singles, Billboard Dance Club Songs #1.
- **"Centipede"**: Global dubstep / drumstep classic.

#### Harmonic Progression & Voicing
- **Aggressive Minor Modes ("Bonfire")**: Key of D minor. Combines offbeat reggae skank chords ($	ext{Dm} - 	ext{Gm}$) with heavy minor-pentatonic bass riffs.
- **"Internet Friends" Harmonic Tension**: Key of F# minor. Ominous telephone ring tones and sirens creating sustained tension over pedal point F# drones.

#### Topline Melodic Hook & Vocal Chops
- **Narrative Vocal Hooks**: Text-to-speech voice samples ("You blocked me on Facebook, and now you're going to die") driving the conceptual theme.
- **Laser-Screech Synths**: Pitch-bent high-resonance synth leads with rapid envelope decays.

#### Bass Groove & Sub Dynamics
- **Drumstep / Electro Fusion**: High-tempo 175 BPM drumstep half-time grooves (snare on beat 3) alternating with 128 BPM four-on-the-floor electro-house.
- **Syncopated Mid-Bass**: Midrange growls moving in complex 16th-note syncopation around the sub bass.

#### Timbral Profile & Synthesis
- **Rob Swire Signature Sound**: Razor-sharp high frequencies, immaculate dynamic control, aggressive limiting without loss of transient punch, flanged supersaw stabs.

#### Structural Dynamics
- **Theatrical Build-Ups**: Extended cinematic builds featuring narrative voiceovers and rising pitch risers, culminating in sudden beat 4 drop pauses.

---

### 71. Pendulum

#### Top Billboard Chart Achievements
- **"Watercolour"**: UK #4, US Billboard Dance/Electronic charts.
- **"Propane Nightmares"**: UK #9, Billboard Dance charts.
- **"Tarantula"**: Historic drum and bass chart anthem.
- **"Witchcraft"**: UK Top 40, global electronic-rock crossover hit.

#### Harmonic Progression & Voicing
- **Cinematic Rock / DnB Harmony ("Watercolour")**: Key of G minor.
  $$	ext{Gm} \longrightarrow 	ext{Eb} \longrightarrow 	ext{Bb} \longrightarrow 	ext{F}$$
  - **Roman Numerals**: $	ext{i} - 	ext{VI} - 	ext{III} - 	ext{VII}$
  - **Brass Voicings**: Fanfare brass voicings in open fourths and fifths doubling the synthesizer chords.
- **"Propane Nightmares" Modal Shift**: Key of F minor ($	ext{Fm} - 	ext{Db} - 	ext{Ab} - 	ext{Eb}$), utilizing the minor pentatonic blues scale in Swire's soaring vocal topline.

#### Topline Melodic Hook & Vocal Chops
- **High-Tenor Rock Vocals**: Rob Swire's soaring, compressed rock vocals doubling synth leads at the octave.
- **Arpeggiated Brass Leads**: Staccato synth brass arpeggios ascending in diatonic thirds.

#### Bass Groove & Sub Dynamics
- **174 BPM Drum & Bass Breakbeats**: Syncopated two-step breakbeat (kick on beat 1 and 2.5, snappy acoustic snare on beats 2 and 4).
- **Rolling Reese Bass**: Multi-oscillator Reese bassline filtered with automated low-pass envelopes, creating a fluid, rolling low-end momentum.

#### Timbral Profile & Synthesis
- **Hybrid Rock-Electronic Production**: Real recorded electric guitars (heavily distorted and gate-synced to drums) layered with analog synthesizers (Access Virus TI).

#### Structural Dynamics
- **Rock Band Architecture**: Verses resemble heavy alternative rock, building into massive drum and bass drops characterized by soaring brass synths and rapid-fire breakbeats.

---

### 72. Chase & Status

#### Top Billboard Chart Achievements
- **"Baddadan" (with Bou feat. IRAH, Flowdan, Trigga, Takura)**: Global DnB revival smash, UK Top 10, Billboard Dance/Electronic charts.
- **"Disconnect" (with Becky Hill)**: UK Top 10, Billboard Dance/Electronic charts.
- **"Blind Faith"**: UK #5 Singles chart.

#### Harmonic Progression & Voicing
- **"Disconnect" Uplifting Minor Pop**: Key of A minor.
  $$	ext{Am} \longrightarrow 	ext{F} \longrightarrow 	ext{C} \longrightarrow 	ext{G}$$
  - **Roman Numerals**: $	ext{i} - 	ext{VI} - 	ext{III} - 	ext{VII}$
- **"Baddadan" Sound-System Minimalism**: Key of F# minor. Single-chord pedal drone focusing exclusively on rhythmic groove and sub-bass impact.

#### Topline Melodic Hook & Vocal Chops
- **UK Grime / Dancehall MC Toplines**: Fast-paced triplet vocal delivery from IRAH and Flowdan ("Baddadan baddadan baddadan") providing rhythmic syncopation.
- **Anthemic Female Vocals ("Disconnect")**: Becky Hill's powerful belt vocals in high register ($C5$ – $E5$).

#### Bass Groove & Sub Dynamics
- **Modern 174 BPM Roller**: Deep, distorted foghorn bass and 808-style DnB sub bass hitting on offbeats.
- **Drum Programming**: Crisp acoustic snare with heavy low-mid crack at 220 Hz and tight, punchy kick.

#### Timbral Profile & Synthesis
- **Dub & Sound-System Grit**: Spring reverb splashes, tape delay dub throws, analog preamp saturation on vocals and drums.

#### Structural Dynamics
- **Short, High-Energy Builds**: 8-bar rapid vocal builds $ightarrow$ quick 1-beat silence $ightarrow$ sudden drop into relentless drum and bass basslines.

---

### 73. Sub Focus

#### Top Billboard Chart Achievements
- **"Desire" (with Dimension)**: UK Platinum certified, Billboard Dance/Electronic charts.
- **"Solar System"**: Global dancefloor drum & bass anthem.
- **"Tidal Wave" (feat. Alpines)**: UK Top 15, global electronic smash.
- **"Ready to Fly" (with Dimension)**: UK Top 40, Billboard Dance entry.

#### Harmonic Progression & Voicing
- **Euphoric DnB Harmony ("Desire")**: Key of G# minor / B Major.
  $$	ext{G\#m} \longrightarrow 	ext{E} \longrightarrow 	ext{B} \longrightarrow 	ext{F\#}$$
  - **Roman Numerals**: $	ext{i} - 	ext{VI} - 	ext{III} - 	ext{VII}$
- **"Solar System" Uplifting Stabs**: Key of F# minor ($	ext{F\#m} - 	ext{D} - 	ext{A} - 	ext{E}$), with suspended 4th chords resolving into sparkling major chords.

#### Topline Melodic Hook & Vocal Chops
- **Trance-Inspired Piano Riffs**: Bright 90s piano house stabs transposed into 174 BPM breakbeat structures.
- **Ethereal Female Vocal Chops**: Soaring vocal phrases drenched in high-plate reverbs.

#### Bass Groove & Sub Dynamics
- **Dancefloor DnB Sub**: Pure sine wave sub bass sitting at 40–55 Hz, perfectly phase-aligned with kick drum transients.
- **Modulated Reese Leads**: Bright Reese bass with high-frequency stereo chorusing, filtered dynamically with resonance peaks.

#### Timbral Profile & Synthesis
- **High-Gloss Mixdown**: Shimmering white noise sweeps, wide detuned supersaw layers, sparkling hi-hats, and pristine mastering clarity.

#### Structural Dynamics
- **Extended Trance-Style Builds**: 16-bar soaring builds with escalating snare rolls and rising synth cutoff frequencies $ightarrow$ explosive release into rolling drum and bass.

---

### 74. Marshmello

#### Top Billboard Chart Achievements
- **"Happier" (with Bastille)**: #2 Billboard Hot 100, #1 Hot Dance/Electronic Songs (historic record: 69 weeks at #1), RIAA 6x Platinum.
- **"Silence" (feat. Khalid)**: #30 Billboard Hot 100, #1 Hot Dance/Electronic Songs, RIAA 4x Platinum.
- **"Alone"**: #60 Billboard Hot 100, #3 Hot Dance/Electronic Songs, RIAA 3x Platinum.
- **"Wolves" (with Selena Gomez)**: #20 Billboard Hot 100, #1 Hot Dance/Electronic Songs, RIAA 4x Platinum.

#### Harmonic Progression & Voicing
- **"Happier" Pop Diatonic Progression**: Key of F Major.
  $$	ext{F} \longrightarrow 	ext{Gm7} \longrightarrow 	ext{Dm} \longrightarrow 	ext{Bb}$$
  - **Roman Numerals**: $	ext{I} - 	ext{ii7} - 	ext{vi} - 	ext{IV}$
  - **Voicings**: Simple, open close-position triads and 7ths with high acoustic piano doubling.
- **"Silence" Bittersweet Ballad**: Key of B minor ($	ext{Bm} - 	ext{G} - 	ext{D} - 	ext{A}$, $	ext{vi} - 	ext{IV} - 	ext{I} - 	ext{V}$).

#### Topline Melodic Hook & Vocal Chops
- **Signature Bell/Pluck Lead**: Bright square-saw synth pluck with fast envelope decay and subtle pitch vibrato.
- **Vocal Chop Earworms**: Melodic vocal chop hooks doubled with whistling leads or synth plucks dancing in pentatonic cascades.

#### Bass Groove & Sub Dynamics
- **Bouncy Future Trap Drums**: Punchy kick drum sitting on beats 1 and 2.5; tight finger snaps and acoustic claps on beat 3; rolling 16th-note hi-hats.
- **Warm 808 Sub**: Saturated 808 bass with smooth portamento glides (70 ms) between chord roots.

#### Timbral Profile & Synthesis
- **Radio-Ready Clarity**: Minimalist frequency arrangement. No clashing midrange layers; vocal sits completely unobstructed; supersaws are polite and bright with gentle sidechain compression.

#### Structural Dynamics
- **Radio Pop Layout**: Intro (Acoustic Guitar/Piano) $ightarrow$ Verse 1 $ightarrow$ Pre-Chorus $ightarrow$ High-Energy Future Bass Drop $ightarrow$ Verse 2 $ightarrow$ Bridge $ightarrow$ Final Drop.

---

### 75. RL Grime

#### Top Billboard Chart Achievements
- **"Core"**: Legendary festival trap anthem, Billboard Dance chart staple.
- **"I Wanna Know" (feat. Daya)**: #13 Billboard Hot Dance/Electronic Songs, RIAA Gold.
- **"UCLA" (feat. 24hrs)**: RIAA Gold, Hot Dance/Electronic hit.
- **"Waiting" (with Skrillex & What So Not)**: Billboard Dance charting hit.

#### Harmonic Progression & Voicing
- **"I Wanna Know" Melodic Future Bass**: Key of Eb Major / C minor.
  $$	ext{Cm} \longrightarrow 	ext{Ab} \longrightarrow 	ext{Eb} \longrightarrow 	ext{Bb}$$
  - **Roman Numerals**: $	ext{vi} - 	ext{IV} - 	ext{I} - 	ext{V}$
  - **Voicing Analysis**: Emotional suspended chords ($	ext{Cm7} - 	ext{Abmaj7} - 	ext{Ebadd9} - 	ext{Bbsus4}$) played across wide supersaw stacks.
- **"Core" Heavy Drone**: Key of D minor. Monophonic distorted brass horn riff.

#### Topline Melodic Hook & Vocal Chops
- **"Core" Horn Scream**: Multi-sampled brass stab pitch-bent upward $+3$ semitones, paired with African tribal chant samples.
- **Soaring Pop Toplines**: Daya's emotive, belting vocals on "I Wanna Know" leading into pitch-bent vocal synth drop hooks.

#### Bass Groove & Sub Dynamics
- **Seismic 808 Glides**: Extended 808 sub bass with long decay times (2.5 seconds), executing octave-up slides (+12 semitones) on syncopated 16th-note offbeats.
- **Trap Drumming**: Heavy half-time trap groove at 75 BPM. Crisp 808 snare on beat 3; rapid-fire 32nd-note and 64th-note hi-hat triplet rolls with volume velocity ramping.

#### Timbral Profile & Synthesis
- **Cinematic Horns & Analog Saturation**: Brass stabs processed through analog saturation (Overstayer Saturator / Thermionic Culture Vulture); massive stereo supersaw walls in melodic tracks.

#### Structural Dynamics
- **Apocalyptic Builds**: Timpani rolls, rising synth brass, and escalating snare rolls building to the legendary pre-drop vocal sample: *"Who do the shit that I do?"* $ightarrow$ 500 ms beat 4 silence $ightarrow$ seismic trap drop.

---

### 76. Alison Wonderland

#### Top Billboard Chart Achievements
- **"I Want U"**: ARIA Gold, Billboard Dance/Electronic charting hit.
- **"Church"**: #35 Hot Dance/Electronic Songs, ARIA 2x Platinum.
- **"Peace"**: Billboard Hot Dance/Electronic Songs hit.
- **"Anything" (with Valentino Khan)**: Billboard Dance/Electronic entry.

#### Harmonic Progression & Voicing
- **"Church" Minor Suspension**: Key of Eb minor.
  $$	ext{Ebm} \longrightarrow 	ext{B} \longrightarrow 	ext{F\#} \longrightarrow 	ext{C\#}$$
  - **Roman Numerals**: $	ext{i} - 	ext{VI} - 	ext{III} - 	ext{VII}$
  - **Real Cello Voicings**: Acoustic cello sections recorded in close mic and layered underneath synthesizers, providing organic minor third and fifth voice leading.

#### Topline Melodic Hook & Vocal Chops
- **Personal Vocal Intimacy**: Alison's own raw, vulnerable vocals singing diaristic lyrics.
- **Screaming Pitch-Bent Leads**: Vocal chops distorted and pitch-bent with expressive glide envelopes.

#### Bass Groove & Sub Dynamics
- **Slumping Half-Time Trap**: Heavy 808 sub bass layered with crunchy acoustic kick drum transients; syncopated claps and offbeat percussion hits.

#### Timbral Profile & Synthesis
- **Classical-Electronic Collision**: Organic cellos and orchestral strings colliding with abrasive digital wavetables, bitcrushed claps, and cavernous hall reverbs.

#### Structural Dynamics
- **Dynamic Arc**: Songs open with solo acoustic cello or piano and whispered vocals $ightarrow$ intense snare crescendo $ightarrow$ drop cuts to solo 808 sub bass and vocal chop before exploding into full synth layers.

---

### 77. NGHTMRE

#### Top Billboard Chart Achievements
- **"GUD VIBRATIONS" (with SLANDER)**: RIAA Platinum, Hot Dance/Electronic Songs hit.
- **"Street"**: Breakthrough festival trap anthem.
- **"Feel Your Love" (with The Chainsmokers)**: Billboard Dance/Electronic hit.
- **"REDLIGHT" (with A$AP Ferg)**: Hot Dance/Electronic Songs hit.

#### Harmonic Progression & Voicing
- **"GUD VIBRATIONS" Uplifting Major Bass**: Key of F# Major.
  $$	ext{F\#} \longrightarrow 	ext{B} \longrightarrow 	ext{D\#m} \longrightarrow 	ext{C\#}$$
  - **Roman Numerals**: $	ext{I} - 	ext{IV} - 	ext{vi} - 	ext{V}$
  - **Voicing Analysis**: Rich $	ext{F\#add9}$ and $	ext{Bmaj7}$ chords creating a nostalgic, triumphant festival anthem feeling.
- **"Street" Metallic Trap**: Key of F minor. Atonal, metallic percussive hits replacing melodic chords.

#### Topline Melodic Hook & Vocal Chops
- **Metallic Percussive Leads**: Real pots, pans, and synthetic metallic bells tuned and sequenced as the main melodic hook.
- **Vocal Chops in Fifths**: Vocal chops harmonized in parallel perfect fifths and octaves.

#### Bass Groove & Sub Dynamics
- **Punchy Hybrid Trap**: Rapid pitch-bent 808 basslines; extremely punchy kick drums with high-frequency transient clicks that slice through dense mixes.

#### Timbral Profile & Synthesis
- **Surgical Transient Design**: Drums and leads shaped using SPL Transient Designer; multi-band distortion isolating 300–1500 Hz for maximum aggression.

#### Structural Dynamics
- **Tension Escalation**: Accelerated tempo modulations, sudden drop switches, white-noise risers paired with pitch-shifted snare rolls.

---

### 78. SLANDER

#### Top Billboard Chart Achievements
- **"Love Is Gone" (feat. Dylan Matthew)**: #13 Hot Dance/Electronic Songs, RIAA Gold, global viral melodic bass anthem (over 320M streams).
- **"All You Need To Know" (with Gryffin & Calle Lehmann)**: #12 Hot Dance/Electronic Songs, RIAA Gold.
- **"First Time" (with Seven Lions & Dabin)**: Hot Dance/Electronic Songs hit.

#### Harmonic Progression & Voicing
- **"Love Is Gone" The Ultimate Tearjerker**: Key of Db Major / Bb minor.
  $$	ext{Bbm} \longrightarrow 	ext{Gb} \longrightarrow 	ext{Db} \longrightarrow 	ext{Ab}$$
  - **Extended Voicings**: $	ext{Bbm7} \longrightarrow 	ext{Gbmaj7} \longrightarrow 	ext{Dbadd9} \longrightarrow 	ext{Absus4}$
  - **Roman Numerals**: $	ext{vi7} - 	ext{IVmaj7} - 	ext{Iadd9} - 	ext{Vsus4}$
  - **Voice Leading**: The notes $F4$ and $Ab4$ remain suspended through the entire progression, creating intense emotional longing.

#### Topline Melodic Hook & Vocal Chops
- **Dylan Matthew's Emotive Belt**: High vocal register belting reaching $Ab4$ and $Bb4$, double-tracked with falsetto harmonies.
- **Drop Supersaw Lead**: Vocal chops pitch-shifted and embedded directly within the center of soaring supersaws.

#### Bass Groove & Sub Dynamics
- **Half-Time Melodic Bass**: 140 BPM half-time groove (snare on beat 3). Low-end anchored by a pure sine sub (35–48 Hz) moving in strict unison with chord roots.
- **Reese Support**: Mid-frequency Reese bass (100–350 Hz) providing warm, saturated body beneath the chord layers.

#### Timbral Profile & Synthesis
- **The "Heaven Trap" Supersaw Wall**:
  - 6 layered instances of Serum: 16 voices per oscillator, detuned 28 cents, spread 100% in stereo field.
  - Multi-band compression: OTT set to 70% depth with high upward compression.
  - Sidechain Pumping: Hard sidechain volume ducking dropping 100% on kicks and snares, recovering over an 8th-note duration.

#### Structural Dynamics
- **Acoustic Ballad to Melodic Drop**: Intimate piano and vocal verse $ightarrow$ orchestral strings building in pre-chorus $ightarrow$ snare build with pitch risers $ightarrow$ beat 4 zero-drop silence with vocal breath $ightarrow$ devastatingly emotional supersaw drop.

---

### 79. Seven Lions

#### Top Billboard Chart Achievements
- **"Strangers" (with Myon & Shane 54 feat. Tove Lo)**: #15 Billboard Hot Dance/Electronic Songs.
- **"First Time" (with SLANDER & Dabin)**: Hot Dance/Electronic Songs hit.
- **"Rush Over Me" (with SLANDER & Said The Sky feat. HALIENE)**: #35 Hot Dance/Electronic Songs.
- **"Don't Leave" (feat. Ellie Goulding)**: Global melodic bass crossover hit.

#### Harmonic Progression & Voicing
- **"Strangers" Soaring Minor Progression**: Key of Eb minor.
  $$	ext{Ebm} \longrightarrow 	ext{B} \longrightarrow 	ext{F\#} \longrightarrow 	ext{C\#}$$
  - **Roman Numerals**: $	ext{i} - 	ext{VI} - 	ext{III} - 	ext{VII}$
  - **Suspensions**: Rich $	ext{Ebmin9}$ and $	ext{Bmaj7}$ voicings that reflect classic trance harmony.
- **"Rush Over Me" Emotional Arc**: Key of Ab Major / F minor ($	ext{Fm} - 	ext{Db} - 	ext{Ab} - 	ext{Eb}$, $	ext{vi} - 	ext{IV} - 	ext{I} - 	ext{V}$).

#### Topline Melodic Hook & Vocal Chops
- **Ethereal Vocal Toplines**: Ethereal, soaring female vocal performances (HALIENE, Tove Lo, Ellie Goulding) with wide vibrato and high emotional intensity.
- **Counterpoint Arpeggiations**: Fast 16th-note plucks weaving counterpoint melodies behind the main supersaw chords.

#### Bass Groove & Sub Dynamics
- **Melodic Dubstep to Psy-Trance Fusion**: Alternates between 140 BPM half-time dubstep grooves and driving 138–140 BPM psy-trance rolling triplet basslines ($	ext{K - B - B - B}$).
- **Distorted Mid-Growls**: Aggressive FM growls layered between melodic chord phrases.

#### Timbral Profile & Synthesis
- **Trance Supersaws + Dubstep Power**: 32-voice detuned supersaws layered with massive cathedral hall reverbs (Valhalla VintageVerb, 4-second decay, 35% wet) automated to duck with the chords.

#### Structural Dynamics
- **Extended Cinematic Journeys**: Fantasy-orchestral intros with strings and harps $ightarrow$ vocal build $ightarrow$ drop 1: soaring melodic dubstep $ightarrow$ drop 2: aggressive psy-trance or brostep switch-up.

---

### 80. Said The Sky

#### Top Billboard Chart Achievements
- **"All I Got" (feat. Kwesi)**: Hot Dance/Electronic Songs hit, over 110M Spotify streams.
- **"Hero" (with Dabin feat. Frills)**: Hot Dance/Electronic entry.
- **"Rush Over Me" (with Seven Lions & SLANDER)**: #35 Hot Dance/Electronic Songs.
- **"Bittersweet Symphony"**: Viral melodic bass anthem.

#### Harmonic Progression & Voicing
- **"All I Got" Organic Diatonic Progression**: Key of C Major / A minor.
  $$	ext{Am} \longrightarrow 	ext{F} \longrightarrow 	ext{C} \longrightarrow 	ext{G}$$
  - **Extended Voicings**: $	ext{Am9} \longrightarrow 	ext{Fmaj7} \longrightarrow 	ext{Cadd9} \longrightarrow 	ext{G6}$
  - **Roman Numerals**: $	ext{vi9} - 	ext{IVmaj7} - 	ext{Iadd9} - 	ext{V6}$
- **"Hero" Folk-Pop Harmony**: Key of Eb Major ($	ext{Eb} - 	ext{Bb} - 	ext{Cm} - 	ext{Ab}$, $	ext{I} - 	ext{V} - 	ext{vi} - 	ext{IV}$) with delicate piano suspensions.

#### Topline Melodic Hook & Vocal Chops
- **Vulnerable Folk-Pop Vocals**: Intimate singer-songwriter vocal performances.
- **Live Acoustic Counter-Melodies**: Real acoustic piano motifs and solo violin/viola lines playing conversational counter-melodies across the drop.

#### Bass Groove & Sub Dynamics
- **Organic Half-Time Groove**: Warm 808 sub bass sitting beneath an acoustic-sampled kick drum; soft acoustic snare layered with a snappy electronic clap; gentle hi-hat brushes.

#### Timbral Profile & Synthesis
- **Acoustic-Electronic Hybrid**: Live recorded upright piano, real violin and cello ensembles, and warm acoustic guitars blended seamlessly into wide, detuned Serum supersaws. Gentle, musical sidechain compression.

#### Structural Dynamics
- **Storybook Emotional Arc**: Begins as an intimate acoustic folk ballad $ightarrow$ strings and acoustic drums enter $ightarrow$ snare build with piano chimes $ightarrow$ beat 4 zero-drop silence with vocal breath $ightarrow$ breathtaking melodic bass drop release.

---

## 3. Comprehensive Voicing & MIDI Architecture Reference Table

| Artist | Hit Track | Key | Roman Numerals | Chord Symbols | Bass MIDI (Roots) | Drop-2 Voicing Notes | Signature Sound Device |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **61. Flume** | *Never Be Like You* | Bb Maj / G min | IVmaj9 - V7sus4 - vi7 - I6 | Ebmaj9 - Fsus4 - Gm7 - Bb/D | 39, 41, 43, 38 | G3, Eb4, F4, D5 | Granular vocal chops, unquantized swing |
| **62. Illenium** | *Good Things Fall Apart* | D Major | I - V - vi7 - IV | Dadd9 - Asus4 - Bm7 - Gmaj7 | 38, 45, 47, 43 | A3, D4, F#4, E5 | 16-voice supersaw stack, 500ms beat 4 cut |
| **63. San Holo** | *Light* | Db Major | ii7 - iii7 - IVmaj7 - Vadd9 | Ebm7 - Fm7 - Gbmaj7 - Abadd9 | 39, 41, 42, 44 | Bb3, Ebm4, F4, Db5 | Clean Stratocaster arps, +12st vocal chop |
| **64. Skrillex** | *Where Are Ü Now* | F# min / A Maj | i - VI - III - VII | F#m9 - Dmaj7 - Aadd9 - Esus4 | 42, 38, 45, 40 | C#4, F#4, A4, G#5 | +24st pitch-shifted "dolphin" vocal lead |
| **65. Diplo** | *Lean On* | G minor | i - VI - III - VII | Gm7 - Ebmaj7 - Bb - F | 43, 39, 46, 41 | D4, G4, Bb4, F5 | Moombahton/trap dembow groove, portamento lead |
| **66. DJ Snake** | *Middle* | A Major | IVmaj7 - V - vi7 - iii7 | Dmaj7 - E - F#m7 - C#m7 | 38, 40, 42, 37 | A3, D4, F#4, C#5 | Formant-shifted pentatonic vocal cascade |
| **67. REZZ** | *Edge* | F Phrygian | i - bII - i | Fm - Gb - Fm | 41, 42, 41 | C4, F4, Ab4, Gb4 | 100 BPM industrial midtempo, distorted Reese |
| **68. Subtronics** | *GRIZTRONICS* | Wonky Riddim | i - #iv - i (Tritone) | F - B - F | 41, 47, 41 | F3, B3, Eb4, G#4 | Serum FM from B, offbeat triplet riddim wonk |
| **69. Excision** | *Feel Something* | Ab minor | i - VI - III - VII | Abm - E - B - F# | 44, 40, 47, 42 | Eb4, Ab4, B4, F#5 | Metalcore screamed build into 500k-watt sub drop |
| **70. Knife Party** | *Internet Friends* | F# minor | i - bVI - bVII - i | F#m - D - E - F#m | 42, 38, 40, 42 | A3, F#4, C#5, E5 | Narrative voiceover, razor-sharp FM screeches |
| **71. Pendulum** | *Watercolour* | G minor | i - VI - III - VII | Gm - Eb - Bb - F | 43, 39, 46, 41 | Bb3, G4, D5, F5 | 174 BPM two-step DnB, rock vocals + brass |
| **72. Chase & Status**| *Disconnect* | A minor | i - VI - III - VII | Am - F - C - G | 45, 41, 36, 43 | C4, A4, E5, G5 | High-belt soul topline, sound-system roller sub |
| **73. Sub Focus** | *Desire* | G# min / B Maj | i - VI - III - VII | G#m - E - B - F# | 44, 40, 47, 42 | B3, G#4, D#5, F#5 | 174 BPM dancefloor DnB, trance piano stabs |
| **74. Marshmello** | *Happier* | F Major | I - ii7 - vi - IV | F - Gm7 - Dm - Bb | 41, 43, 38, 46 | A3, F4, C5, G5 | Radio-pop future bass, pentatonic bell pluck |
| **75. RL Grime** | *I Wanna Know* | Eb Maj / C min | vi - IV - I - V | Cm7 - Abmaj7 - Ebadd9 - Bbsus4 | 36, 44, 39, 46 | G3, Eb4, Bb4, D5 | Octave-sliding 808 sub, cinematic horn builds |
| **76. Alison Wonderland**| *Church* | Eb minor | i - VI - III - VII | Ebm - B - F# - C# | 39, 47, 42, 37 | Bb3, Eb4, Gb4, Db5 | Live acoustic cello layers, slumping trap drums |
| **77. NGHTMRE** | *GUD VIBRATIONS* | F# Major | I - IV - vi - V | F#add9 - Bmaj7 - D#m - C# | 42, 47, 39, 45 | G#3, F#4, C#5, E#5 | Metallic percussive leads, octave vocal chops |
| **78. SLANDER** | *Love Is Gone* | Db Maj / Bb min | vi7 - IVmaj7 - Iadd9 - Vsus4 | Bbm7 - Gbmaj7 - Dbadd9 - Absus4 | 46, 42, 37, 44 | F3, Db4, Ab4, Eb5 | Soaring Dylan Matthew vocal, 6-layer supersaw |
| **79. Seven Lions** | *Strangers* | Eb minor | i - VI - III - VII | Ebmin9 - Bmaj7 - F# - C#sus4 | 39, 47, 42, 37 | F4, Bb4, Eb5, Ab5 | Melodic dubstep + psy-trance rolling triplets |
| **80. Said The Sky** | *All I Got* | C Maj / A min | vi9 - IVmaj7 - Iadd9 - V6 | Am9 - Fmaj7 - Cadd9 - G6 | 45, 41, 36, 43 | G3, C4, E4, B4 | Upright piano + violin hybrid, acoustic folk drop |

---

## 4. Algorithmic Sound Design & Mixing Rules

1. **Sub Bass vs. Kick Alignment**:
   - The sub bass fundamental ($30 - 65	ext{ Hz}$) must always be monophonic.
   - Use dynamic sidechain ducking (e.g. FabFilter Pro-MB in sidechain split mode or Cableguys VolumeShaper) to pull down the sub by $-18	ext{ dB}$ to $-30	ext{ dB}$ for the first $40 - 70	ext{ ms}$ of every kick hit.
2. **Supersaw Stereophony & Layering**:
   - Separate chord stacks into minimum 3 distinct frequency registers:
     - **Low-Mid Warmth (150–400 Hz)**: 2–4 unison voices, narrow stereo spread (20–30%), mono compatible.
     - **Mid Punch (400 Hz – 2.5 kHz)**: 7–8 unison voices, detuned 15 cents, stereo width 100%.
     - **High Air (2.5 kHz – 18 kHz)**: 16 unison voices, detuned 25–35 cents, stereo width 150% (Haas delayed by 10–14 ms), driven by OTT compression (upward + downward).
3. **The Pre-Drop Vacuum (Beat 4 Mute)**:
   - At bar measure $X$, beat 4.0 to beat 4.9, mute all harmonic synths, sub-bass, and drum busses.
   - Retain only an isolated, completely dry vocal breath, drumstick rim click, or acoustic guitar squeak.
   - Release all compressor sidechain circuits on the downbeat of bar $X+1$ for instantaneous maximum SPL impact.
4. **Vocal Chop Processing Chain**:
   - Formant shift (+2 to +5 semitones via Little AlterBoy or Melodyne).
   - High-pass filter at 250 Hz to remove low-mid masking.
   - Aggressive saturation (Soundtoys Decapitator Style T or E, Drive 4.0).
   - Stereo ping-pong delay (1/8th note triplet) into lush hall reverb (3.0s decay, low cut at 400 Hz, high cut at 7 kHz).
