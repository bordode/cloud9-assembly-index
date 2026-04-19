
import numpy as np

class CPAssemblyCalculator:
    def __init__(self):
        self.eta_sm = 1e-18
        self.eta_obs = 6e-10

    def calculate_amplitude_complexity(self, n_amplitudes: int,
                                      phase_information: float) -> float:
        path_bits = np.log2(n_amplitudes) if n_amplitudes > 0 else 0
        phase_bits = phase_information
        return path_bits + phase_bits

    def baryogenesis_efficiency(self, a_cp_c: float, expansion_rate: float = 1.0) -> float:
        """
        Calculate efficiency from CP-Assembly Index.
        expansion_rate is now optional to prevent TypeErrors when called with one argument.
        """
        efficiency = 1 / (1 + np.exp(-(a_cp_c - 1.5)))
        return efficiency

    def high_assembly_instability(self, a_c_system: float,
                                 a_cp_local: float) -> float:
        threshold = 2.0
        if a_c_system < threshold:
            return a_cp_local
        else:
            amplification = 1 + 0.1 * (a_c_system - threshold)
            return a_cp_local * amplification
