#%%

import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler 
from sklearn.linear_model import lasso_path, enet_path, Ridge
import matplotlib.lines as mlines
from matplotlib.ticker import LogLocator, LogFormatter  

#%%

# -------------------- Palette (tweak if you like) --------------------
PALETTE = {
    "A": "#9BC2E9",     # steel blue
    "B": "#0C437A",     # darker slate blue
    "S": "#47B9D6",     # light blue-grey
    "N": "#B8B8B8",     # neutral grey (noise)
    "zero": "#6E6E6E",  # zero line / axes accent
}

plt.rcParams.update({
    "axes.edgecolor": "#1f1f1f",
    "xtick.color": "#1f1f1f",
    "ytick.color": "#1f1f1f",
    "axes.labelcolor": "#1f1f1f",
    "text.color": "#1f1f1f",
    "grid.color": "#D4D4D4",
})

# -------------------- Config --------------------
rng = np.random.default_rng(7)
n_samples = 300
n_features = 16

grpA = [0, 1, 2]     # Group A (positive β)
grpB = [3, 4]        # Group B (negative β)
single = [5]         # Single (positive β)
informative = np.array(grpA + grpB + single)
noise_idx = np.array([i for i in range(n_features) if i not in informative])

# True β with enforced signs
beta_vals = np.array([5.0, 4.5, 4.0, -6.0, -5.0, 3.5])
noise_sd = 3.0

########################################################################
########################################################################
l1_ratio = 0.2 # <------------- Change this to 0.8 to get both EN plots
########################################################################
########################################################################

# -------------------- Covariance --------------------
# --- Define target correlations for the block-structured covariance ---
rho_A, rho_B, rho_cross = 0.90, 0.85, 0.05     # within-GroupA, within-GroupB, across-informative-blocks
rho_noise, rho_noise_cross = 0.10, 0.05        # within-noise block, noise↔informative
Sigma = np.eye(n_features)                     # start from identity (unit variance, zero covariance)

# --- Set high within-block correlations for Group A (3 vars) ---
for i in grpA:
    for j in grpA:
        if i != j:
            Sigma[i, j] = rho_A

# --- Set high within-block correlation for Group B (2 vars) ---
Sigma[grpB[0], grpB[1]] = Sigma[grpB[1], grpB[0]] = rho_B

# --- Set weak correlations across informative blocks (A/B/single) but not within A or B ---
for i in informative:
    for j in informative:
        if i != j and (i not in grpA or j not in grpA) and (i not in grpB or j not in grpB):
            Sigma[i, j] = rho_cross

# --- Set weak within-block correlations for the noise variables ---
for i in noise_idx:
    for j in noise_idx:
        if i != j:
            Sigma[i, j] = rho_noise

# --- Set weak correlations between every noise variable and every informative variable ---
for i in noise_idx:
    for j in informative:
        Sigma[i, j] = Sigma[j, i] = rho_noise_cross

# --- Numerical safety: ensure Sigma is positive semidefinite (tiny diagonal bump if needed) ---
eigvals = np.linalg.eigvalsh(Sigma)
if np.min(eigvals) <= 0:
    Sigma += np.eye(n_features) * (1e-6 - np.min(eigvals))

# -------------------- Simulate --------------------
# Draw X ~ N(0, Sigma) with n_samples observations and n_features variables
X = rng.multivariate_normal(mean=np.zeros(n_features), cov=Sigma, size=n_samples)

# Build the true coefficient vector: nonzeros for informative indices, zeros elsewhere
beta = np.zeros(n_features)
beta[informative] = beta_vals

# Add Gaussian noise to the linear model
eps = rng.normal(0.0, noise_sd, size=n_samples)

# Generate response: y = X beta + ε
y = X @ beta + eps

# Standardize
scaler = StandardScaler()
X_std = scaler.fit_transform(X)
y_centered = y - y.mean()

# Paths
s_max = np.linalg.svd(X_std, compute_uv=False)[0]
s_max2 = s_max*0.001
alphas_ridge = np.geomspace(1e-2, 1e6 * s_max2, 100)
coefs_ridge = np.zeros((n_features, len(alphas_ridge)))
for k, a in enumerate(alphas_ridge):
    ridge = Ridge(alpha=a, fit_intercept=False, solver="svd")
    ridge.fit(X_std, y_centered)
    coefs_ridge[:, k] = ridge.coef_

alphas_lasso, coefs_lasso, _ = lasso_path(X_std, y_centered, alphas=None, max_iter=7000)
alphas_enet,  coefs_enet,  _ = enet_path(X_std, y_centered, l1_ratio=l1_ratio, alphas=None, max_iter=7000)

# Colors
colors = {}
colors.update({j: PALETTE["A"] for j in grpA})
colors.update({j: PALETTE["B"] for j in grpB})
colors.update({j: PALETTE["S"] for j in single})
for j in noise_idx:
    colors[j] = PALETTE["N"]

legend_handles = [
    mlines.Line2D([], [], color=PALETTE["A"], lw=2.8, label="Group A"),
    mlines.Line2D([], [], color=PALETTE["B"], lw=2.8, label="Group B"),
    mlines.Line2D([], [], color=PALETTE["S"], lw=2.8, label="Single"),
    mlines.Line2D([], [], color=PALETTE["N"], lw=1.8, label="Noise"),
]

def plot_paths(alphas, coefs, title, add_legend=False):
    fig = plt.figure(figsize=(6.6, 4.6))
    ax = plt.gca()
    for j in range(coefs.shape[0]):
        lw = 2.8 if j in informative else 1.4
        ax.plot(alphas, coefs[j, :], linewidth=lw, color=colors[j])

    ax.axhline(0.0, linewidth=1.2, color=PALETTE["zero"])

    ax.set_xscale("log")
    ax.xaxis.set_major_locator(LogLocator(base=10.0, numticks=6))
    ax.xaxis.set_major_formatter(LogFormatter(base=10.0))
    ax.tick_params(axis="x", which="major", labelsize=10)  # smaller λ tick labels
    ax.tick_params(axis="x", which="minor", labelsize=8)   # optional: smaller minor ticks

    ax.set_xlabel(r"$log(\lambda)$", fontsize=12)
    ax.set_ylabel("Standardized Coefficients", fontsize=12)
    ax.set_title(title)
    if add_legend:
        ax.legend(handles=legend_handles, loc="best", frameon=False)
    fig.tight_layout()
    plt.show()

# -------------------- Ridge path (full sweep to ~0) --------------------
# Plot LASSO
plot_paths(alphas_lasso, coefs_lasso,
           "LASSO Coefficient Paths",
           add_legend=False)

# Plot Elastic Net
plot_paths(alphas_enet, coefs_enet,
           f"Elastic Net Coefficient Paths ($\\alpha$={l1_ratio})",
           add_legend=True)

# Plot Ridge
plot_paths(alphas_ridge, coefs_ridge, 
           "Ridge Coefficient Paths", 
           add_legend=False)


# %%
