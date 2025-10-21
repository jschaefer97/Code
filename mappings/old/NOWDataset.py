#%%

from data.seriesdataclass import Source, Series, GroupSeries
from data.nowdata import NOWData

#%%

NOWDataset = NOWData("NOWDataset")

# -------------------------------------------------------------------------------------#
# --------------- National Accounts ---------------------------------------------------#
# -------------------------------------------------------------------------------------#

NOWDataset.add(
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

# NOWDataset.add( # NOTE: This series is also in IfoCast. Keep this turned of to easily compare the two datasets.
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

# NOWDataset.add( # NOTE: This series is also in IfoCast. Keep this turned of to easily compare the two datasets.
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

NOWDataset.add(
    GroupSeries(
        series_dict={
            "de_bb_cpi_total_ca_sa": ("buba_mb_137910", None),
            "de_cpi_total_index": ("depric0001", None)
        },
        source_data="mb",
        component="Prices_Monetary_Variables",
        category="CPI",
    )
)

NOWDataset.add(
    GroupSeries(
        series_dict={
            "de_bb_ms_m1_eur": ("buba_mb_154651", None),
            "de_bb_ms_m2_eur": ("buba_mb_154652", None),
            "de_bb_ms_m3_eur": ("buba_mb_154653", None),
        },
        source_data="mb",
        component="Prices_Monetary_Variables",
        category="Money_Supply",
    )
)

NOWDataset.add(
    GroupSeries(
        series_dict={
            "de_bb_fx_ecb_eur_gbp": ("buba_mb_44193", None), # NOTE: Kept the series. Although it only start in 1999.
            "de_bb_fx_ecb_eur_jpy": ("buba_mb_44185", None), # NOTE: Kept the series. Although it only start in 1999.
            "de_bb_fx_ecb_eur_usd": ("buba_mb_44166", None), # NOTE: Kept the series. Although it only start in 1999.
        },
        source_data="mb",
        component="FinancialMarkets",
        category="ExchangeRates",
    )
)

# -------------------------------------------------------------------------------------#
# --------------- Investment ----------------------------------------------------------#
# -------------------------------------------------------------------------------------#

NOWDataset.add(
    GroupSeries(
        series_dict={
            "de_ifo_bs_building_bus_expect_6m_sa": ("desurv7757", None),
            "de_ifo_bs_building_climate_avg_sa": ("desurv7759", None),
            "de_ifo_bs_building_constr_avg3m_sa": ("desurv7725", None),
            "de_ifo_bs_building_constr_expect_3m_sa": ("desurv7741", None),
            "de_ifo_bs_building_insuff_funds_yn": ("desurv7735", None),
            "de_ifo_bs_building_lack_orders_yn": ("desurv7739", None),
            "de_ifo_bs_building_obstruction_yn": ("desurv7727", None),
            "de_ifo_bs_building_orders_prev_sa": ("desurv7743", None),
            "de_ifo_bs_building_orders_sa": ("desurv7745", None),
            "de_ifo_bs_building_other_causes_yn": ("desurv7737", None),
            "de_ifo_bs_building_range_orders_avg_sa": ("desurv7747", None),
            "de_ifo_bs_building_shortage_material_yn": ("desurv7731", None),
            "de_ifo_bs_building_situation_sa": ("desurv7755", None),
            "de_ifo_bs_building_weather_yn": ("desurv7733", None),
        },
        source_data="mb",
        component="Investment",
        category="Ifo_BS",
        subcategory="Construction"
    )
)

NOWDataset.add(
    GroupSeries(
        series_dict={
            "de_ifo_bs_capgoods_bus_expect_6m_sa": ("deifo_c00000b0_ges_bdb", None),
            "de_ifo_bs_capgoods_capacity_bottle_yn": ("deifo_c00000b0_tkj_bdu", None),
            "de_ifo_bs_capgoods_climate_avg_sa": ("desurv1233", None),
            "de_ifo_bs_capgoods_demand_prev_sa": ("deifo_c00000b0_avs_bdb", None),
            "de_ifo_bs_capgoods_fg_inventory_sa": ("deifo_c00000b0_lus_bdb", None),
            "de_ifo_bs_capgoods_financing_bottle_yn": ("deifo_c00000b0_fej_bdu", None),
            "de_ifo_bs_capgoods_foreign_orders_sa": ("deifo_c00000b0_xus_bdb", None),
            "de_ifo_bs_capgoods_labour_bottle_yn": ("deifo_c00000b0_arj_bdu", None),
            "de_ifo_bs_capgoods_lack_orders_yn": ("deifo_c00000b0_afj_bdu", None),
            "de_ifo_bs_capgoods_material_shortage_yn": ("deifo_c00000b0_maj_bdu", None),
            "de_ifo_bs_capgoods_obstruction_yn": ("deifo_c00000b0_bhj_bdu", None),
            "de_ifo_bs_capgoods_obstructive_yn": ("deifo_c00000b0_auj_bdu", None),
            "de_ifo_bs_capgoods_orders_prev_sa": ("deifo_c00000b0_bvs_bdb", None),
            "de_ifo_bs_capgoods_orders_sa": ("desurv1217", None),
            "de_ifo_bs_capgoods_prod_expect_3m_sa": ("deifo_c00000b0_qes_bdb", None),
            "de_ifo_bs_capgoods_prod_prev_sa": ("deifo_c00000b0_qvs_bdb", None),
            "de_ifo_bs_capgoods_situation_sa": ("deifo_c00000b0_gus_bdb", None),
        },
        source_data="mb",
        component="Investment",
        category="Ifo_BS",
        subcategory="CapitalGoods"
    )
)

NOWDataset.add(
    GroupSeries(
        series_dict={
            "de_ifo_bs_civil_bus_expect_6m_sa": ("desurv7721", None),
            "de_ifo_bs_civil_climate_avg_sa": ("desurv7723", None),
            "de_ifo_bs_civil_constr_avg3m_sa": ("desurv7689", None),
            "de_ifo_bs_civil_constr_expect_3m_sa": ("desurv7705", None),
            "de_ifo_bs_civil_insuff_funds_yn": ("desurv7699", None),
            "de_ifo_bs_civil_lack_orders_yn": ("desurv7703", None),
            "de_ifo_bs_civil_obstruction_yn": ("desurv7691", None),
            "de_ifo_bs_civil_orders_prev_sa": ("desurv7707", None),
            "de_ifo_bs_civil_orders_sa": ("desurv7709", None),
            "de_ifo_bs_civil_other_causes_yn": ("desurv7701", None),
            "de_ifo_bs_civil_range_orders_avg_sa": ("desurv7711", None),
            "de_ifo_bs_civil_shortage_material_yn": ("desurv7695", None),
            "de_ifo_bs_civil_situation_sa": ("desurv7719", None),
            "de_ifo_bs_civil_weather_yn": ("desurv7697", None),
        },
        source_data="mb",
        component="Investment",
        category="Ifo_BS",
        subcategory="CivilEngineering"
    )
)

NOWDataset.add(
    GroupSeries(
        series_dict={
            "de_ifo_bs_commercial_bus_expect_6m_sa": ("desurv7901", None),
            "de_ifo_bs_commercial_climate_avg_sa": ("desurv7903", None),
            "de_ifo_bs_commercial_constr_avg3m_sa": ("desurv7869", None),
            "de_ifo_bs_commercial_constr_expect_3m_sa": ("desurv7885", None),
            "de_ifo_bs_commercial_insuff_funds_yn": ("desurv7879", None),
            "de_ifo_bs_commercial_lack_orders_yn": ("desurv7883", None),
            "de_ifo_bs_commercial_obstruction_yn": ("desurv7871", None),
            "de_ifo_bs_commercial_orders_prev_sa": ("desurv7887", None),
            "de_ifo_bs_commercial_orders_sa": ("desurv7889", None),
            "de_ifo_bs_commercial_other_causes_yn": ("desurv7881", None),
            "de_ifo_bs_commercial_range_orders_avg_sa": ("desurv7891", None),
            "de_ifo_bs_commercial_shortage_material_yn": ("desurv7875", None),
            "de_ifo_bs_commercial_situation_sa": ("desurv7899", None),
            "de_ifo_bs_commercial_weather_yn": ("desurv7877", None),
        },
        source_data="mb",
        component="Investment",
        category="Ifo_BS",
        subcategory="CommercialBuilding"
    )
)

NOWDataset.add(
    GroupSeries(
        series_dict={
            "de_ifo_bs_leasing_bus_expect_6m_sa": ("desurv00262", None),
            "de_ifo_bs_leasing_capacity_bottle_yn": ("desurv00752", None),
            "de_ifo_bs_leasing_climate_avg_sa": ("desurv00264", None),
            "de_ifo_bs_leasing_demand_sa": ("desurv00256", None),
            "de_ifo_bs_leasing_financing_bottle_yn": ("desurv00753", None),
            "de_ifo_bs_leasing_lack_demand_yn": ("desurv00750", None),
            "de_ifo_bs_leasing_lack_employees_sa": ("desurv00751", None),
            "de_ifo_bs_leasing_lack_space_yn": ("desurv00754", None),
            "de_ifo_bs_leasing_obstruction_yn": ("desurv00749", None),
            "de_ifo_bs_leasing_obstructive_yn": ("desurv00756", None),
            "de_ifo_bs_leasing_orders_sa": ("desurv00252", None),
            "de_ifo_bs_leasing_situation_sa": ("desurv00244", None),
        },
        source_data="mb",
        component="Investment",
        category="Ifo_BS",
        subcategory="FinancialLeasing"
    )
)

NOWDataset.add(
    GroupSeries(
        series_dict={
            "de_ifo_bs_machinery_bus_expect_6m_sa": ("deifo_c2800000_ges_bdb", None),
            "de_ifo_bs_machinery_capacity_bottle_yn": ("deifo_c2800000_tkj_bdu", None),
            "de_ifo_bs_machinery_climate_avg_sa": ("deifo_c2800000_kld_bdb", None),
            "de_ifo_bs_machinery_demand_prev_sa": ("deifo_c2800000_avs_bdb", None),
            "de_ifo_bs_machinery_fg_inventory_sa": ("deifo_c2800000_lus_bdb", None),
            "de_ifo_bs_machinery_financing_bottle_yn": ("deifo_c2800000_fej_bdu", None),
            "de_ifo_bs_machinery_foreign_orders_sa": ("deifo_c2800000_xus_bdb", None),
            "de_ifo_bs_machinery_labour_bottle_yn": ("deifo_c2800000_arj_bdu", None),
            "de_ifo_bs_machinery_lack_orders_yn": ("deifo_c2800000_afj_bdu", None),
            "de_ifo_bs_machinery_material_shortage_yn": ("deifo_c2800000_maj_bdu", None),
            "de_ifo_bs_machinery_obstruction_yn": ("deifo_c2800000_bhj_bdu", None),
            "de_ifo_bs_machinery_obstructive_yn": ("deifo_c2800000_auj_bdu", None),
            "de_ifo_bs_machinery_orders_prev_sa": ("deifo_c2800000_bvs_bdb", None),
            "de_ifo_bs_machinery_orders_sa": ("deifo_c2800000_bus_bdb", None),
            "de_ifo_bs_machinery_prod_expect_3m_sa": ("deifo_c2800000_qes_bdb", None),
            "de_ifo_bs_machinery_prod_prev_sa": ("deifo_c2800000_qvs_bdb", None),
            "de_ifo_bs_machinery_situation_sa": ("deifo_c2800000_gus_bdb", None),
        },
        source_data="mb",
        component="Investment",
        category="Ifo_BS",
        subcategory="Machinery"
    )
)

NOWDataset.add(
    GroupSeries(
        series_dict={
            "de_ifo_bs_motor_bus_expect_6m_sa": ("deifo_c2900000_ges_bdb", None),
            "de_ifo_bs_motor_capacity_bottle_yn": ("deifo_c2900000_tkj_bdu", None),
            "de_ifo_bs_motor_climate_avg_sa": ("deifo_c2900000_kld_bdb", None),
            "de_ifo_bs_motor_demand_prev_sa": ("deifo_c2900000_avs_bdb", None),
            "de_ifo_bs_motor_fg_inventory_sa": ("deifo_c2900000_lus_bdb", None),
            "de_ifo_bs_motor_financing_bottle_yn": ("deifo_c2900000_fej_bdu", None),
            "de_ifo_bs_motor_foreign_orders_sa": ("deifo_c2900000_xus_bdb", None),
            "de_ifo_bs_motor_labour_bottle_yn": ("deifo_c2900000_arj_bdu", None),
            "de_ifo_bs_motor_lack_orders_yn": ("deifo_c2900000_afj_bdu", None),
            "de_ifo_bs_motor_material_shortage_yn": ("deifo_c2900000_maj_bdu", None),
            "de_ifo_bs_motor_obstruction_yn": ("deifo_c2900000_bhj_bdu", None),
            "de_ifo_bs_motor_obstructive_yn": ("deifo_c2900000_auj_bdu", None),
            "de_ifo_bs_motor_orders_prev_sa": ("deifo_c2900000_bvs_bdb", None),
            "de_ifo_bs_motor_orders_sa": ("deifo_c2900000_bus_bdb", None),
            "de_ifo_bs_motor_prod_expect_3m_sa": ("deifo_c2900000_qes_bdb", None),
            "de_ifo_bs_motor_prod_prev_sa": ("deifo_c2900000_qvs_bdb", None),
            "de_ifo_bs_motor_situation_sa": ("deifo_c2900000_gus_bdb", None),
        },
        source_data="mb",
        component="Investment",
        category="Ifo_BS",
        subcategory="MotorVehicles"
    )
)

NOWDataset.add(
    GroupSeries(
        series_dict={
            "de_ifo_bs_othercivil_bus_expect_6m_sa": ("desurv7829", None),
            "de_ifo_bs_othercivil_climate_avg_sa": ("desurv7831", None),
            "de_ifo_bs_othercivil_constr_avg3m_sa": ("desurv7797", None),
            "de_ifo_bs_othercivil_constr_expect_3m_sa": ("desurv7813", None),
            "de_ifo_bs_othercivil_insuff_funds_yn": ("desurv7807", None),
            "de_ifo_bs_othercivil_lack_orders_yn": ("desurv7811", None),
            "de_ifo_bs_othercivil_obstruction_yn": ("desurv7799", None),
            "de_ifo_bs_othercivil_orders_prev_sa": ("desurv7815", None),
            "de_ifo_bs_othercivil_orders_sa": ("desurv7817", None),
            "de_ifo_bs_othercivil_other_causes_yn": ("desurv7809", None),
            "de_ifo_bs_othercivil_range_orders_avg_sa": ("desurv7819", None),
            "de_ifo_bs_othercivil_shortage_material_yn": ("desurv7803", None),
            "de_ifo_bs_othercivil_situation_sa": ("desurv7827", None),
            "de_ifo_bs_othercivil_weather_yn": ("desurv7805", None),
        },
        source_data="mb",
        component="Investment",
        category="Ifo_BS",
        subcategory="OtherCivilEngineering"
    )
)

NOWDataset.add(
    GroupSeries(
        series_dict={
            "de_ifo_bs_public_bus_expect_6m_sa": ("desurv7865", None),
            "de_ifo_bs_public_climate_avg_sa": ("desurv7867", None),
            "de_ifo_bs_public_constr_avg3m_sa": ("desurv7833", None),
            "de_ifo_bs_public_constr_expect_3m_sa": ("desurv7849", None),
            "de_ifo_bs_public_insuff_funds_yn": ("desurv7843", None),
            "de_ifo_bs_public_lack_orders_yn": ("desurv7847", None),
            "de_ifo_bs_public_obstruction_yn": ("desurv7835", None),
            "de_ifo_bs_public_orders_prev_sa": ("desurv7851", None),
            "de_ifo_bs_public_orders_sa": ("desurv7853", None),
            "de_ifo_bs_public_other_causes_yn": ("desurv7845", None),
            "de_ifo_bs_public_range_orders_avg_sa": ("desurv7855", None),
            "de_ifo_bs_public_shortage_material_yn": ("desurv7839", None),
            "de_ifo_bs_public_situation_sa": ("desurv7863", None),
            "de_ifo_bs_public_weather_yn": ("desurv7841", None),
        },
        source_data="mb",
        component="Investment",
        category="Ifo_BS",
        subcategory="PublicBuildingConstruction"
    )
)

NOWDataset.add(
    GroupSeries(
        series_dict={
            "de_ifo_bs_residential_bus_expect_6m_sa": ("desurv7937", None),
            "de_ifo_bs_residential_climate_avg_sa": ("desurv7939", None),
            "de_ifo_bs_residential_constr_avg3m_sa": ("desurv7905", None),
            "de_ifo_bs_residential_constr_expect_3m_sa": ("desurv7921", None),
            "de_ifo_bs_residential_insuff_funds_yn": ("desurv7915", None),
            "de_ifo_bs_residential_lack_orders_yn": ("desurv7919", None),
            "de_ifo_bs_residential_obstruction_yn": ("desurv7907", None),
            "de_ifo_bs_residential_orders_prev_sa": ("desurv7923", None),
            "de_ifo_bs_residential_orders_sa": ("desurv7925", None),
            "de_ifo_bs_residential_other_causes_yn": ("desurv7917", None),
            "de_ifo_bs_residential_shortage_material_yn": ("desurv7911", None),
            "de_ifo_bs_residential_situation_sa": ("desurv7935", None),
            "de_ifo_bs_residential_weather_yn": ("desurv7913", None),
        },
        source_data="mb",
        component="Investment",
        category="Ifo_BS",
        subcategory="ResidentialConstruction"
    )
)

NOWDataset.add(
    GroupSeries(
        series_dict={
            "de_ip_goods_capital_total_ca_sa": ("deprod1350", None),
            "de_ip_goods_capital_ex_motor_ca_sa": ("deprod3715", None),
            "de_ip_goods_capital_ex_other_ca_sa": ("deprod3720", None),
            "de_ip_goods_capital_ex_motor_other_ca_sa": ("deprod3725", None),
            "de_ip_goods_consumer_ca_sa": ("deprod1365", None),
            "de_ip_goods_intermediate_ca_sa": ("deprod1345", None),
            # "de_ip_total_ca_sa": ("deprod1404", None), # NOTE: This series is also in IfoCast. Keep this turned of to easily compare the two datasets.
            "de_ip_total_ex_energy_const_ca_sa": ("deprod1375", None),
        },
        source_data="mb",
        component="Investment",
        category="Industrial_Production",
        subcategory="By_Goods_Type"
    )
)

NOWDataset.add(
    GroupSeries(
        series_dict={
            # "de_no_dom_total_ca_sa": ("deprod2113", None), # NOTE: This series is also in IfoCast. Keep this turned of to easily compare the two datasets.
            "de_no_dom_goods_capital_ca_sa": ("deprod2158", None),
            "de_no_dom_goods_cap_ex_major_ca_sa": ("deprod2500", None),
            "de_no_dom_chemicals_ca_sa": ("deprod2668", None),
            "de_no_dom_basic_metals_ca_sa": ("deprod2708", None),
            "de_no_dom_fab_metal_ca_sa": ("deprod2728", None),
            "de_no_dom_comp_elecopt_ca_sa": ("deprod2748", None),
            "de_no_dom_machinery_eq_ca_sa": ("deprod2787", None),
            "de_no_dom_motor_vehicles_ca_sa": ("deprod1775", None),
            "de_no_dom_electrical_eq_ca_sa": ("deprod1429", None),
            "de_no_dom_other_transport_ca_sa": ("deprod2815", None),
        },
        source_data="mb",
        component="Investment",
        category="New_Orders",
        subcategory="Domestic"
    )
)

NOWDataset.add(
    GroupSeries(
        series_dict={
            "de_ps_turnover_manuf_dom_ca_sa": ("detrad3415", None),
            "de_ps_turnover_capital_dom_ca_sa": ("detrad1904", None),
            "de_ps_turnover_chemicals_dom_ca_sa": ("detrad4745", None),
            "de_ps_turnover_comp_elecopt_dom_ca_sa": ("detrad4775", None),
            "de_ps_turnover_fab_metal_dom_ca_sa": ("detrad4770", None),
            "de_ps_turnover_machinery_eq_dom_ca_sa": ("detrad4785", None),
            "de_ps_turnover_electrical_eq_dom_ca_sa": ("detrad4780", None),
            "de_ps_turnover_motor_vehicles_dom_ca_sa": ("detrad4789", None),
            "de_ps_turnover_other_transport_dom_ca_sa": ("detrad4794", None),
        },
        source_data="mb",
        component="Investment",
        category="Production_Sales",
        subcategory="Domestic_Turnover"
    )
)

NOWDataset.add(
    GroupSeries(
        series_dict={
            "de_so_manu_dom_total_ca_sa": ("deprod2928", None),
            "de_so_manu_dom_goods_capital_ca_sa": ("deprod2930", None),
            "de_so_manu_dom_chemicals_ca_sa": ("deprod3252", None),
            "de_so_manu_dom_basic_metals_ca_sa": ("deprod3254", None),
            "de_so_manu_dom_comp_elec_eq_ca_sa": ("deprod2943", None), # NOTE: Non-stationary - check if it can be made stationary.
            "de_so_manu_dom_electrical_eq_ca_sa": ("deprod3257", None),
            "de_so_manu_dom_motor_vehicles_ca_sa": ("deprod3259", None),
            "de_so_manu_dom_other_transport_eq_ca_sa": ("deprod3260", "cch"),
            "de_so_manu_dom_transport_eq_ca_sa": ("deprod2944", None),
        },
        source_data="mb",
        component="Investment",
        category="Stock_of_Orders",
        subcategory="Domestic"
    )
)

NOWDataset.add(
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

NOWDataset.add(
    GroupSeries(
        series_dict={
            "de_so_manu_dom_transport_eq_ca_sa": ("deprod2944", None),
            "de_so_manu_total_ca_sa": ("deprod2907", None),
        },
        source_data="mb",
        component="Investment",
        category="Stock_of_Orders",
        subcategory="Transport_Equipment"
    )
)

NOWDataset.add(
    GroupSeries(
        series_dict={
            # Demand & Inventory
            "de_ifo_bs_motorcv_demand_prev_sa": ("desurv6113", None),
            "de_ifo_bs_motorcv_foreign_orders_sa": ("desurv6127", None),
            "de_ifo_bs_motorcv_fg_inventory_sa": ("desurv6111", None),

            # Bottlenecks & Obstructions
            "de_ifo_bs_motorcv_financing_bottle_yn": ("deifo_c2911000_fej_bdu", None),
            "de_ifo_bs_motorcv_labour_bottle_yn": ("deifo_c2911000_arj_bdu", None),
            "de_ifo_bs_motorcv_material_shortage_yn": ("deifo_c2911000_maj_bdu", None),
            "de_ifo_bs_motorcv_obstruction_yn": ("deifo_c2911000_bhj_bdu", None),
            "de_ifo_bs_motorcv_obstructive_yn": ("deifo_c2911000_auj_bdu", None),
            "de_ifo_bs_motorcv_capacity_bottle_yn": ("deifo_c2911000_tkj_bdu", None),

            # Sentiment
            "de_ifo_bs_motorcv_lack_orders_yn": ("deifo_c2911000_afj_bdu", None),
            "de_ifo_bs_motorcv_climate_avg_sa": ("deifo_c2911000_kld_bdb", None),
            "de_ifo_bs_motorcv_situation_sa": ("deifo_c2911000_gus_bdb", None),
            "de_ifo_bs_motorcv_bus_expect_6m_sa": ("deifo_c2911000_ges_bdb", None),

            # Orders & Production
            "de_ifo_bs_motorcv_orders_prev_sa": ("desurv6115", None),
            "de_ifo_bs_motorcv_orders_sa": ("desurv6117", None),
            "de_ifo_bs_motorcv_prod_expect_3m_sa": ("desurv6121", None),
            "de_ifo_bs_motorcv_prod_prev_sa": ("desurv6109", None),
        },
        source_data="mb",
        component="Investment",
        category="Ifo_BS",
        subcategory="Motor_Vehicles_Commercial"
    )
)


NOWDataset.add(
    GroupSeries(
        series_dict={
            "de_cu_manuf_capital_avg_sa": ("deprod2007", None),
            "de_cu_manuf_total_avg_sa": ("deprod2001", None),
        },
        source_data="mb",
        component="Investment",
        category="Capacity_Utilization",
        subcategory="Manufacturing"
    )
)

NOWDataset.add( # NOTE: Put this to Netexport?
    GroupSeries(
        series_dict={
            "de_dt_vehicle_reg_commercial": ("detrad1805", None),
            "de_dt_vehicle_reg_motor_pc": ("detrad1800", None),
        },
        source_data="mb",
        component="Investment",
        category="Domestic_Trade",
        subcategory="Vehicle_Registrations"
    )
)

NOWDataset.add( # NOTE: Maybe put this together with other uncertainty indices?
    GroupSeries(
        series_dict={
            "de_epu_news_index": ("deepunnewsindex", None),
            "de_epu_wui_index": ("dewui", None),
        },
        source_data="mb",
        component="Investment",
        category="Economic_Uncertainty",
        subcategory="EPU_Indices"
    )
)

NOWDataset.add(
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

NOWDataset.add(
    GroupSeries(
        series_dict={
            "de_dgecf_bs_n_construction_build_3m": ("buil_de_tot_1_bs_m", None),
            "de_dgecf_bs_n_construction_employ_3m": ("buil_de_tot_4_bs_m", None),
            "de_dgecf_bs_n_construction_orders": ("buil_de_tot_3_bs_m", None),
            "de_dgecf_bs_n_construction_prices_3m": ("buil_de_tot_5_bs_m", None)
        },
        source_data="mb",
        component="Investment",
        category="Construction",
        subcategory="Construction surveys and orders"
    )
)

NOWDataset.add(
    GroupSeries( # NOTE: Error in the release period. Check if this can be fixed by manually adjusting the series releaese periods. Would be interesting to see how good this indicator is.
        series_dict={
            "de_sme_turnover_mom": ("debust2428", None), 
            "de_sme_employment_mom": ("debust2446", None),
            "de_sme_wages_mom": ("debust2437", None)
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

NOWDataset.add(
    GroupSeries(
        series_dict={
            "de_employment_socialsec_temp_hrprov_sa": ("delama0075", None),
            "de_employment_socialsec_accommodation_food_sa": ("delama0071", None),
            "de_employment_socialsec_agriculture_sa": ("delama0065", None), # NOTE: Non-stationary - check if it can be made stationary.
            "de_employment_socialsec_arts_household_services_sa": ("delama0080", None),
            "de_employment_socialsec_education_sa": ("delama0077", None),
            "de_employment_socialsec_finance_insurance_sa": ("delama0073", None),
            "de_employment_socialsec_healthcare_sa": ("delama0078", None),
            "de_employment_socialsec_info_comm_sa": ("delama0072", None),
            "de_employment_socialsec_manufacturing_sa": ("delama0067", None),
            "de_employment_socialsec_realestate_scientific_admin_sa": ("delama0074", None),
            "de_employment_socialsec_transportation_sa": ("delama0070", None),
            "de_employment_socialsec_trade_vehicles_sa": ("delama0069", None),
            "de_employment_socialsec_utilities_sa": ("delama0066", None)
        },
        source_data="mb",
        component="Labormarket",
        category="Employment",
        subcategory="SocialSecurity_BySector"
    )
)

NOWDataset.add(
    GroupSeries(
        series_dict={
            "de_employment_total_domestic_employees_sa": ("delama1317", None),
            "de_employment_total_resident_sa": ("delama1314", None),
            "de_employment_total_ilo_trend_sa": ("delama1320", None),
        },
        source_data="mb",
        component="Labormarket",
        category="Employment",
        subcategory="Total_Resident_Domestic"
    )
)

NOWDataset.add(
    Series(
        name = "de_iab_unemployment_index",
        description = "Germany, IAB Labor Market Barometer, Component A, Unemployment, Index",
        component="Labormarket",
        category="IAB_Barometer",
        transformation = "",
        source = Source(
            data = "mb",
            variable = "delama0003"
        )
    )
)

NOWDataset.add(
    Series(
        name = "de_ifo_emp_barometer_sa",
        description = "Germany, Business Surveys, Ifo, Employment Barometer, Total, SA, Index",
        component="Labormarket",
        category="Ifo_BS",
        subcategory="EmploymentBarometer",
        transformation = "",
        source = Source(
            data = "mb",
            variable = "desurv0340"
        )
    )
)

NOWDataset.add(
    GroupSeries(
        series_dict={
            "de_ifo_emp_expect_constr_sa": ("desurv7681", None),
            "de_ifo_emp_expect_mfg_sa": ("desurv1148", None),
            "de_ifo_emp_expect_services_sa": ("desurv8719", None),
        },
        source_data="mb",
        component="Labormarket",
        category="Ifo_BS",
        subcategory="EmploymentExpectations_Sectoral"
    )
)

NOWDataset.add(
    GroupSeries(
        series_dict={
            "de_ifo_overtime_yes_sa": ("deifo_c0000000_u1j_bds", None),
            "de_ifo_overtime_customary_yes_sa": ("deifo_c0000000_u2j_bds", None),
            "de_ifo_shorttime_yes_sa": ("deifo_c0000000_k1j_bds", None),
            "de_ifo_shorttime_expect_yes_sa": ("deifo_c0000000_k2j_bds", None),
        },
        source_data="mb",
        component="Labormarket",
        category="Ifo_BS",
        subcategory="Overtime_ShortTimeWork"
    )
)

NOWDataset.add(
    Series(
        name = "de_labor_shortage_index",
        description = "Germany, Labor Market Indicators, Labor Shortage Index",
        component="Labormarket",
        category="Labor_Shortage_Index",
        transformation = "",
        source = Source(
            data = "mb",
            variable = "delama0314"
        )
    )
)

NOWDataset.add(
    GroupSeries(
        series_dict={
            "de_unemployment_total_ilo": ("delama1302", None),
            "de_unemployment_total_ilo_trend_sa": ("delama1321", None),
            "de_unemployment_total_wider_sa": ("delama0033", None),
            "de_unemployment_longterm": ("delama1101", None),
            "de_unemployment_shortterm": ("delama1100", None),
            "de_unemployment_code_ii_total": ("delama1091", None), # NOTE: Non-stationary - check if it can be made stationary.
            "de_unemployment_code_iii_total": ("delama1082", None),
        },
        source_data="mb",
        component="Labormarket",
        category="Unemployment",
        subcategory="Total_AndByDuration"
    )
)

NOWDataset.add(
    GroupSeries(
        series_dict={
            "de_unemployment_foreigners_total": ("delama1049", None),
            "de_unemployment_germans_total": ("delama1040", None),
            "de_unemployment_rate_civilian_lf_sa": ("delama0822", None),
            "de_unemployment_total_sa": ("delama0817", None),
            "de_unemployment_rate_ilo_trend_sa": ("delama1322", None),
            "de_unemployment_expectations": ("cons2_de_tot_7_bs_m", None),
        },
        source_data="mb",
        component="Labormarket",
        category="Unemployment",
        subcategory="ByNationality_AndExpectations"
    )
)

NOWDataset.add(
    GroupSeries(
        series_dict={
            "de_underemployment_excl_shortwork": ("delama0035", None),
            "de_underemployment_strict_sa": ("delama0034", None),
            "de_tariff_hourly_index": ("deinea0832", None), # NOTE: Non-stationary - check if it can be made stationary.
            "de_tariff_hourly_special_index": ("deinea0961", None),
        },
        source_data="mb",
        component="Labormarket",
        category="EmploymentAdjustments",
        subcategory="ShortTime_Underemployment_Tariff"
    )
)

NOWDataset.add(
    GroupSeries(
        series_dict={
            "de_vacancies_total_sa": ("delama1501", None),
            "de_indeed_jpi_total_sa": ("ind_de_job_tot", None),
            # "de_vacancies_sa_idx": ("delama0016", None), # NOTE: This series is also in IfoCast. Keep this turned of to easily compare the two datasets.
        },
        source_data="mb",
        component="Labormarket",
        category="Productivity",
        subcategory="UnitLaborCost"
    )
)

NOWDataset.add(
    GroupSeries(
        series_dict={
            "de_wages_growth_3mma_yoy": ("deineaindwt3m", None),
            "de_wages_growth_yoy": ("deineaindwtyoy", None),
        },
        source_data="mb",
        component="Labormarket",
        category="Wages",
        subcategory="Growth_JobPostings"
    )
)

NOWDataset.add(
    GroupSeries(
        series_dict={
            "de_bb_employment_lowpaid_sa": ("buba_mb_66280", None),
            "de_bb_employment_lowpaid_unadj": ("buba_mb_66290", None),
        },
        source_data="mb",
        component="Labormarket",
        category="Employment",
        subcategory="LowPaid"
    )
)

# -------------------------------------------------------------------------------------#
# --------------- Net Export ----------------------------------------------------------#
# -------------------------------------------------------------------------------------#

NOWDataset.add(
    GroupSeries(
        series_dict={
            # "de_ifo_bs_mfg_export_expect_3m_sa": ("desurv1142", None), # NOTE: This series is also in IfoCast. Keep this turned of to easily compare the two datasets.
            "de_ifo_bs_mfg_foreign_orders_sa": ("deifo_c0000000_xus_bdb", None)
        },
        source_data="mb",
        component="Netexport",
        category="Ifo_BS",
        subcategory="Exports_Expectations"
    )
)

NOWDataset.add(
    GroupSeries(
        series_dict={
            "de_new_orders_construction_sa": ("deprod1633", None),
            "de_new_orders_foreign_exmajor_idx": ("deprod2473", None),
            "de_new_orders_foreign_exveh_idx": ("deprod2825", None),
            "de_new_orders_ea_exveh_idx": ("deprod2834", None)
        },
        source_data="mb",
        component="Netexport",
        category="NewOrders",
        subcategory="Manufacturing"
    )
)

NOWDataset.add(
    GroupSeries(
        series_dict={
            "de_export_price_idx": ("depric4691", None),
            "de_import_price_idx": ("depric4690", None)
        },
        source_data="mb",
        component="Netexport",
        category="Prices",
        subcategory="TradePrices"
    )
)

NOWDataset.add( # NOTE: Error in the release period. Check if this can be fixed by manually adjusting the series release periods. Would be interesting to see how good this indicator is.
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

NOWDataset.add(
    GroupSeries(
        series_dict={
            "ea20_capacity_util_mfg": ("euprod0507", None),
            "us_capacity_util_sa": ("usprod1071", None),
            "cn_capacity_util_total": ("cnprod0910", None)
        },
        source_data="mb",
        component="Netexport",
        category="ProductionCapacity",
        subcategory="CapacityUtilization_Foreign"
    )
)

# NOWDataset.add( # NOTE: This series is also in IfoCast. Keep this turned of to easily compare the two datasets.
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

NOWDataset.add(
    GroupSeries(
        series_dict={
            "de_dgecfin_cc_confidence_balance_sa": ("cons2_de_tot_cof_bs_m", None),
            "de_dgecfin_cc_econ_sit_12mo_sa": ("cons2_de_tot_4_bs_m", None),
            "de_dgecfin_cc_fin_sit_12mo_sa": ("cons2_de_tot_2_bs_m", None),
            "de_dgecfin_cc_household_fin_statement_sa": ("cons2_de_tot_12_bs_m", None),
            "de_dgecfin_cc_major_purchases_now_sa": ("cons2_de_tot_8_bs_m", None),
            "de_dgecfin_cc_major_purchases_12mo_sa": ("cons2_de_tot_9_bs_m", None),
            "de_dgecfin_cc_price_dev_12mo": ("cons2_de_tot_6_b_m", None)
        },
        source_data="mb",
        component="Privconsumption",
        category="DGECFIN_CS",
        subcategory="DGECFIN_Confidence"
    )
)

NOWDataset.add(
    GroupSeries(
        series_dict={
            "de_dgecfin_cc_buy_car_12mo": ("cons2_de_tot_13_b_q", None),
            "de_dgecfin_cc_buy_home_12mo": ("cons2_de_tot_14_b_q", None),
            "de_dgecfin_cc_home_improve_12mo": ("cons2_de_tot_15_b_q", None)
        },
        source_data="mb",
        component="Privconsumption",
        category="DGECFIN_CS",
        subcategory="DGECFIN_Intentions"
    )
)

NOWDataset.add(
    GroupSeries(
        series_dict={
            "de_gfk_climate_indicator": ("desurv0029", None),
            "de_gfk_econ_expectations": ("desurv0026", None),
            "de_gfk_income_expectations": ("desurv0027", None),
            "de_gfk_willingness_buy": ("desurv0028", None)
        },
        source_data="mb",
        component="Privconsumption",
        category="GfK_CS",
    )
)

NOWDataset.add(
    GroupSeries(
        series_dict={
            "de_hde_total_index": ("desurv01062", None),
            "de_hde_income_expectations_index": ("desurv01063", None),
            "de_hde_willingness_buy_index": ("desurv01064", None), # NOTE: Non-stationary - check if it can be made stationary.
            "de_hde_price_expectations_index": ("desurv01066", None),
            "de_hde_econ_expectations_index": ("desurv01067", None),
            "de_hde_interest_expectations_index": ("desurv01068", None)
        },
        source_data="mb",
        component="Privconsumption",
        category="HDE_ConsumerBarometer",
    )
)

NOWDataset.add(
    GroupSeries(
        series_dict={ 
            # "de_dt_retail_turnover_sa": ("detrad1360", None), # NOTE: This series is also in IfoCast. Keep this turned of to easily compare the two datasets.
            "de_dt_services_turnover_sa": ("detrad3845", None),
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

NOWDataset.add(
    GroupSeries(
        series_dict={
            "de_zew_es_automobile_balance": ("desurv0068", None),
            "de_zew_es_banks_balance": ("desurv0066", None),
            "de_zew_es_chemicals_balance": ("desurv0069", None),
            "de_zew_es_construction_balance": ("desurv0074", None),
            "de_zew_es_current_balance": ("desurv0018", None),
            "de_zew_es_electronics_balance": ("desurv0071", None),
            # "de_zew_es_expect_balance": ("desurv0017", None), # NOTE: This series is also in IfoCast. Keep this turned of to easily compare the two datasets.
            "de_zew_es_insurance_balance": ("desurv0067", None),
            "de_zew_es_it_balance": ("desurv0078", None), # NOTE: Kept the series. Although it only start in 1999.
            "de_zew_es_mechanical_balance": ("desurv0072", None),
            "de_zew_es_retail_balance": ("desurv0073", None), 
            "de_zew_es_services_balance": ("desurv0076", None), # NOTE: Kept the series. Although it only start in 1999.
            "de_zew_es_steel_balance": ("desurv0070", None),
            "de_zew_es_telecom_balance": ("desurv0077", None),
            "de_zew_es_utilities_balance": ("desurv0075", None),
        },
        source_data="mb",
        component="FinancialMarkets",
        category="ZEW_ES",
        subcategory="ZEW_Balance_Indicators"
    )
)

NOWDataset.add( # NOTE: Add more yields
    GroupSeries(
        series_dict={
            "us_govt_benchmark_5y_yield": ("us05ygov", None),
            "de_govt_benchmark_5y_yield": ("de5ygov", None),
            "it_govt_benchmark_5y_yield": ("it5ygov", None),
            "de_govt_benchmark_yield10y": ("de10ygov_m", None)
        },
        source_data="mb",
        component="FinancialMarkets",
        category="GovtYields",
    )
)

NOWDataset.add(
    Series(
        name="ea_ecb_reuters_euribor3m_avg",
        description="Euro Area, ECB, Financial Market Provider: Reuters, Money Market, EURIBOR 3-Month, Historical Close, Average of Period",
        component="FinancialMarkets",
        category="EURIBOR",
        transformation="",
        source=Source(
            data="mb",
            variable="ecb_00858138"
        )
    )
)


# -------------------------------------------------------------------------------------#
# --------------- IfoCast -------------------------------------------------------------#
# -------------------------------------------------------------------------------------#

NOWDataset.add(
    GroupSeries(
        series_dict={
            "ifocast_ip_tot": ("deprod1404", None),
            "ifocast_to_energy": ("detrad3364", None),
            "ifocast_to_retail": ("detrad1360", None),
            "ifocast_to_hosp": ("detrad3877", None),
            "ifocast_to_wholesale": ("detrad8150", None),
            "ifocast_no_tot_manu": ("deprod2112", None),
            "ifocast_no_dom_manu": ("deprod2113", None),
            "ifocast_ifo_trade_indus": ("desurv0006", None),
            "ifocast_ifo_manu": ("desurv1142", None),
            "ifocast_ifo_exp_climate": ("desurv0344", None),
            "ifocast_ifo_manu_ordchange": ("deifo_f4010300_bvsa_bdu", None),
            "ifocast_ifo_wholesale_exp": ("deifo_g4600010_ges_bds", None),
            "ifocast_zew_fmr": ("desurv0017", None),
            "ifocast_lt_unf_vac": ("delama0016", None),
            "ifocast_imp_tot": ("detrad0689", None),
            "ifocast_exp_tot": ("detrad0692", None),
            "ifocast_trade_world": ("worldtrad0001", None),
            "ifocast_inflation": ("depric1962", None)
        },
        source_data="mb",
        component="IfoCast",
    )
)



# %%
