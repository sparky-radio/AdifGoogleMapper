BAND_COLORS = { "17m" : "#f2f261",
               "160m" : "#7cfc00",
               "15m" : "#cca166", 
               "20m" : "#f2c40c", 
               "30m" : "#62d962", 
               "40m" : "#5959ff", 
               "12m" : "#b22222",
               "10m" : "#ff69b4",
               "80m" : "#e550e5",
               "60m" : "#00008b",
               "6m" : "#FF0000",
               "600m" : "#1e90ff",
               "2m" : "#FF1493",
               "11m" : "#00ff00",
               "10Ghz" : "#696969",
               "2200m" : "#ff4500",
               "2200m" : "#ff4500",
               "2.4Ghz" : "#FF7F50",
               "5m" : "#e0e0e0",
               "8m" : "#7f00f1"
                 }

def wspr_frequency_to_band(frequency) :
  band = ''
  if frequency > 0 and frequency < 3:
    band = '160m'
  elif frequency < 5:
    band = '80m'
  elif frequency < 7:
    band = '60m'
  elif frequency < 10:
    band = '40m'
  elif frequency < 14:
    band = '30m'
  elif frequency < 18:
    band = '20m'
  elif frequency < 21:
    band = '17m'
  elif frequency < 24:
    band = '15m'
  elif frequency < 28:
    band = '12m'
  elif frequency < 30:
    band = '10m'
  elif frequency < 52:
    band = '6m'
  elif frequency < 145:
    band = '2m'

  return band