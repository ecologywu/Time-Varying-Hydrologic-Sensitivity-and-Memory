"""
Render methods-section equations as high-resolution PNGs (STIX math font)
for insertion into the Word manuscript. Equation number right-aligned.
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT_DIR = r"C:\Users\dell\Documents\Trae-CN\temp_20261018_01\figures\equations"
os.makedirs(OUT_DIR, exist_ok=True)

plt.rcParams["mathtext.fontset"] = "stix"
plt.rcParams["font.family"] = "STIXGeneral"

EQUATIONS = {
    # ---- 2.2 DLM ----
    "eq01": (r"$x^{\prime}(t) = x(t) - \overline{x}_{DOY}(t)$", "1"),
    "eq02": (r"$Q^{\prime}(t) = \beta_0 + \sum_{m \in \{P,\,VPD,\,SM\}} \sum_{l=0}^{L-1} w_m(l;\, \theta_m) X_m(t-l) + \varepsilon(t)$", "2"),
    "eq03": (r"$w_m(l;\, \theta_m) = \sum_{k=1}^{4} \theta_{m,k}\, B_k(l)$", "3"),
    "eq04": (r"$\beta_m = \sum_{l=0}^{L-1} w_m(l;\, \theta_m)$", "4"),
    "eq05": (r"$M75_m = \min \left\{ l^{*} : \sum_{l=0}^{l^{*}} |w_m(l)| \geq 0.75 \sum_{l=0}^{L-1} |w_m(l)| \right\}$", "5"),
    # ---- 2.3 Decomposition ----
    "eq06": (r"$\theta_m(t_w) = \alpha_{m,0} + \alpha_m^{T} \mathbf{f}(t_w) + r_m(t_w)$", "6"),
    "eq07": (r"$\theta_m(t_w) = \overline{\theta}_m + C_m(t_w) + R_m(t_w), \quad C_m(t_w) = \alpha_m^{T}[\mathbf{f}(t_w) - \overline{\mathbf{f}}]$", "7"),
    "eq08": (r"$s_{R,m} = \sum_{w} (t_w - \overline{t})\, R_m(t_w) \; / \; \sum_{w} (t_w - \overline{t})^{2}$", "8"),
    # ---- 2.4 Moran's I ----
    "eq09": (r"$I = \frac{n}{S_0} \, \frac{\sum_{i \neq j} w_{ij}\, z_i\, z_j}{\sum_{i} z_i^{2}}, \quad S_0 = \sum_{i \neq j} w_{ij}$", "9"),
    # ---- 2.5 Counterfactual ----
    "eq10": (r"$\hat{Q}_s(t) = \sum_{m} \sum_{l=0}^{L-1} w_m(l;\, \theta_s(t_w)) X_m(t-l), \quad s \in \{\mathrm{fact},\, A,\, B\}$", "10"),
    "eq11": (r"$\Delta_A = b_{\mathrm{fact}} - b_{A}, \qquad \Delta_B = b_{\mathrm{fact}} - b_{B}$", "11"),
}

def render(name, latex, number, fontsize=13):
    fig = plt.figure(figsize=(7.0, 0.62))
    fig.patch.set_facecolor("white")
    fig.text(0.5, 0.5, latex, ha="center", va="center", fontsize=fontsize)
    fig.text(0.985, 0.5, f"({number})", ha="right", va="center", fontsize=11)
    fig.savefig(os.path.join(OUT_DIR, name + ".png"), dpi=300)
    plt.close(fig)

def main():
    for name, (latex, number) in EQUATIONS.items():
        render(name, latex, number)
    print(f"Rendered {len(EQUATIONS)} equations to {OUT_DIR}")

if __name__ == "__main__":
    main()
