
#%%

from data.nowdata import NOWData
from data.seriesdataclass import Source, Series, GroupSeries

# %%

Test_Data = NOWData("Test_Data") 

Test_Data.add(
    Series(
        name="de_gdp_total_ca_cop_sa",
        description="Germany, Gross Domestic Product, Total, Calendar Adjusted (X-13 ARIMA), Constant Prices, SA (X-13 ARIMA), Chained, EUR",
        category="GDP_quarterly",
        transformation="pch",
        source=Source(
            data="mb",
            variable="denaac1000"
        )
    )
)

# Test_Data.add(
#     GroupSeries(
#         series_dict={
#             "de_cu_manuf_total_avg_sa": ("deprod2001", None),
#             # "de_ifo_bs_motorcv_capacity_bottle_yn": ("deifo_c2911000_tkj_bdu", None),
#         },
#         source_data="mb",
#         component="Quarterly",
#     )
# )


# Test_Data.add(
#     GroupSeries(
#         series_dict={
#             # "ifocast_ip_tot": ("deprod1404", None),
#             "de_ifo_bs_motorcv_climate_avg_sa": ("deifo_c2911000_kld_bdb", None),
#         },
#         source_data="mb",
#         component="Monthly",
#     )
# )


# Test_Data.add(
#     GroupSeries(
#         series_dict={
#             "de_govt_benchmark_5y_yield": ("de5ygov", None),
#         },
#         source_data="mb",
#         component="Daily",
#     )
# )

