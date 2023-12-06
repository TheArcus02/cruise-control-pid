import numpy as np
from scipy.integrate import odeint
from vehicle import vehicle


def keep_limit(u: int) -> int:
    if u >= 100.0:
        u = 100.0
    if u <= -50.0:
        u = -50.0
    return u


def simulate(tf=300.0, load=200.0, v0=0, ubias=0):
    # Ustawienia symulacji
    if tf <= 0:
        tf = 1
    nsteps = 301  # ilość kroków czasowych
    delta_t = tf / (nsteps - 1)  # długość poszczególnego kroku czasowego
    ts = np.linspace(0, tf, nsteps)  # wektor czasu z równymi odstępami (time space)

    step = np.zeros(nsteps)  # % położenia pedału gazu

    if load < 0 or not load:
        load = 0
    if v0 < 0 or not v0:
        v0 = 0

    # prędkość docelowa (set point)
    sp = 25.0

    # Wartiści początkowe
    if not ubias:
        ubias = 0
    ubias = keep_limit(ubias)

    sum_int = 0.0

    # Sterowanie kontrolera
    Kc = 1.0 / 1.2  # Kc = 1/Kp
    tauI = 20.0

    # Przechowywanie wyników
    v_res = np.zeros(nsteps)
    error_res = np.zeros(nsteps)
    int_res = np.zeros(nsteps)
    sp_res = np.zeros(nsteps)

    for i in range(nsteps - 1):
        # Zmiana prędkości docelowej
        if i == 50:
            sp = 0
        if i == 100:
            sp = 15
        if i == 150:
            sp = 20
        if i == 200:
            sp = 10

        sp_res[i + 1] = sp
        error = sp - v0
        error_res[i + 1] = error

        # Całka korelacji
        sum_int = sum_int + error + delta_t
        u = ubias + Kc * error + Kc / tauI * sum_int

        # Utrzymanie wartości pedału gazu w odpowienim przedziale
        u = keep_limit(u)

        int_res[i + 1] = sum_int
        step[i + 1] = u

        # Obliczenie chwili czasu dla prędkości
        v = odeint(vehicle, v0, [0, delta_t], args=(u, load))

        v0 = v[-1]  # take the last value
        v_res[i + 1] = v0  # store the velocity for plotting

    return ts, step, v_res, error_res, int_res, sp_res
