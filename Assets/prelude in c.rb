use_bpm 48
use_synth :piano


C       = [:C4, :E4, :G4, :C5, :E5, :G4, :C5, :E5]
CM7_B   = [:B3, :C4, :E4, :G4, :C5, :E4, :G4, :C5]
D7      = [:D3, :A3, :D4, :Fs4, :D5, :Fs4, :A4, :D5]
Dm7_C   = [:C4, :D4, :A4, :D5, :F5, :A4, :D5, :F5]
D7_C    = [:C4, :D4, :Fs4, :A4, :D5, :Fs4, :A4, :D5]
G       = [:G3, :B3, :D4, :G4, :B4, :D4, :G4, :B4]
G_B     = [:B3, :D4, :G4, :D5, :G5, :G4, :D5, :G5]
G7_B    = [:B3, :D4, :G4, :D5, :F5, :G4, :D5, :F5]
Am7     = [:A3, :C4, :E4, :G4, :C5, :E4, :G4, :C5]
Am_C    = [:C4, :E4, :A4, :E5, :A5, :A4, :E5, :A5]

define :note_play do |a|
  2.times do
    for i in 0..8
      if i==0
        midi a[i], sustain: 2, decay: 2
      elsif i==1
        midi a[i], sustain: 1.75, decay: 1.75
      else
        midi a[i], sustain: 0.25
      end
      if i!=7
        sleep 0.25
      end
    end
  end
end

note_play C
note_play Dm7_C
note_play G7_B
note_play C
note_play Am_C
note_play D7_C
note_play G_B
note_play CM7_B
note_play Am7
note_play D7
note_play G_B