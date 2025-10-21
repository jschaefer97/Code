#%%

from data.seriesdataclass import Source, Series, GroupSeries
from data.nowdata import NOWData

#%%

NDv2 = NOWData("NDv2")

# -------------------------------------------------------------------------------------#
# --------------- National Accounts ---------------------------------------------------#
# -------------------------------------------------------------------------------------#

NDv2.add(
    Series(
        name="de_gdp_total_ca_cop_sa",
        description="Germany, Gross Domestic Product, Total, Calendar Adjusted (X-13 ARIMA), Constant Prices, SA (X-13 ARIMA), Chained, EUR",
        component="National_Accounts",
        category="GDP",
        transformation="pch",
        source=Source(
            data="mb",
            variable="denaac1000"
        )
    )
)

# NDv2.add( # NOTE: This series is also in IfoCast. Keep this turned of to easily compare the two datasets.
#     Series(
#         name = "de_trade_export_sa_eur",
#         description = "Germany, Foreign Trade, Total, Export, Calendar Adjusted (X13 JDemetra+), SA (X13 JDemetra+), EUR",
#         component="National_Accounts",
#         category="EXPORT",
#         transformation = "",
#         source = Source(
#             data = "mb",
#             variable = "detrad0692"
#         )
#     )
# )

# NDv2.add( # NOTE: This series is also in IfoCast. Keep this turned of to easily compare the two datasets.
#     Series(
#         name = "de_trade_import_sa_eur",
#         description = "Germany, Foreign Trade, Total, Import, Calendar Adjusted (X13 JDemetra+), SA (X13 JDemetra+), EUR",
#         component="National_Accounts",
#         category="IMPORT",
#         transformation = "",
#         source = Source(
#             data = "mb",
#             variable = "detrad0689"
#         )
#     )
# )

# -------------------------------------------------------------------------------------#
# --------------- Prices and Monetary Variables ---------------------------------------#
# -------------------------------------------------------------------------------------#

NDv2.add(
    GroupSeries(
        series_dict={
            "de_bb_cpi_total_ca_sa": ("buba_mb_137910", "lin"),
            "de_cpi_total_index": ("depric0001", "lin")
        },
        source_data="mb",
        component="Prices_Monetary_Variables",
        category="CPI",
    )
)

NDv2.add(
    GroupSeries(
        series_dict={
            "de_bb_ms_m1_eur": ("buba_mb_154651", "pch"),
            "de_bb_ms_m2_eur": ("buba_mb_154652", "pch"),
            "de_bb_ms_m3_eur": ("buba_mb_154653", "pch"),
        },
        source_data="mb",
        component="Prices_Monetary_Variables",
        category="Money_Supply",
    )
)

NDv2.add(
    GroupSeries(
        series_dict={
            "de_bb_fx_ecb_eur_gbp": ("buba_mb_44193", "pch"), # NOTE: Kept the series. Although it only start in 1999.
            "de_bb_fx_ecb_eur_jpy": ("buba_mb_44185", "pch"), # NOTE: Kept the series. Although it only start in 1999.
            "de_bb_fx_ecb_eur_usd": ("buba_mb_44166", "pch"), # NOTE: Kept the series. Although it only start in 1999.
        },
        source_data="mb",
        component="FinancialMarkets",
        category="ExchangeRates",
    )
)

# -------------------------------------------------------------------------------------#
# --------------- Investment ----------------------------------------------------------#
# -------------------------------------------------------------------------------------#

NDv2.add(
    GroupSeries(
        series_dict={
            "de_ifo_bs_building_bus_expect_6m_sa": ("desurv7757", "lin"),
            "de_ifo_bs_building_climate_avg_sa": ("desurv7759", "lin"),
            "de_ifo_bs_building_constr_avg3m_sa": ("desurv7725", "lin"),
            "de_ifo_bs_building_constr_expect_3m_sa": ("desurv7741", "lin"),
            "de_ifo_bs_building_insuff_funds_yn": ("desurv7735", "lin"),
            "de_ifo_bs_building_lack_orders_yn": ("desurv7739", "lin"),
            "de_ifo_bs_building_obstruction_yn": ("desurv7727", "lin"),
            "de_ifo_bs_building_orders_prev_sa": ("desurv7743", "lin"),
            "de_ifo_bs_building_orders_sa": ("desurv7745", "lin"),
            "de_ifo_bs_building_other_causes_yn": ("desurv7737", "lin"),
            "de_ifo_bs_building_range_orders_avg_sa": ("desurv7747", "lin"),
            "de_ifo_bs_building_shortage_material_yn": ("desurv7731", "lin"),
            "de_ifo_bs_building_situation_sa": ("desurv7755", "lin"),
            "de_ifo_bs_building_weather_yn": ("desurv7733", "lin"),
        },
        source_data="mb",
        component="Investment",
        category="Ifo_BS",
        subcategory="Construction"
    )
)

NDv2.add(
    GroupSeries(
        series_dict={
            "de_ifo_bs_capgoods_bus_expect_6m_sa": ("deifo_c00000b0_ges_bdb", "lin"),
            "de_ifo_bs_capgoods_capacity_bottle_yn": ("deifo_c00000b0_tkj_bdu", "lin"),
            "de_ifo_bs_capgoods_climate_avg_sa": ("desurv1233", "lin"),
            "de_ifo_bs_capgoods_demand_prev_sa": ("deifo_c00000b0_avs_bdb", "lin"),
            "de_ifo_bs_capgoods_fg_inventory_sa": ("deifo_c00000b0_lus_bdb", "lin"),
            "de_ifo_bs_capgoods_financing_bottle_yn": ("deifo_c00000b0_fej_bdu", "lin"),
            "de_ifo_bs_capgoods_foreign_orders_sa": ("deifo_c00000b0_xus_bdb", "lin"),
            "de_ifo_bs_capgoods_labour_bottle_yn": ("deifo_c00000b0_arj_bdu", "lin"),
            "de_ifo_bs_capgoods_lack_orders_yn": ("deifo_c00000b0_afj_bdu", "lin"),
            "de_ifo_bs_capgoods_material_shortage_yn": ("deifo_c00000b0_maj_bdu", "lin"),
            "de_ifo_bs_capgoods_obstruction_yn": ("deifo_c00000b0_bhj_bdu", "lin"),
            "de_ifo_bs_capgoods_obstructive_yn": ("deifo_c00000b0_auj_bdu", "lin"),
            "de_ifo_bs_capgoods_orders_prev_sa": ("deifo_c00000b0_bvs_bdb", "lin"),
            "de_ifo_bs_capgoods_orders_sa": ("desurv1217", "lin"),
            "de_ifo_bs_capgoods_prod_expect_3m_sa": ("deifo_c00000b0_qes_bdb", "lin"),
            "de_ifo_bs_capgoods_prod_prev_sa": ("deifo_c00000b0_qvs_bdb", "lin"),
            "de_ifo_bs_capgoods_situation_sa": ("deifo_c00000b0_gus_bdb", "lin"),
        },
        source_data="mb",
        component="Investment",
        category="Ifo_BS",
        subcategory="CapitalGoods"
    )
)

NDv2.add(
    GroupSeries(
        series_dict={
            "de_ifo_bs_civil_bus_expect_6m_sa": ("desurv7721", "lin"),
            "de_ifo_bs_civil_climate_avg_sa": ("desurv7723", "lin"),
            "de_ifo_bs_civil_constr_avg3m_sa": ("desurv7689", "lin"),
            "de_ifo_bs_civil_constr_expect_3m_sa": ("desurv7705", "lin"),
            "de_ifo_bs_civil_insuff_funds_yn": ("desurv7699", "lin"),
            "de_ifo_bs_civil_lack_orders_yn": ("desurv7703", "lin"),
            "de_ifo_bs_civil_obstruction_yn": ("desurv7691", "lin"),
            "de_ifo_bs_civil_orders_prev_sa": ("desurv7707", "lin"),
            "de_ifo_bs_civil_orders_sa": ("desurv7709", "lin"),
            "de_ifo_bs_civil_other_causes_yn": ("desurv7701", "lin"),
            "de_ifo_bs_civil_range_orders_avg_sa": ("desurv7711", "lin"),
            "de_ifo_bs_civil_shortage_material_yn": ("desurv7695", "lin"),
            "de_ifo_bs_civil_situation_sa": ("desurv7719", "lin"),
            "de_ifo_bs_civil_weather_yn": ("desurv7697", "lin"),
        },
        source_data="mb",
        component="Investment",
        category="Ifo_BS",
        subcategory="CivilEngineering"
    )
)

NDv2.add(
    GroupSeries(
        series_dict={
            "de_ifo_bs_commercial_bus_expect_6m_sa": ("desurv7901", "lin"),
            "de_ifo_bs_commercial_climate_avg_sa": ("desurv7903", "lin"),
            "de_ifo_bs_commercial_constr_avg3m_sa": ("desurv7869", "lin"),
            "de_ifo_bs_commercial_constr_expect_3m_sa": ("desurv7885", "lin"),
            "de_ifo_bs_commercial_insuff_funds_yn": ("desurv7879", "lin"),
            "de_ifo_bs_commercial_lack_orders_yn": ("desurv7883", "lin"),
            "de_ifo_bs_commercial_obstruction_yn": ("desurv7871", "lin"),
            "de_ifo_bs_commercial_orders_prev_sa": ("desurv7887", "lin"),
            "de_ifo_bs_commercial_orders_sa": ("desurv7889", "lin"),
            "de_ifo_bs_commercial_other_causes_yn": ("desurv7881", "lin"),
            "de_ifo_bs_commercial_range_orders_avg_sa": ("desurv7891", "lin"),
            "de_ifo_bs_commercial_shortage_material_yn": ("desurv7875", "lin"),
            "de_ifo_bs_commercial_situation_sa": ("desurv7899", "lin"),
            "de_ifo_bs_commercial_weather_yn": ("desurv7877", "lin"),
        },
        source_data="mb",
        component="Investment",
        category="Ifo_BS",
        subcategory="CommercialBuilding"
    )
)

NDv2.add(
    GroupSeries(
        series_dict={
            "de_ifo_bs_leasing_bus_expect_6m_sa": ("desurv00262", "lin"),
            "de_ifo_bs_leasing_capacity_bottle_yn": ("desurv00752", "lin"),
            "de_ifo_bs_leasing_climate_avg_sa": ("desurv00264", "lin"),
            "de_ifo_bs_leasing_demand_sa": ("desurv00256", "lin"),
            "de_ifo_bs_leasing_financing_bottle_yn": ("desurv00753", "lin"),
            "de_ifo_bs_leasing_lack_demand_yn": ("desurv00750", "lin"),
            "de_ifo_bs_leasing_lack_employees_sa": ("desurv00751", "lin"),
            "de_ifo_bs_leasing_lack_space_yn": ("desurv00754", "lin"),
            "de_ifo_bs_leasing_obstruction_yn": ("desurv00749", "lin"),
            "de_ifo_bs_leasing_obstructive_yn": ("desurv00756", "lin"),
            "de_ifo_bs_leasing_orders_sa": ("desurv00252", "lin"),
            "de_ifo_bs_leasing_situation_sa": ("desurv00244", "lin"),
        },
        source_data="mb",
        component="Investment",
        category="Ifo_BS",
        subcategory="FinancialLeasing"
    )
)

NDv2.add(
    GroupSeries(
        series_dict={
            "de_ifo_bs_machinery_bus_expect_6m_sa": ("deifo_c2800000_ges_bdb", "lin"),
            "de_ifo_bs_machinery_capacity_bottle_yn": ("deifo_c2800000_tkj_bdu", "lin"),
            "de_ifo_bs_machinery_climate_avg_sa": ("deifo_c2800000_kld_bdb", "lin"),
            "de_ifo_bs_machinery_demand_prev_sa": ("deifo_c2800000_avs_bdb", "lin"),
            "de_ifo_bs_machinery_fg_inventory_sa": ("deifo_c2800000_lus_bdb", "lin"),
            "de_ifo_bs_machinery_financing_bottle_yn": ("deifo_c2800000_fej_bdu", "lin"),
            "de_ifo_bs_machinery_foreign_orders_sa": ("deifo_c2800000_xus_bdb", "lin"),
            "de_ifo_bs_machinery_labour_bottle_yn": ("deifo_c2800000_arj_bdu", "lin"),
            "de_ifo_bs_machinery_lack_orders_yn": ("deifo_c2800000_afj_bdu", "lin"),
            "de_ifo_bs_machinery_material_shortage_yn": ("deifo_c2800000_maj_bdu", "lin"),
            "de_ifo_bs_machinery_obstruction_yn": ("deifo_c2800000_bhj_bdu", "lin"),
            "de_ifo_bs_machinery_obstructive_yn": ("deifo_c2800000_auj_bdu", "lin"),
            "de_ifo_bs_machinery_orders_prev_sa": ("deifo_c2800000_bvs_bdb", "lin"),
            "de_ifo_bs_machinery_orders_sa": ("deifo_c2800000_bus_bdb", "lin"),
            "de_ifo_bs_machinery_prod_expect_3m_sa": ("deifo_c2800000_qes_bdb", "lin"),
            "de_ifo_bs_machinery_prod_prev_sa": ("deifo_c2800000_qvs_bdb", "lin"),
            "de_ifo_bs_machinery_situation_sa": ("deifo_c2800000_gus_bdb", "lin"),
        },
        source_data="mb",
        component="Investment",
        category="Ifo_BS",
        subcategory="Machinery"
    )
)

NDv2.add(
    GroupSeries(
        series_dict={
            "de_ifo_bs_motor_bus_expect_6m_sa": ("deifo_c2900000_ges_bdb", "lin"),
            "de_ifo_bs_motor_capacity_bottle_yn": ("deifo_c2900000_tkj_bdu", "lin"),
            "de_ifo_bs_motor_climate_avg_sa": ("deifo_c2900000_kld_bdb", "lin"),
            "de_ifo_bs_motor_demand_prev_sa": ("deifo_c2900000_avs_bdb", "lin"),
            "de_ifo_bs_motor_fg_inventory_sa": ("deifo_c2900000_lus_bdb", "lin"),
            "de_ifo_bs_motor_financing_bottle_yn": ("deifo_c2900000_fej_bdu", "lin"),
            "de_ifo_bs_motor_foreign_orders_sa": ("deifo_c2900000_xus_bdb", "lin"),
            "de_ifo_bs_motor_labour_bottle_yn": ("deifo_c2900000_arj_bdu", "lin"),
            "de_ifo_bs_motor_lack_orders_yn": ("deifo_c2900000_afj_bdu", "lin"),
            "de_ifo_bs_motor_material_shortage_yn": ("deifo_c2900000_maj_bdu", "lin"),
            "de_ifo_bs_motor_obstruction_yn": ("deifo_c2900000_bhj_bdu", "lin"),
            "de_ifo_bs_motor_obstructive_yn": ("deifo_c2900000_auj_bdu", "lin"),
            "de_ifo_bs_motor_orders_prev_sa": ("deifo_c2900000_bvs_bdb", "lin"),
            "de_ifo_bs_motor_orders_sa": ("deifo_c2900000_bus_bdb", "lin"),
            "de_ifo_bs_motor_prod_expect_3m_sa": ("deifo_c2900000_qes_bdb", "lin"),
            "de_ifo_bs_motor_prod_prev_sa": ("deifo_c2900000_qvs_bdb", "lin"),
            "de_ifo_bs_motor_situation_sa": ("deifo_c2900000_gus_bdb", "lin"),
        },
        source_data="mb",
        component="Investment",
        category="Ifo_BS",
        subcategory="MotorVehicles"
    )
)

NDv2.add(
    GroupSeries(
        series_dict={
            "de_ifo_bs_othercivil_bus_expect_6m_sa": ("desurv7829", "lin"),
            "de_ifo_bs_othercivil_climate_avg_sa": ("desurv7831", "lin"),
            "de_ifo_bs_othercivil_constr_avg3m_sa": ("desurv7797", "lin"),
            "de_ifo_bs_othercivil_constr_expect_3m_sa": ("desurv7813", "lin"),
            "de_ifo_bs_othercivil_insuff_funds_yn": ("desurv7807", "lin"),
            "de_ifo_bs_othercivil_lack_orders_yn": ("desurv7811", "lin"),
            "de_ifo_bs_othercivil_obstruction_yn": ("desurv7799", "lin"),
            "de_ifo_bs_othercivil_orders_prev_sa": ("desurv7815", "lin"),
            "de_ifo_bs_othercivil_orders_sa": ("desurv7817", "lin"),
            "de_ifo_bs_othercivil_other_causes_yn": ("desurv7809", "lin"),
            "de_ifo_bs_othercivil_range_orders_avg_sa": ("desurv7819", "lin"),
            "de_ifo_bs_othercivil_shortage_material_yn": ("desurv7803", "lin"),
            "de_ifo_bs_othercivil_situation_sa": ("desurv7827", "lin"),
            "de_ifo_bs_othercivil_weather_yn": ("desurv7805", "lin"),
        },
        source_data="mb",
        component="Investment",
        category="Ifo_BS",
        subcategory="OtherCivilEngineering"
    )
)

NDv2.add(
    GroupSeries(
        series_dict={
            "de_ifo_bs_public_bus_expect_6m_sa": ("desurv7865", "lin"),
            "de_ifo_bs_public_climate_avg_sa": ("desurv7867", "lin"),
            "de_ifo_bs_public_constr_avg3m_sa": ("desurv7833", "lin"),
            "de_ifo_bs_public_constr_expect_3m_sa": ("desurv7849", "lin"),
            "de_ifo_bs_public_insuff_funds_yn": ("desurv7843", "lin"),
            "de_ifo_bs_public_lack_orders_yn": ("desurv7847", "lin"),
            "de_ifo_bs_public_obstruction_yn": ("desurv7835", "lin"),
            "de_ifo_bs_public_orders_prev_sa": ("desurv7851", "lin"),
            "de_ifo_bs_public_orders_sa": ("desurv7853", "lin"),
            "de_ifo_bs_public_other_causes_yn": ("desurv7845", "lin"),
            "de_ifo_bs_public_range_orders_avg_sa": ("desurv7855", "lin"),
            "de_ifo_bs_public_shortage_material_yn": ("desurv7839", "lin"),
            "de_ifo_bs_public_situation_sa": ("desurv7863", "lin"),
            "de_ifo_bs_public_weather_yn": ("desurv7841", "lin"),
        },
        source_data="mb",
        component="Investment",
        category="Ifo_BS",
        subcategory="PublicBuildingConstruction"
    )
)

NDv2.add(
    GroupSeries(
        series_dict={
            "de_ifo_bs_residential_bus_expect_6m_sa": ("desurv7937", "lin"),
            "de_ifo_bs_residential_climate_avg_sa": ("desurv7939", "lin"),
            "de_ifo_bs_residential_constr_avg3m_sa": ("desurv7905", "lin"),
            "de_ifo_bs_residential_constr_expect_3m_sa": ("desurv7921", "lin"),
            "de_ifo_bs_residential_insuff_funds_yn": ("desurv7915", "lin"),
            "de_ifo_bs_residential_lack_orders_yn": ("desurv7919", "lin"),
            "de_ifo_bs_residential_obstruction_yn": ("desurv7907", "lin"),
            "de_ifo_bs_residential_orders_prev_sa": ("desurv7923", "lin"),
            "de_ifo_bs_residential_orders_sa": ("desurv7925", "lin"),
            "de_ifo_bs_residential_other_causes_yn": ("desurv7917", "lin"),
            "de_ifo_bs_residential_shortage_material_yn": ("desurv7911", "lin"),
            "de_ifo_bs_residential_situation_sa": ("desurv7935", "lin"),
            "de_ifo_bs_residential_weather_yn": ("desurv7913", "lin"),
        },
        source_data="mb",
        component="Investment",
        category="Ifo_BS",
        subcategory="ResidentialConstruction"
    )
)

NDv2.add(
    GroupSeries(
        series_dict={
            "de_ip_goods_capital_total_ca_sa": ("deprod1350", "pch"),
            "de_ip_goods_capital_ex_motor_ca_sa": ("deprod3715", "pch"),
            "de_ip_goods_capital_ex_other_ca_sa": ("deprod3720", "pch"),
            "de_ip_goods_capital_ex_motor_other_ca_sa": ("deprod3725", "pch"),
            "de_ip_goods_consumer_ca_sa": ("deprod1365", "pch"),
            "de_ip_goods_intermediate_ca_sa": ("deprod1345", "pch"),
            # "de_ip_total_ca_sa": ("deprod1404", "pch"), # NOTE: This series is also in IfoCast. Keep this turned of to easily compare the two datasets.
            "de_ip_total_ex_energy_const_ca_sa": ("deprod1375", "pch"),
        },
        source_data="mb",
        component="Investment",
        category="Industrial_Production",
        subcategory="By_Goods_Type"
    )
)

NDv2.add(
    GroupSeries(
        series_dict={
            # "de_no_dom_total_ca_sa": ("deprod2113", "pch"), # NOTE: This series is also in IfoCast. Keep this turned of to easily compare the two datasets.
            "de_no_dom_goods_capital_ca_sa": ("deprod2158", "pch"),
            "de_no_dom_goods_cap_ex_major_ca_sa": ("deprod2500", "pch"),
            "de_no_dom_chemicals_ca_sa": ("deprod2668", "pch"),
            "de_no_dom_basic_metals_ca_sa": ("deprod2708", "pch"),
            "de_no_dom_fab_metal_ca_sa": ("deprod2728", "pch"),
            "de_no_dom_comp_elecopt_ca_sa": ("deprod2748", "pch"),
            "de_no_dom_machinery_eq_ca_sa": ("deprod2787", "pch"),
            "de_no_dom_motor_vehicles_ca_sa": ("deprod1775", "pch"),
            "de_no_dom_electrical_eq_ca_sa": ("deprod1429", "pch"),
            "de_no_dom_other_transport_ca_sa": ("deprod2815", "pch"),
        },
        source_data="mb",
        component="Investment",
        category="New_Orders",
        subcategory="Domestic"
    )
)

NDv2.add(
    GroupSeries(
        series_dict={
            "de_ps_turnover_manuf_dom_ca_sa": ("detrad3415", "pch"),
            "de_ps_turnover_capital_dom_ca_sa": ("detrad1904", "pch"),
            "de_ps_turnover_chemicals_dom_ca_sa": ("detrad4745", "pch"),
            "de_ps_turnover_comp_elecopt_dom_ca_sa": ("detrad4775", "pch"),
            "de_ps_turnover_fab_metal_dom_ca_sa": ("detrad4770", "pch"),
            "de_ps_turnover_machinery_eq_dom_ca_sa": ("detrad4785", "pch"),
            "de_ps_turnover_electrical_eq_dom_ca_sa": ("detrad4780", "pch"),
            "de_ps_turnover_motor_vehicles_dom_ca_sa": ("detrad4789", "pch"),
            "de_ps_turnover_other_transport_dom_ca_sa": ("detrad4794", "pch"),
        },
        source_data="mb",
        component="Investment",
        category="Production_Sales",
        subcategory="Domestic_Turnover"
    )
)

NDv2.add(
    GroupSeries(
        series_dict={
            "de_so_manu_dom_total_ca_sa": ("deprod2928", "pch"),
            "de_so_manu_dom_goods_capital_ca_sa": ("deprod2930", "pch"),
            "de_so_manu_dom_chemicals_ca_sa": ("deprod3252", "pch"),
            "de_so_manu_dom_basic_metals_ca_sa": ("deprod3254", "pch"),
            "de_so_manu_dom_comp_elec_eq_ca_sa": ("deprod2943", "pch"), # NOTE: Non-stationary - check if it can be made stationary.
            "de_so_manu_dom_electrical_eq_ca_sa": ("deprod3257", "pch"),
            "de_so_manu_dom_motor_vehicles_ca_sa": ("deprod3259", "pch"),
            "de_so_manu_dom_other_transport_eq_ca_sa": ("deprod3260", "pch"),
            "de_so_manu_dom_transport_eq_ca_sa": ("deprod2944", "pch"),
        },
        source_data="mb",
        component="Investment",
        category="Stock_of_Orders",
        subcategory="Domestic"
    )
)

NDv2.add(
    Series(
        name = "de_li_tax_turnover_early_ca_sa",
        description = "Germany, Leading Indicators, German Federal Statistical Office (Statistisches Bundesamt), Early Indicator, Advance Turnover Tax Returns of the Non-Financial Business Economy, Calendar Adjusted (X13 JDemetra+), Constant Prices, SA (X13 JDemetra+), Index",
        component="Investment",
        category = "Leading_Indicators",
        source = Source(
            data = "mb",
            variable = "delead0008"
        )
    )
)

NDv2.add(
    GroupSeries(
        series_dict={
            "de_so_manu_dom_transport_eq_ca_sa": ("deprod2944", "pch"),
            "de_so_manu_total_ca_sa": ("deprod2907", "pch"),
        },
        source_data="mb",
        component="Investment",
        category="Stock_of_Orders",
        subcategory="Transport_Equipment"
    )
)

NDv2.add(
    GroupSeries(
        series_dict={
            # Demand & Inventory
            "de_ifo_bs_motorcv_demand_prev_sa": ("desurv6113", "lin"),
            "de_ifo_bs_motorcv_foreign_orders_sa": ("desurv6127", "lin"),
            "de_ifo_bs_motorcv_fg_inventory_sa": ("desurv6111", "lin"),

            # # Bottlenecks & Obstructions
            # "de_ifo_bs_motorcv_financing_bottle_yn": ("deifo_c2911000_fej_bdu", "lin"), # NOTE: Difference to the NDv0
            # "de_ifo_bs_motorcv_labour_bottle_yn": ("deifo_c2911000_arj_bdu", "lin"),
            # "de_ifo_bs_motorcv_material_shortage_yn": ("deifo_c2911000_maj_bdu", "lin"),
            # "de_ifo_bs_motorcv_obstruction_yn": ("deifo_c2911000_bhj_bdu", "lin"),
            # "de_ifo_bs_motorcv_obstructive_yn": ("deifo_c2911000_auj_bdu", "lin"),
            # "de_ifo_bs_motorcv_capacity_bottle_yn": ("deifo_c2911000_tkj_bdu", "lin"),

            # # Sentiment
            # "de_ifo_bs_motorcv_lack_orders_yn": ("deifo_c2911000_afj_bdu", "lin"),
            "de_ifo_bs_motorcv_climate_avg_sa": ("deifo_c2911000_kld_bdb", "lin"),
            "de_ifo_bs_motorcv_situation_sa": ("deifo_c2911000_gus_bdb", "lin"),
            "de_ifo_bs_motorcv_bus_expect_6m_sa": ("deifo_c2911000_ges_bdb", "lin"),

            # Orders & Production
            "de_ifo_bs_motorcv_orders_prev_sa": ("desurv6115", "lin"),
            "de_ifo_bs_motorcv_orders_sa": ("desurv6117", "lin"),
            "de_ifo_bs_motorcv_prod_expect_3m_sa": ("desurv6121", "lin"),
            "de_ifo_bs_motorcv_prod_prev_sa": ("desurv6109", "lin"),
        },
        source_data="mb",
        component="Investment",
        category="Ifo_BS",
        subcategory="Motor_Vehicles_Commercial"
    )
)


NDv2.add(
    GroupSeries(
        series_dict={
            "de_cu_manuf_capital_avg_sa": ("deprod2007", "pch"),
            "de_cu_manuf_total_avg_sa": ("deprod2001", "pch"),
        },
        source_data="mb",
        component="Investment",
        category="Capacity_Utilization",
        subcategory="Manufacturing"
    )
)

NDv2.add( # NOTE: Put this to Netexport?
    GroupSeries(
        series_dict={
            "de_dt_vehicle_reg_commercial": ("detrad1805", "pch"),
            "de_dt_vehicle_reg_motor_pc": ("detrad1800", "pch"),
        },
        source_data="mb",
        component="Investment",
        category="Domestic_Trade",
        subcategory="Vehicle_Registrations"
    )
)

NDv2.add( # NOTE: Maybe put this together with other uncertainty indices?
    GroupSeries(
        series_dict={
            "de_epu_news_index": ("deepunnewsindex", "lin"),
            "de_epu_wui_index": ("dewui", "lin"),
        },
        source_data="mb",
        component="Investment",
        category="Economic_Uncertainty",
        subcategory="EPU_Indices"
    )
)

NDv2.add(
    Series(
        name = "de_es_dihk_investment_balance",
        description = "Germany, Economic Surveys, DIHK, Economic Survey, Enterprises' Investment Intentions Balance",
        component="Investment",
        category = "DIHK_BS",
        transformation = "",
        source = Source(
            data = "mb",
            variable = "desurv0405"
        )
    )
)

NDv2.add(
    GroupSeries(
        series_dict={
            "de_dgecf_bs_n_construction_build_3m": ("buil_de_tot_1_bs_m", "lin"),
            "de_dgecf_bs_n_construction_employ_3m": ("buil_de_tot_4_bs_m", "lin"),
            "de_dgecf_bs_n_construction_orders": ("buil_de_tot_3_bs_m", "lin"),
            "de_dgecf_bs_n_construction_prices_3m": ("buil_de_tot_5_bs_m", "lin")
        },
        source_data="mb",
        component="Investment",
        category="Construction",
        subcategory="Construction surveys and orders"
    )
)

NDv2.add(
    GroupSeries( # NOTE: Error in the release period. Check if this can be fixed by manually adjusting the series releaese periods. Would be interesting to see how good this indicator is.
        series_dict={
            "de_sme_turnover_mom": ("debust2428", "lin"), 
            "de_sme_employment_mom": ("debust2446", "lin"),
            "de_sme_wages_mom": ("debust2437", "lin")
        },
        source_data="mb",
        component="Investment",
        category="SME_Incidators",
        subcategory="Datev_SME_Indicators"
    )
)


# -------------------------------------------------------------------------------------#
# --------------- Labor Market --------------------------------------------------------#
# -------------------------------------------------------------------------------------#

# NDv2.add(
#     GroupSeries(
#         series_dict={
#             "de_employment_socialsec_temp_hrprov_sa": ("delama0075", None),
#             "de_employment_socialsec_accommodation_food_sa": ("delama0071", None),
#             "de_employment_socialsec_agriculture_sa": ("delama0065", None), # NOTE: Non-stationary - check if it can be made stationary.
#             "de_employment_socialsec_arts_household_services_sa": ("delama0080", None),
#             "de_employment_socialsec_education_sa": ("delama0077", None),
#             "de_employment_socialsec_finance_insurance_sa": ("delama0073", None),
#             "de_employment_socialsec_healthcare_sa": ("delama0078", None),
#             "de_employment_socialsec_info_comm_sa": ("delama0072", None),
#             "de_employment_socialsec_manufacturing_sa": ("delama0067", None),
#             "de_employment_socialsec_realestate_scientific_admin_sa": ("delama0074", None),
#             "de_employment_socialsec_transportation_sa": ("delama0070", None),
#             "de_employment_socialsec_trade_vehicles_sa": ("delama0069", None),
#             "de_employment_socialsec_utilities_sa": ("delama0066", None)
#         },
#         source_data="mb",
#         component="Labormarket",
#         category="Employment",
#         subcategory="SocialSecurity_BySector"
#     )
# )

# NDv2.add(
#     GroupSeries(
#         series_dict={
#             "de_employment_total_domestic_employees_sa": ("delama1317", None),
#             "de_employment_total_resident_sa": ("delama1314", None),
#             "de_employment_total_ilo_trend_sa": ("delama1320", None),
#         },
#         source_data="mb",
#         component="Labormarket",
#         category="Employment",
#         subcategory="Total_Resident_Domestic"
#     )
# )

# NDv2.add(
#     Series(
#         name = "de_iab_unemployment_index",
#         description = "Germany, IAB Labor Market Barometer, Component A, Unemployment, Index",
#         component="Labormarket",
#         category="IAB_Barometer",
#         transformation = "",
#         source = Source(
#             data = "mb",
#             variable = "delama0003"
#         )
#     )
# )

# NDv2.add(
#     Series(
#         name = "de_ifo_emp_barometer_sa",
#         description = "Germany, Business Surveys, Ifo, Employment Barometer, Total, SA, Index",
#         component="Labormarket",
#         category="Ifo_BS",
#         subcategory="EmploymentBarometer",
#         transformation = "",
#         source = Source(
#             data = "mb",
#             variable = "desurv0340"
#         )
#     )
# )

# NDv2.add(
#     GroupSeries(
#         series_dict={
#             "de_ifo_emp_expect_constr_sa": ("desurv7681", None),
#             "de_ifo_emp_expect_mfg_sa": ("desurv1148", None),
#             "de_ifo_emp_expect_services_sa": ("desurv8719", None),
#         },
#         source_data="mb",
#         component="Labormarket",
#         category="Ifo_BS",
#         subcategory="EmploymentExpectations_Sectoral"
#     )
# )

# NDv2.add(
#     GroupSeries(
#         series_dict={
#             "de_ifo_overtime_yes_sa": ("deifo_c0000000_u1j_bds", None),
#             "de_ifo_overtime_customary_yes_sa": ("deifo_c0000000_u2j_bds", None),
#             "de_ifo_shorttime_yes_sa": ("deifo_c0000000_k1j_bds", None),
#             "de_ifo_shorttime_expect_yes_sa": ("deifo_c0000000_k2j_bds", None),
#         },
#         source_data="mb",
#         component="Labormarket",
#         category="Ifo_BS",
#         subcategory="Overtime_ShortTimeWork"
#     )
# )

# NDv2.add(
#     Series(
#         name = "de_labor_shortage_index",
#         description = "Germany, Labor Market Indicators, Labor Shortage Index",
#         component="Labormarket",
#         category="Labor_Shortage_Index",
#         transformation = "",
#         source = Source(
#             data = "mb",
#             variable = "delama0314"
#         )
#     )
# )

# NDv2.add(
#     GroupSeries(
#         series_dict={
#             "de_unemployment_total_ilo": ("delama1302", None),
#             "de_unemployment_total_ilo_trend_sa": ("delama1321", None),
#             "de_unemployment_total_wider_sa": ("delama0033", None),
#             "de_unemployment_longterm": ("delama1101", None),
#             "de_unemployment_shortterm": ("delama1100", None),
#             "de_unemployment_code_ii_total": ("delama1091", None), # NOTE: Non-stationary - check if it can be made stationary.
#             "de_unemployment_code_iii_total": ("delama1082", None),
#         },
#         source_data="mb",
#         component="Labormarket",
#         category="Unemployment",
#         subcategory="Total_AndByDuration"
#     )
# )

# NDv2.add(
#     GroupSeries(
#         series_dict={
#             "de_unemployment_foreigners_total": ("delama1049", None),
#             "de_unemployment_germans_total": ("delama1040", None),
#             "de_unemployment_rate_civilian_lf_sa": ("delama0822", None),
#             "de_unemployment_total_sa": ("delama0817", None),
#             "de_unemployment_rate_ilo_trend_sa": ("delama1322", None),
#             "de_unemployment_expectations": ("cons2_de_tot_7_bs_m", None),
#         },
#         source_data="mb",
#         component="Labormarket",
#         category="Unemployment",
#         subcategory="ByNationality_AndExpectations"
#     )
# )

# NDv2.add(
#     GroupSeries(
#         series_dict={
#             "de_underemployment_excl_shortwork": ("delama0035", None),
#             "de_underemployment_strict_sa": ("delama0034", None),
#             "de_tariff_hourly_index": ("deinea0832", None), # NOTE: Non-stationary - check if it can be made stationary.
#             "de_tariff_hourly_special_index": ("deinea0961", None),
#         },
#         source_data="mb",
#         component="Labormarket",
#         category="EmploymentAdjustments",
#         subcategory="ShortTime_Underemployment_Tariff"
#     )
# )

# NDv2.add(
#     GroupSeries(
#         series_dict={
#             "de_vacancies_total_sa": ("delama1501", None),
#             "de_indeed_jpi_total_sa": ("ind_de_job_tot", None),
#             # "de_vacancies_sa_idx": ("delama0016", None), # NOTE: This series is also in IfoCast. Keep this turned of to easily compare the two datasets.
#         },
#         source_data="mb",
#         component="Labormarket",
#         category="Productivity",
#         subcategory="UnitLaborCost"
#     )
# )

# NDv2.add(
#     GroupSeries(
#         series_dict={
#             "de_wages_growth_3mma_yoy": ("deineaindwt3m", None),
#             "de_wages_growth_yoy": ("deineaindwtyoy", None),
#         },
#         source_data="mb",
#         component="Labormarket",
#         category="Wages",
#         subcategory="Growth_JobPostings"
#     )
# )

# NDv2.add(
#     GroupSeries(
#         series_dict={
#             "de_bb_employment_lowpaid_sa": ("buba_mb_66280", None),
#             "de_bb_employment_lowpaid_unadj": ("buba_mb_66290", None),
#         },
#         source_data="mb",
#         component="Labormarket",
#         category="Employment",
#         subcategory="LowPaid"
#     )
# )

# -------------------------------------------------------------------------------------#
# --------------- Net Export ----------------------------------------------------------#
# -------------------------------------------------------------------------------------#

NDv2.add(
    GroupSeries(
        series_dict={
            # "de_ifo_bs_mfg_export_expect_3m_sa": ("desurv1142", None), # NOTE: This series is also in IfoCast. Keep this turned of to easily compare the two datasets.
            "de_ifo_bs_mfg_foreign_orders_sa": ("deifo_c0000000_xus_bdb", "pch")
        },
        source_data="mb",
        component="Netexport",
        category="Ifo_BS",
        subcategory="Exports_Expectations"
    )
)

NDv2.add(
    GroupSeries(
        series_dict={
            "de_new_orders_construction_sa": ("deprod1633", "pch"),
            "de_new_orders_foreign_exmajor_idx": ("deprod2473", "pch"),
            "de_new_orders_foreign_exveh_idx": ("deprod2825", "pch"),
            "de_new_orders_ea_exveh_idx": ("deprod2834", "pch")
        },
        source_data="mb",
        component="Netexport",
        category="NewOrders",
        subcategory="Manufacturing"
    )
)

NDv2.add(
    GroupSeries(
        series_dict={
            "de_export_price_idx": ("depric4691", "pch"),
            "de_import_price_idx": ("depric4690", "pch")
        },
        source_data="mb",
        component="Netexport",
        category="Prices",
        subcategory="TradePrices"
    )
)

NDv2.add( # NOTE: Error in the release period. Check if this can be fixed by manually adjusting the series release periods. Would be interesting to see how good this indicator is.
    Series(
        name = "de_pmi_sa_idx",
        description = "Germany, Business Surveys, S&P Global, Manufacturing, Manufacturing PMI, SA, Index",
        component="Netexport",
        category="SPGlobal",
        subcategory="PMI_Germany",
        transformation = "",
        source = Source(
            data = "mb",
            variable = "markit_3y_pmidemanpm"
        )
    )
)

NDv2.add(
    GroupSeries(
        series_dict={
            "ea20_capacity_util_mfg": ("euprod0507", "pch"),
            "us_capacity_util_sa": ("usprod1071", "pch"),
            "cn_capacity_util_total": ("cnprod0910", "pch")
        },
        source_data="mb",
        component="Netexport",
        category="ProductionCapacity",
        subcategory="CapacityUtilization_Foreign"
    )
)

# NDv2.add( # NOTE: This series is also in IfoCast. Keep this turned of to easily compare the two datasets.
#     Series(
#         name = "world_trade_volume_idx",
#         description = "World, Foreign Trade, CPB World Trade Monitor, Total, Volume, SA, Index",
#         component="Netexport",
#         category="WorldTrade",
#         transformation = "",
#         source = Source(
#             data = "mb",
#             variable = "worldtrad0001"
#         )
#     )
# )

# -------------------------------------------------------------------------------------#
# --------------- Private Consumption -------------------------------------------------#
# -------------------------------------------------------------------------------------#

NDv2.add(
    GroupSeries(
        series_dict={
            "de_dgecfin_cc_confidence_balance_sa": ("cons2_de_tot_cof_bs_m", "lin"),
            "de_dgecfin_cc_econ_sit_12mo_sa": ("cons2_de_tot_4_bs_m", "lin"),
            "de_dgecfin_cc_fin_sit_12mo_sa": ("cons2_de_tot_2_bs_m", "lin"),
            "de_dgecfin_cc_household_fin_statement_sa": ("cons2_de_tot_12_bs_m", "lin"),
            "de_dgecfin_cc_major_purchases_now_sa": ("cons2_de_tot_8_bs_m", "lin"),
            "de_dgecfin_cc_major_purchases_12mo_sa": ("cons2_de_tot_9_bs_m", "lin"),
            "de_dgecfin_cc_price_dev_12mo": ("cons2_de_tot_6_b_m", "lin")
        },
        source_data="mb",
        component="Privconsumption",
        category="DGECFIN_CS",
        subcategory="DGECFIN_Confidence"
    )
)

NDv2.add(
    GroupSeries(
        series_dict={
            "de_dgecfin_cc_buy_car_12mo": ("cons2_de_tot_13_b_q", "lin"),
            "de_dgecfin_cc_buy_home_12mo": ("cons2_de_tot_14_b_q", "lin"),
            "de_dgecfin_cc_home_improve_12mo": ("cons2_de_tot_15_b_q", "lin")
        },
        source_data="mb",
        component="Privconsumption",
        category="DGECFIN_CS",
        subcategory="DGECFIN_Intentions"
    )
)

NDv2.add(
    GroupSeries(
        series_dict={
            "de_gfk_climate_indicator": ("desurv0029", "lin"),
            "de_gfk_econ_expectations": ("desurv0026", "lin"),
            "de_gfk_income_expectations": ("desurv0027", "lin"),
            "de_gfk_willingness_buy": ("desurv0028", "lin")
        },
        source_data="mb",
        component="Privconsumption",
        category="GfK_CS",
    )
)

NDv2.add(
    GroupSeries(
        series_dict={
            "de_hde_total_index": ("desurv01062", "lin"),
            "de_hde_income_expectations_index": ("desurv01063", "lin"),
            "de_hde_willingness_buy_index": ("desurv01064", "lin"), # NOTE: Non-stationary - check if it can be made stationary.
            "de_hde_price_expectations_index": ("desurv01066", "lin"),
            "de_hde_econ_expectations_index": ("desurv01067", "lin"),
            "de_hde_interest_expectations_index": ("desurv01068", "lin")
        },
        source_data="mb",
        component="Privconsumption",
        category="HDE_ConsumerBarometer",
    )
)

NDv2.add(
    GroupSeries(
        series_dict={ 
            # "de_dt_retail_turnover_sa": ("detrad1360", "lin"), # NOTE: This series is also in IfoCast. Keep this turned of to easily compare the two datasets.
            "de_dt_services_turnover_sa": ("detrad3845", "lin"),
        },
        source_data="mb",
        component="Privconsumption",
        category="Turnover",
        subcategory="Retail_Services"
    )
)

# -------------------------------------------------------------------------------------#
# --------------- Financial -----------------------------------------------------------#
# -------------------------------------------------------------------------------------#

# NDv2.add(
#     GroupSeries(
#         series_dict={
#             "de_zew_es_automobile_balance": ("desurv0068", "pch"),
#             "de_zew_es_banks_balance": ("desurv0066", "pch"),
#             "de_zew_es_chemicals_balance": ("desurv0069", "pch"),
#             "de_zew_es_construction_balance": ("desurv0074", "pch"),
#             "de_zew_es_current_balance": ("desurv0018", "pch"),
#             "de_zew_es_electronics_balance": ("desurv0071", "pch"),
#             # "de_zew_es_expect_balance": ("desurv0017", "pch"), # NOTE: This series is also in IfoCast. Keep this turned of to easily compare the two datasets.
#             "de_zew_es_insurance_balance": ("desurv0067", "pch"),
#             "de_zew_es_it_balance": ("desurv0078", "pch"), # NOTE: Kept the series. Although it only start in 1999.
#             "de_zew_es_mechanical_balance": ("desurv0072", "pch"),
#             "de_zew_es_retail_balance": ("desurv0073", "pch"), 
#             "de_zew_es_services_balance": ("desurv0076", "pch"), # NOTE: Kept the series. Although it only start in 1999.
#             "de_zew_es_steel_balance": ("desurv0070", "pch"),
#             "de_zew_es_telecom_balance": ("desurv0077", "pch"),
#             "de_zew_es_utilities_balance": ("desurv0075", "pch"),
#         },
#         source_data="mb",
#         component="FinancialMarkets",
#         category="ZEW_ES",
#         subcategory="ZEW_Balance_Indicators"
#     )
# )

# NDv2.add( # NOTE: Add more yields
#     GroupSeries(
#         series_dict={
#             "us_govt_benchmark_5y_yield": ("us05ygov", "pch"),
#             "de_govt_benchmark_5y_yield": ("de5ygov", "pch"),
#             "it_govt_benchmark_5y_yield": ("it5ygov", "pch"),
#             "de_govt_benchmark_yield10y": ("de10ygov_m", "pch")
#         },
#         source_data="mb",
#         component="FinancialMarkets",
#         category="GovtYields",
#     )
# )

# NDv2.add(
#     Series(
#         name="ea_ecb_reuters_euribor3m_avg",
#         description="Euro Area, ECB, Financial Market Provider: Reuters, Money Market, EURIBOR 3-Month, Historical Close, Average of Period",
#         component="FinancialMarkets",
#         category="EURIBOR",
#         transformation="",
#         source=Source(
#             data="mb",
#             variable="ecb_00858138"
#         )
#     )
# )


# -------------------------------------------------------------------------------------#
# --------------- IfoCast -------------------------------------------------------------#
# -------------------------------------------------------------------------------------#

NDv2.add(
    GroupSeries(
        series_dict={
            "ifocast_ip_tot": ("deprod1404", "pch"),
            "ifocast_to_energy": ("detrad3364", "pch"),
            "ifocast_to_retail": ("detrad1360", "pch"),
            "ifocast_to_hosp": ("detrad3877", "pch"),
            "ifocast_to_wholesale": ("detrad8150", "pch"),
            "ifocast_no_tot_manu": ("deprod2112", "pch"),
            "ifocast_no_dom_manu": ("deprod2113", "pch"),
            "ifocast_ifo_trade_indus": ("desurv0006", "pch"), # NOTE: Difference to the NDv1
            "ifocast_ifo_manu": ("desurv1142", "lin"),
            "ifocast_ifo_exp_climate": ("desurv0344", "lin"),
            "ifocast_ifo_manu_ordchange": ("deifo_f4010300_bvsa_bdu", "lin"),
            "ifocast_ifo_wholesale_exp": ("deifo_g4600010_ges_bds", "lin"),
            "ifocast_zew_fmr": ("desurv0017", "lin"),
            "ifocast_lt_unf_vac": ("delama0016", "lin"),
            "ifocast_imp_tot": ("detrad0689", "pch"),
            "ifocast_exp_tot": ("detrad0692", "pch"),
            "ifocast_trade_world": ("worldtrad0001", "pch"),
            "ifocast_inflation": ("depric1962", "pch")
        },
        source_data="mb",
        component="IfoCast",
    )
)




# %%
