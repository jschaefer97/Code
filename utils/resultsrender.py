import os
import numpy as np
import pandas as pd
import re

def save_overall_rmse_table(df, *, path, caption="Relative RMSE by horizon",
                   label="tab:rel_rmse_panel", panel_title="Relative RMSE"):
    """
    Render a Booktabs + threeparttable + tabularx LaTeX table that
    spans the full text width. INPUT df is expected to have rows=horizons (e.g., h0,h1,h2)
    and columns=methods (LASSO, Elastic Net, ...). This function TRANSPOSES it so that
    methods become rows and horizons become columns.
    """

    # transpose: methods = rows, horizons = columns
    dfT = df.T if isinstance(df, pd.DataFrame) else pd.DataFrame(df).T
    methods = list(dfT.index)
    horizons = list(dfT.columns)

    # number formatting: 2 decimals, NaN -> blank
    def fmt(x):
        try:
            x = float(x)
            return "" if not np.isfinite(x) else f"{x:.2f}"
        except Exception:
            return ""

    # build header: first column is method label, then horizon labels
    header = " & ".join([""] + [str(h) for h in horizons]) + r" \\"

    # panel row (italic text in the first cell, blanks elsewhere)
    panel_row = (
        r"\multicolumn{1}{l}{\textit{" + panel_title + r"}} & "
        + " & ".join([""] * len(horizons))
        + r" \\"
    )

    # body
    body_lines = []
    for m in methods:
        vals = [fmt(dfT.loc[m, h]) for h in horizons]
        body_lines.append(f"{m} & " + " & ".join(vals) + r" \\")
    body = "\n".join(body_lines)

    # column spec: left first col + centered, stretchy columns for the horizons
    # tabularx with full width; each numeric col uses centered X columns
    num_cols = len(horizons)
    colspec = "l" + " ".join([r">{\centering\arraybackslash}X" for _ in range(num_cols)])

    latex = (
        r"% Requires in preamble: \usepackage{booktabs,threeparttable,tabularx}" "\n"
        r"\begin{table}[!htbp]" "\n"
        r"  \centering" "\n"
        r"  \renewcommand{\arraystretch}{1.15}" "\n"
        r"  \setlength{\tabcolsep}{5pt}" "\n"
        r"  \begin{threeparttable}" "\n"
        f"    \\caption{{{caption}}}\n"
        f"    \\label{{{label}}}\n"
        f"    \\begin{{tabularx}}{{\\textwidth}}{{{colspec}}}\n"
        r"      \toprule" "\n"
        f"      {header}\n"
        r"      \midrule" "\n"
        f"      {panel_row}\n"
        f"{body}\n"
        r"      \bottomrule" "\n"
        r"    \end{tabularx}" "\n"
        r"  \end{threeparttable}" "\n"
        r"\end{table}"
    )

    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(latex)

def save_period_rel_rmse_panels(
    df_by_h: dict,                # {"h0": df0, "h1": df1, "h2": df2}, rows=methods, cols=eras
    *,
    path: str,
    caption: str = "Relative RMSE by era (three panels by horizon)",
    label: str = "tab:rel_rmse_panels",   # labels are written raw (not TeX-escaped)
    panel_titles: dict | None = None,     # {"h0": "Horizon h0", "h1": "Horizon h1", "h2": "Horizon h2"}
    era_order: list[str] | None = None,   # ["covid","post_covid","all"]; if None, inferred from first df
    method_labels: dict | None = None     # map method -> pretty label; if None, use index as-is
):
    """
    Write a LaTeX table (Booktabs + threeparttable + tabularx + array) with THREE PANELS (h0,h1,h2).
    - Era headers ("Covid", "Post Covid", "All") are shown ONCE at the top.
    - In each panel, the minimum value per column is bolded (NaNs ignored).
    - Values formatted to 2 decimals; NaNs -> blank.
    - 'label' is NOT TeX-escaped; it is sanitized and written raw to avoid aux issues.
    """

    # ---- validate horizons ----
    horizon_order = [h for h in ["h0", "h1", "h2"] if h in df_by_h and isinstance(df_by_h[h], pd.DataFrame)]
    if not horizon_order:
        raise ValueError("df_by_h must contain at least one of: 'h0','h1','h2' with DataFrame values.")

    # ---- choose era order ----
    if era_order is None:
        era_order = list(df_by_h[horizon_order[0]].columns)

    # ---- era display names ----
    era_display = {"covid": "Covid", "post_covid": "Post Covid", "all": "All"}
    for e in era_order:
        era_display.setdefault(e, str(e).replace("_", r"\_"))

    # ---- escaping for visible text (NOT for labels) ----
    def tex_escape(s: str) -> str:
        s = str(s)
        return (s.replace("\\", r"\textbackslash{}")
                 .replace("_", r"\_")
                 .replace("%", r"\%")
                 .replace("&", r"\&"))

    # ---- sanitize label: keep only [A-Za-z0-9:._-] ----
    def sanitize_label(s: str) -> str:
        s = str(s)
        s = re.sub(r"[^A-Za-z0-9:._-]+", "-", s)
        s = re.sub(r"-{2,}", "-", s).strip("-")
        return s

    # ---- number formatting ----
    def fmt_num(x) -> str:
        try:
            x = float(x)
            return "" if not np.isfinite(x) else f"{x:.2f}"
        except Exception:
            return ""

    # ---- ensure all dfs have the requested columns (drop extras) ----
    for h in horizon_order:
        missing = [e for e in era_order if e not in df_by_h[h].columns]
        if missing:
            raise ValueError(f"df_by_h['{h}'] is missing columns: {missing}")
        df_by_h[h] = df_by_h[h].reindex(columns=era_order)

    # ---- column spec & header printed once ----
    num_cols = len(era_order)
    colspec = "l " + " ".join([r">{\centering\arraybackslash}X" for _ in range(num_cols)])
    header_once = " & ".join([""] + [era_display[e] for e in era_order]) + r" \\"

    # ---- panel titles ----
    ptitles = panel_titles or {"h0": "Horizon h0", "h1": "Horizon h1", "h2": "Horizon h2"}

    # ---- build all panels ----
    panels_tex = []
    for h in horizon_order:
        df = df_by_h[h]

        # per-column minima for this panel (ignore NaNs)
        col_mins = {}
        for e in era_order:
            col_vals = pd.to_numeric(df[e], errors="coerce")
            col_mins[e] = float(np.nanmin(col_vals)) if np.isfinite(col_vals).any() else None

        # pretty row labels (escaped)
        row_labels = [method_labels.get(i, i) if method_labels else i for i in df.index]
        row_labels = [tex_escape(lbl) for lbl in row_labels]

        # panel title line
        n_total_cols = 1 + num_cols
        title = tex_escape(ptitles.get(h, h))
        panel_lines = [rf"\multicolumn{{{n_total_cols}}}{{l}}{{\textit{{{title}}}}} \\"]

        # rows
        for idx, m in enumerate(df.index):
            row_vals = []
            for e in era_order:
                raw = df.loc[m, e]
                sval = fmt_num(raw)
                if sval != "":
                    cm = col_mins[e]
                    try:
                        v = float(raw)
                        if (cm is not None) and np.isfinite(v) and np.isclose(v, cm, rtol=1e-9, atol=1e-12):
                            sval = r"\textbf{" + sval + "}"
                    except Exception:
                        pass
                row_vals.append(sval)
            panel_lines.append(f"{row_labels[idx]} & " + " & ".join(row_vals) + r" \\")
        panels_tex.append("\n".join(panel_lines))

    panels_joined = (r"      \midrule" "\n").join(panels_tex)

    # ---- assemble LaTeX ----
    safe_label = sanitize_label(label)
    latex = (
        r"% Requires in preamble: \usepackage{booktabs,threeparttable,tabularx,array}" "\n"
        r"% NOTE: the 'array' package is required for \arraybackslash in the colspec." "\n"
        r"\begin{table}[!htbp]" "\n"
        r"  \centering" "\n"
        r"  \renewcommand{\arraystretch}{1.15}" "\n"
        r"  \setlength{\tabcolsep}{5pt}" "\n"
        r"  \begin{threeparttable}" "\n"
        f"    \\caption{{{tex_escape(caption)}}}\n"
        f"    \\label{{{safe_label}}}\n"
        f"    \\begin{{tabularx}}{{\\textwidth}}{{{colspec}}}\n"
        r"      \toprule" "\n"
        f"      {header_once}\n"
        r"      \midrule" "\n"
        f"{panels_joined}\n"
        r"      \bottomrule" "\n"
        r"    \end{tabularx}" "\n"
        r"  \end{threeparttable}" "\n"
        r"\end{table}"
    )

    # ---- write file ----
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(latex)
