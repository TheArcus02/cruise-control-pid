import numpy as np
from scipy.integrate import odeint
from vehicle import vehicle



def keep_limit(u: int) -> int:
    if u >= 100.0:
        u = 100.0
    if u <= -50.0:
        u = -50.0
    return u


def generate_angle_array(angles, length):

    if 0 not in angles.keys():
        angles[0] = 0

    angle_array = np.zeros(length)

    prev_angle_key = None
    prev_angle_val = None

    for key, value in sorted(angles.items()):
        if prev_angle_key is not None and prev_angle_val is not None:
            start_index = prev_angle_key
            end_index = key

            if start_index != end_index:
                end_index = min(end_index, length)
                angle_array[start_index:end_index] = np.linspace(prev_angle_val, value, end_index - start_index)

        prev_angle_key = key
        prev_angle_val = value

    # Dostosowanie od ostatniej wartosci do końca tablicy
    angle_array[prev_angle_key:] = prev_angle_val

    return angle_array


def simulate(tf=300.0, load=200.0, v0=0, ubias=0, set_points=None, angles=None, kc=0, taui=20):
    # Ustawienia symulacji
    if set_points is None:
        set_points = {0: 0}

    print(set_points)

    if tf is None or tf <= 0:
        tf = 1

    nsteps = tf + 1  # ilość kroków czasowych
    delta_t = tf / (nsteps - 1)  # długość poszczególnego kroku czasowego
    ts = np.linspace(0, tf, nsteps)  # wektor czasu z równymi odstępami (time space)

    step = np.zeros(nsteps)  # % położenia pedału gazu

    if load is None or load < 0:
        load = 0

    if  v0 is None or v0 < 0:
        v0 = 0

    if angles is None:
        angles = np.zeros(nsteps)
    else:
        angles = generate_angle_array(angles, nsteps)

    # prędkość docelowa (set point)
    sp = 0

    # Wartiści początkowe
    if not ubias:
        ubias = 0
    ubias = keep_limit(ubias)
    sum_int = 0.0

    # Sterowanie kontrolera
    Kc = kc
    tauI = taui

    # Przechowywanie wyników
    v_res = np.zeros(nsteps)
    error_res = np.zeros(nsteps)
    int_res = np.zeros(nsteps)
    sp_res = np.zeros(nsteps)

    for i in range(nsteps - 1):
        # Zmiana prędkości docelowej
        if i in set_points.keys():
            sp = set_points[i]

        sp_res[i + 1] = sp
        error = sp - v0
        error_res[i + 1] = error

        # Całka korelacji
        sum_int = sum_int + (error * delta_t)
        u = ubias + (Kc * error) + (Kc / tauI * sum_int)

        # Utrzymanie wartości pedału gazu w odpowienim przedziale
        u = keep_limit(u)

        int_res[i + 1] = sum_int
        step[i + 1] = u

        # Obliczenie chwili czasu dla prędkości
        angle = angles[i]
        v = odeint(vehicle, v0, [0, delta_t], args=(u, load, angle))
        v0 = v[-1]  # take the last value
        if v0 < 0: v0 = 0
        v_res[i + 1] = v0  # store the velocity for plotting

    return ts, step, v_res, error_res, int_res, sp_res, angles
