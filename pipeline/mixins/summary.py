import html
from typing import List
import pandas as pd
from typing import Dict, Optional
import numpy as np
import re
import os
from datetime import datetime
import tempfile

class SummaryMixin:

    def get_spec_summary(
        self,
        results_dict: Dict,
        *,
        spec_name: str,
        mapping_periods_name: str,
        mapping_name: str,
        impute: bool,
        impute_method: str,
        transform_all: str,
        confidence: float,
        start_date: pd.Timestamp,
        end_date: pd.Timestamp,
        dropvarlist: List[str],
        no_lags: str,
        umidas_model_lags: int,
        y_var: str,
        y_var_lags: int,
        y_var_short_name: str,
        nowcast_start: pd.Timestamp,
        varselection_method: str,
        alpha: int,
        tcv_splits: int,
        test_size: int,
        gap: int,
        max_train_size: int,
        cv: int,
        alphas: int,
        max_iter: int,
        random_state: int,
        with_mean: bool,
        with_std: bool,
        fit_intercept: bool,
        coef_tol: bool,
        selection_rule: str,
        se_factor: float,
        threshold_divisor: float,
        window_quarters: int,
        output_path: Optional[str] = None,
    ) -> str:
        """
        Create an HTML summary file with:
          1) Spec name + all parameters
          2) For each pool in {"avg","median","mseweight"} and for each [branch][crit]:
             yearly Avg RMSE and Avg MSE across all periods, plus overall
             avg/median/total RMSE & MSE (across all periods).

        Returns the path to the created HTML file.
        """

        def _to_dtindex(df: pd.DataFrame) -> pd.DatetimeIndex:
            if isinstance(df.index, pd.PeriodIndex):
                return df.index.to_timestamp()
            return pd.to_datetime(df.index)

        def _fmt_list(x):
            return ", ".join(map(str, x)) if isinstance(x, (list, tuple)) else str(x)

        def _num(x):
            try:
                return float(x)
            except Exception:
                return float("nan")

        # ---------- Build parameters section ----------
        params = [
            "General",
            ("spec_name", spec_name),
            ("mapping_periods_name", mapping_periods_name),
            ("mapping_name", mapping_name),
            ("start_date", str(pd.Timestamp(start_date).date()) if pd.notna(start_date) else ""),
            ("nowcast_start", str(pd.Timestamp(nowcast_start).date()) if pd.notna(nowcast_start) else ""),
            ("end_date", str(pd.Timestamp(end_date).date()) if pd.notna(end_date) else ""),
            ("y_var", y_var),
            ("y_var_short_name", y_var_short_name),

            "Data",
            ("impute", impute),
            ("impute_method", impute_method),
            ("transform_all", transform_all),
            ("confidence", confidence),
            ("dropvarlist", _fmt_list(dropvarlist)),
            ("no_lags", no_lags),
            ("umidas_model_lags", umidas_model_lags),
            ("y_var_lags", y_var_lags),

            "Selection",
            ("varselection_method", varselection_method),
            ("alpha", alpha),
            ("lambdas", alphas),
            ("max_iter", max_iter),
            ("random_state", random_state),
            ("with_mean", with_mean),
            ("with_std", with_std),
            ("fit_intercept", fit_intercept),
            ("selection_rule", selection_rule),
            ("se_factor", se_factor),
            ("threshold_divisor", threshold_divisor),
            ("coef_tol", coef_tol),
            ("window_quarters", window_quarters),

            "Selection - pyeacv",  
            ("cv", cv),

            "Selection - pyeatcv",   
            ("max_train_size", max_train_size),         
            ("tcv_splits", tcv_splits),
            ("test_size", test_size),
            ("gap", gap),
        ]

        # ---------- Pools from results_dict ----------
        model = results_dict.get("model", {})
        periods_avg = model.get("periods_avg", {})
        periods_median = model.get("periods_median", {})
        periods_mseweight = model.get("periods_mseweight", {})

        pools = [
            ("avg", "Average", periods_avg),
            ("median", "Median", periods_median),
            ("mseweight", "MSFE-weighted", periods_mseweight),
        ]

        # HTML parts accumulator
        sections = []

        # ---- Render rows: support section headers (strings or 1-tuples) ----
        spec_rows_parts = []
        for item in params:
            if isinstance(item, str) or (isinstance(item, tuple) and len(item) == 1):
                # section header row
                label = item if isinstance(item, str) else item[0]
                spec_rows_parts.append(
                    f'<tr><th class="section" colspan="2">{html.escape(str(label))}</th></tr>'
                )
            else:
                # regular (key, value) row
                try:
                    k, v = item
                except Exception:
                    # safety: render anything unexpected as a one-cell row
                    spec_rows_parts.append(
                        f'<tr><td colspan="2">{html.escape(str(item))}</td></tr>'
                    )
                else:
                    spec_rows_parts.append(
                        f"<tr><td><b>{html.escape(str(k))}</b></td>"
                        f"<td>{html.escape(str(v))}</td></tr>"
                    )

        spec_rows = "\n".join(spec_rows_parts)

        spec_section = f"""
        <h1>{html.escape(spec_name)}</h1>
        <h2>Parameters</h2>
        <table border="1" cellspacing="0" cellpadding="6">
            <tbody>
                {spec_rows}
            </tbody>
        </table>
        """
        sections.append(spec_section)

        # Metrics section intro
        sections.append("<h2>Performance Summary (Yearly averages over all periods)</h2>")
        sections.append(
            "<p>This section reports, for each pool "
            "<code>{\"avg\",\"median\",\"mseweight\"}</code> and for each "
            "<code>[branch][crit]</code> combination: "
            "(a) the per-year average RMSE and average MSE across all periods; and "
            "(b) overall averages, medians, and totals computed across all periods.</p>"
        )

        def _compute_yearly_avgs_and_overall(periods_dict: Dict[str, pd.DataFrame]):
            """
            Computes:
              - rmse_by_year_all (mean by year across all periods)
              - mse_by_year_all (mean by year across all periods)
              - overall rmse/mse vectors across all periods for avg/median/total
            """
            # keep only valid dataframes
            period_frames = {p: df for p, df in periods_dict.items() if isinstance(df, pd.DataFrame) and not df.empty}
            if not period_frames:
                return pd.Series(dtype=float), pd.Series(dtype=float), pd.Series(dtype=float), pd.Series(dtype=float)

            rmse_concat, mse_concat = [], []
            for _, df in period_frames.items():
                idx = _to_dtindex(df)
                # RMSE vector (per-quarter) preference: 'rmse'; else ratio mse/mse_ar4 as proxy
                if "rmse" in df.columns:
                    r = pd.to_numeric(df["rmse"], errors="coerce")
                    rmse_concat.append(pd.Series(r.values, index=idx.year))
                else:
                    if "mse" in df.columns and "mse_ar4" in df.columns:
                        mse = pd.to_numeric(df["mse"], errors="coerce")
                        mse_ar4 = pd.to_numeric(df["mse_ar4"], errors="coerce")
                        with np.errstate(divide="ignore", invalid="ignore"):
                            r = mse / mse_ar4
                        rmse_concat.append(pd.Series(r.values, index=idx.year))

                # MSE vector (per-quarter)
                if "mse" in df.columns:
                    m = pd.to_numeric(df["mse"], errors="coerce")
                    mse_concat.append(pd.Series(m.values, index=idx.year))
                elif {"y_actual", "y_pred"} <= set(df.columns):
                    ya = pd.to_numeric(df["y_actual"], errors="coerce")
                    yp = pd.to_numeric(df["y_pred"], errors="coerce")
                    se = (ya - yp) ** 2
                    mse_concat.append(pd.Series(se.values, index=idx.year))

            rmse_all = pd.concat(rmse_concat, axis=0) if rmse_concat else pd.Series(dtype=float)
            mse_all = pd.concat(mse_concat, axis=0) if mse_concat else pd.Series(dtype=float)

            rmse_by_year_all = rmse_all.groupby(level=0).mean() if not rmse_all.empty else pd.Series(dtype=float)
            mse_by_year_all = mse_all.groupby(level=0).mean() if not mse_all.empty else pd.Series(dtype=float)

            return rmse_by_year_all, mse_by_year_all, rmse_all, mse_all

        # Iterate pools -> branches -> crits
        for pool_key, pool_label, pool_dict in pools:
            if not pool_dict:
                continue

            sections.append(f"<h3>Pool: {html.escape(pool_label)}</h3>")

            for branch in ["latest", "selected"]:
                branch_dict = pool_dict.get(branch, {})
                if not branch_dict:
                    continue

                sections.append(f"<h3>Branch: {html.escape(branch)}</h3>")
                for crit in sorted(branch_dict.keys()):
                    periods_dict = branch_dict.get(crit, {})
                    rmse_by_year, mse_by_year, rmse_all_vals, mse_all_vals = _compute_yearly_avgs_and_overall(periods_dict)

                    # Yearly table
                    if not rmse_by_year.empty or not mse_by_year.empty:
                        years = sorted(set(rmse_by_year.index.astype(int)).union(set(mse_by_year.index.astype(int))))
                        rows = []
                        for y in years:
                            r = rmse_by_year.get(y, np.nan)
                            m = mse_by_year.get(y, np.nan)
                            rtxt = "" if pd.isna(r) else f"{float(r):.4f}"
                            mtxt = "" if pd.isna(m) else f"{float(m):.4f}"
                            rows.append(f"<tr><td>{y}</td><td>{rtxt}</td><td>{mtxt}</td></tr>")
                        year_table = f"""
                        <table border="1" cellspacing="0" cellpadding="6">
                            <thead><tr><th colspan="3" align="left">{html.escape(crit.upper())} — Yearly Averages</th></tr>
                                   <tr><th>Year</th><th>Avg RMSE (all periods)</th><th>Avg MSE (all periods)</th></tr></thead>
                            <tbody>
                                {''.join(rows)}
                            </tbody>
                        </table>
                        """
                    else:
                        year_table = "<p><i>No data available to compute yearly averages.</i></p>"

                    # Overall stats across ALL periods
                    def _stats(s: pd.Series):
                        s = pd.to_numeric(s, errors="coerce").dropna()
                        if s.empty:
                            return dict(avg="", median="", total="")
                        return dict(
                            avg=f"{s.mean():.4f}",
                            median=f"{s.median():.4f}",
                            total=f"{s.sum():.4f}",
                        )

                    rmse_stats = _stats(rmse_all_vals)
                    mse_stats = _stats(mse_all_vals)

                    overall_table = f"""
                    <table border="1" cellspacing="0" cellpadding="6">
                        <thead><tr><th colspan="4" align="left">{html.escape(crit.upper())} — Overall (all periods)</th></tr></thead>
                        <tbody>
                            <tr><td><b>Metric</b></td><td><b>Average</b></td><td><b>Median</b></td><td><b>Total</b></td></tr>
                            <tr><td>RMSE</td><td>{rmse_stats['avg']}</td><td>{rmse_stats['median']}</td><td>{rmse_stats['total']}</td></tr>
                            <tr><td>MSE</td><td>{mse_stats['avg']}</td><td>{mse_stats['median']}</td><td>{mse_stats['total']}</td></tr>
                        </tbody>
                    </table>
                    """

                    sections.append(f"<h4>Criterion: {html.escape(crit.upper())}</h4>")
                    sections.append(year_table)
                    sections.append(overall_table)

        # ---------- Write HTML ----------
        safe_name = re.sub(r"[^a-zA-Z0-9._-]+", "_", spec_name.strip()) or "spec_summary"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Normalize output_path: accept directory or file path
        if output_path is None or not str(output_path).strip():
            output_path = f"{safe_name}.html"
        else:
            output_path = os.path.expanduser(str(output_path))
            # If it's an existing dir, or has no .html/.htm suffix, treat as a directory
            is_dir_target = os.path.isdir(output_path)
            has_html_ext = os.path.splitext(output_path)[1].lower() in {".html", ".htm"}
            if is_dir_target or not has_html_ext:
                os.makedirs(output_path, exist_ok=True) if is_dir_target else os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
                # choose directory base
                target_dir = output_path if is_dir_target else (os.path.dirname(output_path) or ".")
                output_path = os.path.join(target_dir, f"{safe_name}_{timestamp}.html")
            else:
                # ensure parent exists
                os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

        html_doc = f"""<!doctype html>
        <html>
        <head>
            <meta charset="utf-8" />
            <title>{html.escape(spec_name)} – Spec Summary</title>
            <style>
                body {{ font-family: Arial, Helvetica, sans-serif; margin: 24px; }}
                h1 {{ margin-bottom: 0.2em; }}
                h2 {{ margin-top: 1.2em; }}
                table {{ border-collapse: collapse; margin: 12px 0; }}
                th, td {{ padding: 6px 10px; }}
                th {{ background: #f2f2f2; }}
                code {{ background: #f6f8fa; padding: 2px 4px; border-radius: 4px; }}
                .section {{
                    text-align: left;
                    background: #e9eef6;
                    font-size: 1.05em;
                }}
            </style>
        </head>
        <body>
            {''.join(sections)}
        </body>
        </html>""".strip()

        # Try writing; if permission blocked, fall back to a temp file
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html_doc)
        except PermissionError:
            fd, tmp_path = tempfile.mkstemp(prefix=f"{safe_name}_", suffix=".html")
            os.close(fd)
            with open(tmp_path, "w", encoding="utf-8") as f:
                f.write(html_doc)
            output_path = tmp_path

        return output_path
