import math
import matplotlib.pyplot as plt
import pandas as pd
import os
import numpy as np
from utils.utils import get_formatted_date  # keep if you use it elsewhere
from typing import Dict, Any, Optional

class SavingMixin:

    # -------------------- helpers --------------------

    def _format_for_display(self, df: pd.DataFrame) -> pd.DataFrame:
        """Format floats nicely and replace NaNs with '' for display exports (PNG/HTML)."""
        def _fmt(x):
            if pd.isna(x):
                return ""
            if isinstance(x, (float, np.floating)):
                return f"{x:.4f}"
            return str(x)
        return df.applymap(_fmt)

    def _flatten_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Flatten 2-level MultiIndex columns to 'Quarter\\np#' for nicer CSV/PNG/Excel output.
        Leaves other column types unchanged.
        """
        if isinstance(df.columns, pd.MultiIndex) and df.columns.nlevels == 2:
            flat = [f"{q}\n{p}" for (q, p) in df.columns]
            out = df.copy()
            out.columns = pd.Index(flat, name="Quarter/Period")
            return out
        return df

    def _df_to_pngs(self, df: pd.DataFrame, out_dir: str, base_name: str, max_rows: int = 35) -> None:
        """
        Render a DataFrame as one or more PNGs using matplotlib's table artist.
        Splits into multiple images if there are many rows.
        """
        os.makedirs(out_dir, exist_ok=True)
        display_df = self._format_for_display(df)

        # paginate rows to avoid tiny unreadable tables
        n = len(display_df.index)
        pages = math.ceil(n / max_rows) if n else 1

        for page in range(pages):
            chunk = display_df.iloc[page*max_rows : (page+1)*max_rows]
            # figure size heuristic
            ncols = max(1, len(display_df.columns))
            nrows = max(1, len(chunk.index))
            fig_w = min(20, max(6, 0.9 * ncols))
            fig_h = min(20, max(2.5, 0.6 * nrows))

            fig, ax = plt.subplots(figsize=(fig_w, fig_h))
            ax.axis("off")

            tbl = ax.table(
                cellText=chunk.values,
                colLabels=[str(c) for c in display_df.columns],
                rowLabels=[str(i) for i in chunk.index],
                loc="center",
                cellLoc="center",
            )
            tbl.auto_set_font_size(False)
            tbl.set_fontsize(8)
            tbl.scale(1.1, 1.2)

            # bold header row
            for (row, col), cell in tbl.get_celld().items():
                if row == 0:
                    cell.set_text_props(weight="bold")

            fig.tight_layout()
            suffix = f"_p{page+1}" if pages > 1 else ""
            out_path = os.path.join(out_dir, f"{base_name}{suffix}.png")
            fig.savefig(out_path, dpi=300, bbox_inches="tight")
            plt.close(fig)

    # -------------------- main save --------------------

    def _save_output( 
        self,
        file_path_output: str, 
        spec_name: str,
        period_selection_plots: Optional[Dict[str, Any]],
        average_plots: Optional[Dict[str, Any]],
        rmse_tables: Optional[Dict[str, pd.DataFrame]],
        selected_vars_table: Optional[pd.DataFrame] = None,  # NEW argument
    ) -> None:
        """
        Save artifacts to disk.

        - period_selection_plots[period] -> PNG
        - average_plots[crit][period] -> PNG
        - rmse_tables[crit] -> CSV, LaTeX, HTML, PNG(s), Excel (one workbook for all crits)
        - selected_vars_table -> same exports under 'selected_vars_table/'
        """

        # Root folder for this spec/run
        file_path_output_folder = os.path.join(file_path_output, spec_name)
        os.makedirs(file_path_output_folder, exist_ok=True)

        # -------------------- SELECTION PLOTS --------------------
        if period_selection_plots:
            selection_plots_dir = os.path.join(file_path_output_folder, "period_selection_plots")
            os.makedirs(selection_plots_dir, exist_ok=True)
            for period, selection_fig in period_selection_plots.items():
                fname = f"{spec_name}_{period}_selection.png"
                selection_fig.savefig(os.path.join(selection_plots_dir, fname), dpi=300, bbox_inches="tight")
                plt.close(selection_fig)

        # -------------------- AVERAGE PLOTS --------------------
        if average_plots:
            average_plots_dir = os.path.join(file_path_output_folder, "average_plots")
            for crit, period_avg in average_plots.items():
                crit_dir = os.path.join(average_plots_dir, crit)
                os.makedirs(crit_dir, exist_ok=True)
                if not period_avg:
                    continue

                for period, item in period_avg.items():
                    # item is (fig, ax) or just fig
                    if isinstance(item, tuple) and len(item) == 2:
                        average_fig, _ = item
                    else:
                        average_fig = item

                    fname = f"{spec_name}_{crit}_{period}_average_plot.png"
                    average_fig.savefig(os.path.join(crit_dir, fname), dpi=300, bbox_inches="tight")
                    plt.close(average_fig)

        # -------------------- TABLES: RMSE --------------------
        if rmse_tables:
            tables_root = os.path.join(file_path_output_folder, "rmse_tables")
            os.makedirs(tables_root, exist_ok=True)

            # Excel writer for all crits in one workbook
            xlsx_path = os.path.join(tables_root, "rmse_tables.xlsx")
            try:
                xw = pd.ExcelWriter(xlsx_path, engine="xlsxwriter")
            except Exception:
                xw = pd.ExcelWriter(xlsx_path, engine="openpyxl")

            with xw as writer:
                for crit, df in rmse_tables.items():
                    if not isinstance(df, pd.DataFrame) or df.empty:
                        continue

                    crit_dir = os.path.join(tables_root, crit)
                    os.makedirs(crit_dir, exist_ok=True)

                    # CSV
                    df.to_csv(os.path.join(crit_dir, f"{spec_name}_{crit}_rmse.csv"), encoding="utf-8")

                    # LaTeX
                    df.to_latex(
                        buf=os.path.join(crit_dir, f"{spec_name}_{crit}_rmse.tex"),
                        index=True,
                        na_rep="",
                        float_format=lambda x: f"{x:.4f}" if pd.notnull(x) else "",
                        escape=False,
                        longtable=True,
                        caption=f"{str(crit).upper()} – RMSE",
                        label=f"tab:rmse_{crit}",
                    )

                    # HTML
                    self._format_for_display(df).to_html(
                        os.path.join(crit_dir, f"{spec_name}_{crit}_rmse.html"),
                        index=True,
                        border=0,
                        classes="rmse-table"
                    )

                    # PNG(s)
                    self._df_to_pngs(df, crit_dir, base_name=f"{spec_name}_rmse_{crit}", max_rows=35)

                    # Excel sheet
                    sheet_name = str(crit)[:31].replace("/", "_").replace("\\", "_").replace("*", "_").replace("?", "_").replace("[","(").replace("]",")")
                    df.to_excel(writer, sheet_name=sheet_name, index=True)

        # -------------------- TABLE: SELECTED VARS --------------------
        if isinstance(selected_vars_table, pd.DataFrame) and not selected_vars_table.empty:
            sel_root = os.path.join(file_path_output_folder, "selected_vars_table")
            os.makedirs(sel_root, exist_ok=True)

            # Flatten multi-index columns for prettier files (keeps original df intact)
            flat_df = self._flatten_columns(selected_vars_table)

            # CSV
            flat_df.to_csv(os.path.join(sel_root, f"{spec_name}_selected_vars.csv"), encoding="utf-8")

            # LaTeX
            flat_df.to_latex(
                buf=os.path.join(sel_root, f"{spec_name}_selected_vars.tex"),
                index=True,
                na_rep="",
                float_format=lambda x: f"{x:.4f}" if pd.notnull(x) else "",
                escape=False,
                longtable=True,
                caption="Selected Variables by Quarter and Period",
                label="tab:selected_vars",
            )

            # HTML
            self._format_for_display(flat_df).to_html(
                os.path.join(sel_root, f"{spec_name}_selected_vars.html"),
                index=True,
                border=0,
                classes="selected-vars-table"
            )

            # PNG(s)
            self._df_to_pngs(flat_df, sel_root, base_name=f"{spec_name}_selected_vars", max_rows=35)

            # Excel workbook (single sheet)
            xlsx_path = os.path.join(sel_root, "selected_vars.xlsx")
            try:
                xw = pd.ExcelWriter(xlsx_path, engine="xlsxwriter")
            except Exception:
                xw = pd.ExcelWriter(xlsx_path, engine="openpyxl")
            with xw as writer:
                flat_df.to_excel(writer, sheet_name="selected_vars", index=True)
