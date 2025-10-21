from loguru import logger

def get_model_grid_dict():
    """
    Generate fixed lag index grids with NO HOLES (prefix-consecutive blocks).

    Index layout (column positions in X *excluding* y_var itself):
      - y lags:            [0, 1, 2, 3]        (4 lags)
      - monthly x lags:    [4, ..., 15]        (12 lags)
      - quarterly x lags:  [4, ..., 7]         (4 lags)

    We only allow blocks that start at the first available lag and extend
    consecutively (prefix). That is:
      y-block length k_y  -> indices [0, 1, ..., k_y-1]
      m-block length k_m  -> indices [4, ..., 4+k_m-1]
      q-block length k_q  -> indices [4, ..., 4+k_q-1]

    Monthly grid size  : 4 * 12 = 48
    Quarterly grid size: 4 * 4  = 16
    """
    # ----- Monthly: all prefix lengths -----
    monthly_grid = []
    for y_len in range(1, 4 + 1):                     # 1..4 y-lags
        y_block = list(range(0, y_len))
        for m_len in range(1, 12 + 1):                # 1..12 monthly lags
            m_block = list(range(4, 4 + m_len))
            monthly_grid.append(tuple(y_block + m_block))

    # ----- Quarterly: all prefix lengths -----
    quarterly_grid = []
    for y_len in range(1, 4 + 1):                     # 1..4 y-lags
        y_block = list(range(0, y_len))
        for q_len in range(1, 4 + 1):                 # 1..4 quarterly lags
            q_block = list(range(4, 4 + q_len))
            quarterly_grid.append(tuple(y_block + q_block))

    return {
        "monthly_grid": monthly_grid,
        "quarterly_grid": quarterly_grid,
    }
