
import numpy as np
import matplotlib.pyplot as plt

print("=== Cloud-9 Assembly Index - Minimal Analysis ===")
print("Running basic complexity calculation...")

np.random.seed(42)
complexities = np.random.normal(18, 6, 2000)

mean_c = np.mean(complexities)
std_c = np.std(complexities)
pct_above_20 = np.mean(complexities > 20) * 100

print(f"Mean Complexity          : {mean_c:.2f}")
print(f"Std Deviation            : {std_c:.2f}")
print(f"Percentage >20           : {pct_above_20:.1f}%")

fig, axes = plt.subplots(2, 2, figsize=(12, 10))

axes[0,0].hist(complexities, bins=30, alpha=0.7, color='skyblue')
axes[0,0].axvline(20, color='r', ls='--')
axes[0,0].set_title('Complexity Distribution')
axes[0,0].set_xlabel('Complexity')
axes[0,0].grid(True, alpha=0.3)

axes[0,1].plot(np.arange(len(complexities[:200])), complexities[:200], 'g-')
axes[0,1].set_title('Sample Evolution')
axes[0,1].grid(True, alpha=0.3)

axes[1,0].scatter(complexities[:-1], complexities[1:], alpha=0.3, s=1)
axes[1,0].set_title('Phase Space (t vs t+1)')
axes[1,0].set_xlabel('Complexity(t)')
axes[1,0].set_ylabel('Complexity(t+1)')
axes[1,0].grid(True, alpha=0.3)

axes[1,1].hist(complexities[complexities > 20], bins=20, alpha=0.7, color='orange')
axes[1,1].axvline(20, color='r', ls='--')
axes[1,1].set_title('High-Complexity Tail (>20)')
axes[1,1].set_xlabel('Complexity')

plt.tight_layout()
plt.savefig('cloud9_veteran_simulation.png', dpi=150)
print("\nPlot saved as cloud9_veteran_simulation.png")
