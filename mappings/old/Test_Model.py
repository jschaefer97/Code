
#%%

from data.nowdata import NOWData
from data.seriesdataclass import Source, Series, GroupSeries

# %%

Test_Model = NOWData("Test_Model") 

Test_Model.add(
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

# Test_Model.add(
#     GroupSeries(
#         series_dict={
#             "de_cu_manuf_total_avg_sa": ("deprod2001", None),
#             "de_ifo_bs_motorcv_capacity_bottle_yn": ("deifo_c2911000_tkj_bdu", None),
#         },
#         source_data="mb",
#         component="Quarterly",
#     )
# )

# Test_Model.add(
#     GroupSeries(
#         series_dict={
#             "de_ifo_bs_motor_bus_expect_6m_sa": ("deifo_c2900000_ges_bdb", None),
#             "de_ifo_bs_motor_capacity_bottle_yn": ("deifo_c2900000_tkj_bdu", None),
#             "de_ifo_bs_motor_climate_avg_sa": ("deifo_c2900000_kld_bdb", None),
#             "de_ifo_bs_motor_demand_prev_sa": ("deifo_c2900000_avs_bdb", None),
#             "de_ifo_bs_motor_fg_inventory_sa": ("deifo_c2900000_lus_bdb", None),
#             "de_ifo_bs_motor_financing_bottle_yn": ("deifo_c2900000_fej_bdu", None),
#             "de_ifo_bs_motor_foreign_orders_sa": ("deifo_c2900000_xus_bdb", None),
#             "de_ifo_bs_motor_labour_bottle_yn": ("deifo_c2900000_arj_bdu", None),
#             "de_ifo_bs_motor_lack_orders_yn": ("deifo_c2900000_afj_bdu", None),
#             "de_ifo_bs_motor_material_shortage_yn": ("deifo_c2900000_maj_bdu", None),
#         },
#         source_data="mb",
#         component="Investment",
#         category="Ifo_BS",
#         subcategory="MotorVehicles"
#     )
# )

Test_Model.add(
    GroupSeries(
        series_dict={
            "ifocast_ip_tot": ("deprod1404", None),
            # "de_ifo_bs_motorcv_climate_avg_sa": ("deifo_c2911000_kld_bdb", None),
        },
        source_data="mb",
        category="Industrial Production",
    )
)


Test_Model.add(
    GroupSeries(
        series_dict={
            "Ifo_business_climate": ("desurv01046", None),
            # "de_ifo_bs_motorcv_climate_avg_sa": ("deifo_c2911000_kld_bdb", None),
        },
        source_data="mb",
        category="Ifo_business_climate",
    )
)



# Test_Model.add(
#     GroupSeries(
#         series_dict={
#             "de_govt_benchmark_5y_yield": ("de5ygov", None),
#         },
#         source_data="mb",
#         component="Daily",
#     )
# )
