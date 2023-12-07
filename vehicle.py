import numpy as np
def vehicle(v,t,u,load, angle):
    #  v    = prędkość pojazdu (m/s)
    #  t    = czas (sec)
    #  u    = pozycja pedału gazu (-50% to 100%)
    #  load = obciążenie pojazdu (pasażerowie, załadunek) (kg)
    #  angle = kąt nachylenia powierzchni

    Cd = 0.24    # opór aerodynamiczny (Drag coeffcient)
    rho = 1.225  # gęstość powietrza (kg/m^3)
    A = 5.0      # Przekrój czynny (m^2)
    Fp = 30      # siła ciągu (N/%pedal)
    m = 500      # masa pojazdu (kg)
    # * np.sin(np.deg2rad(angle))
    # pochodna prędkości
    dv_dt = (1.0/(m+load)) * (Fp*u - 0.5*rho*Cd*A*v**2*np.sin(np.deg2rad(angle)))
    return dv_dt

