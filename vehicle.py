import numpy as np
def vehicle(v,t,u,load, angle):
    """
    :param v: prędkość pojazdu (m/s)
    :param t: czas (sec)
    :param u: pozycja pedału gazu (-50% to 100%)
    :param load: obciążenie pojazdu (pasażerowie, załadunek) (kg)
    :param angle: kąt nachylenia powierzchni
    :return: dv_dt: prędkość w chwili czasu
    """

    Cd = 0.24    # opór aerodynamiczny (Drag coeffcient)
    rho = 1.225  # gęstość powietrza (kg/m^3)
    A = 5.0      # Przekrój czynny (m^2)
    Fp = 30      # siła ciągu (N/%pedal)
    m = 500      # masa pojazdu (kg)
    # * np.sin(np.deg2rad(angle))
    # pochodna prędkości
    dv_dt = (1.0/(m+load)) * (Fp*u - 0.5*rho*Cd*A*v**2*np.sin(np.deg2rad(angle)))
    return dv_dt

